import decimal
from datetime import timedelta

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from absortium.utils import calculate_total_or_amount

__author__ = 'andrew.shvv@gmail.com'

from celery import shared_task
from django.db import transaction
from django.db.utils import OperationalError

from absortium import constants
from absortium.wallet.pool import AccountPool
from absortium.celery.base import get_base_class
from absortium.crossbarhttp import publishment
from absortium.exceptions import AlreadyExistError, LockFailureError, UnlockFailureError, UpdateFailureError
from absortium.model.locks import lockorder
from absortium.model.models import Account, Order, MarketInfo
from absortium.serializers import \
    OrderSerializer, \
    WithdrawSerializer, \
    DepositSerializer, \
    AccountSerializer
from core.utils.logging import getPrettyLogger

logger = getPrettyLogger(__name__)


@shared_task(bind=True, max_retries=constants.CELERY_MAX_RETRIES, base=get_base_class())
def do_deposit(self, *args, **kwargs):
    def do():
        data = kwargs['data']
        user_pk = kwargs['user_pk']

        serializer = DepositSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        deposit = serializer.save(owner_id=user_pk)
        deposit.process_account()

        return serializer.data

    try:
        with transaction.atomic():
            return do()
    except OperationalError:
        raise self.retry(countdown=constants.CELERY_RETRY_COUNTDOWN)


@shared_task(bind=True, max_retries=constants.CELERY_MAX_RETRIES, base=get_base_class())
def do_withdrawal(self, *args, **kwargs):
    def do():
        data = kwargs['data']
        user_pk = kwargs['user_pk']

        serializer = WithdrawSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        withdrawal = serializer.save(owner_id=user_pk)
        withdrawal.process_account()

        return serializer.data

    try:
        with transaction.atomic():
            return do()
    except OperationalError:
        raise self.retry(countdown=constants.CELERY_RETRY_COUNTDOWN)


@shared_task(bind=True, max_retries=constants.CELERY_MAX_RETRIES, base=get_base_class())
def create_order(self, *args, **kwargs):
    data = kwargs['data']
    user_pk = kwargs['user_pk']

    serializer = OrderSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    order = serializer.object(owner_id=user_pk)

    if order.total < constants.ORDER_MIN_TOTAL_AMOUNT:
        raise ValidationError("Total amount lower than {}".format(constants.ORDER_MIN_TOTAL_AMOUNT))

    try:
        with publishment.atomic():
            with transaction.atomic():
                with lockorder(order=order):
                    order.freeze_money()
                    return [OrderSerializer(e).data for e in order.process()]

    except OperationalError:
        raise self.retry(countdown=constants.CELERY_RETRY_COUNTDOWN)


@shared_task(bind=True, max_retries=constants.CELERY_MAX_RETRIES, base=get_base_class())
def cancel_order(self, *args, **kwargs):
    def do():
        with lockorder(pk=kwargs['order_pk']) as order:

            if order.status not in [constants.ORDER_CANCELED, constants.ORDER_COMPLETED]:
                if order.status in [constants.ORDER_APPROVING, constants.ORDER_APPROVED]:
                    with lockorder(pk=order.link.pk) as opposite:
                        opposite.status = constants.ORDER_PENDING

                order.unfreeze_money()
                order.status = constants.ORDER_CANCELED

                return OrderSerializer(order).data
            else:
                raise ValidationError("Order already canceled")

    try:
        with publishment.atomic():
            with transaction.atomic():
                return do()
    except OperationalError:
        raise self.retry(countdown=constants.CELERY_RETRY_COUNTDOWN)


@shared_task(bind=True, max_retries=constants.CELERY_MAX_RETRIES, base=get_base_class())
def lock_order(self, *args, **kwargs):
    def do():
        order = Order.lock(pk=kwargs['order_pk'])

        if order.status in [constants.ORDER_INIT, constants.ORDER_PENDING]:
            order.status = constants.ORDER_LOCKED
            order.save()

            return OrderSerializer(order).data
        else:
            raise LockFailureError("Can't lock order in status {}".format(order.status))

    try:
        with publishment.atomic():
            with transaction.atomic():
                return do()
    except OperationalError:
        raise self.retry(countdown=constants.CELERY_RETRY_COUNTDOWN)


@shared_task(bind=True, max_retries=constants.CELERY_MAX_RETRIES, base=get_base_class())
def unlock_order(self, *args, **kwargs):
    def do():
        with lockorder(pk=kwargs['order_pk']) as order:
            if order.status == constants.ORDER_LOCKED:
                order.status = constants.ORDER_INIT

                return [OrderSerializer(e).data for e in order.process()]

            else:
                raise UnlockFailureError("Can't unlock not locked order")

    try:
        with publishment.atomic():
            with transaction.atomic():
                return do()
    except OperationalError:
        raise self.retry(countdown=constants.CELERY_RETRY_COUNTDOWN)


@shared_task(bind=True, max_retries=constants.CELERY_MAX_RETRIES, base=get_base_class())
def approve_order(self, *args, **kwargs):
    def do():
        with lockorder(pk=kwargs['order_pk']) as order:
            if order.need_approve and order.status != constants.ORDER_APPROVED:
                order.status = constants.ORDER_APPROVED

                with lockorder(pk=order.link.pk) as opposite:

                    if opposite.need_approve:
                        if opposite.status == constants.ORDER_APPROVED:
                            order.merge(opposite)
                    else:
                        order.merge(opposite)

        return OrderSerializer(order).data

    try:
        with transaction.atomic():
            return do()
    except OperationalError:
        raise self.retry(countdown=constants.CELERY_RETRY_COUNTDOWN)


@shared_task(bind=True, max_retries=constants.CELERY_MAX_RETRIES, base=get_base_class())
def update_order(self, *args, **kwargs):
    def do():
        data = kwargs['data']
        with lockorder(pk=kwargs['order_pk']) as order:
            if order.status in [constants.ORDER_INIT, constants.ORDER_PENDING, constants.ORDER_LOCKED]:

                order.unfreeze_money()

                if data.get('price') is None:
                    data['price'] = str(order.price)

                data = calculate_total_or_amount(data)
                order.price = decimal.Decimal(data.get('price'))
                order.amount = decimal.Decimal(data.get('amount'))
                order.total = decimal.Decimal(data.get('total'))
                order.freeze_money()
            else:
                raise UpdateFailureError("Can't update orders in status '{}'".format(order.status))

        return OrderSerializer(order).data

    try:
        with publishment.atomic():
            with transaction.atomic():
                return do()

    except OperationalError:
        raise self.retry(countdown=constants.CELERY_RETRY_COUNTDOWN)


@shared_task(bind=True, max_retries=constants.CELERY_MAX_RETRIES, base=get_base_class())
def create_account(self, *args, **kwargs):
    data = kwargs['data']
    user_pk = kwargs['user_pk']

    with publishment.atomic():
        serializer = AccountSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        currency = serializer.validated_data["currency"]

        try:
            obj = Account.objects.filter(owner_id=user_pk, currency=currency).all()[0]
            data = AccountSerializer(obj).data
            raise AlreadyExistError(data)

        except IndexError:
            with transaction.atomic():
                account = AccountPool(currency).assign_account(user_pk=user_pk)
                return AccountSerializer(account).data


@shared_task(bind=True, base=get_base_class())
def calculate_market_info(self, *args, **kwargs):
    with publishment.atomic():
        with transaction.atomic():

            for pair in constants.AVAILABLE_CURRENCY_PAIRS:
                info = MarketInfo()
                info.pair = pair

                # 1. Get orders for the last 24h.
                day_ago = timezone.now() - timedelta(hours=constants.MARKET_INFO_DELTA)
                orders_24h = Order.objects.filter(status=constants.ORDER_COMPLETED,
                                                  pair=pair,
                                                  created__gte=day_ago).all()

                rate_24h_max = 0
                rate_24h_min = 0
                volume_24h = 0
                if orders_24h:
                    rates = [order.price for order in orders_24h]

                    # 2. Get max rate.
                    rate_24h_max = max(rates)

                    # 3. Get min rate.
                    rate_24h_min = min(rates)

                    # 4. Calculate the market volume.
                    volume_24h = sum((order.total for order in orders_24h))

                info.rate_24h_max = rate_24h_max
                info.rate_24h_min = rate_24h_min
                info.volume_24h = volume_24h

                # 5. Get the last completed orders
                last_orders = Order.objects.filter(status=constants.ORDER_COMPLETED,
                                                   pair=pair).all()[:constants.MARKET_INFO_COUNT_OF_EXCHANGES]

                average_price = 0
                if last_orders:
                    # 6. Calculate average price
                    average_price = sum([order.price for order in last_orders]) / len(last_orders)

                info.rate = average_price
                info.save()


@shared_task(bind=True, base=get_base_class())
def pregenerate_accounts(self, *args, **kwargs):
    with transaction.atomic():
        currencies = constants.AVAILABLE_CURRENCIES

        for currency in currencies:
            pool = AccountPool(currency)
            count = constants.ACCOUNT_POOL_LENGTH - len(pool)

            while count > 0:
                account = pool.create_account()
                account.save()
                count -= 1
