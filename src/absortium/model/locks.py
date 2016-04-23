__author__ = 'andrew.shvv@gmail.com'

import decimal

from absortium import constants
from absortium.model.models import Exchange, Account
from core.utils.logging import getLogger

logger = getLogger(__name__)


class lockexchange:
    def __init__(self, exchange=None):
        self.exchange = exchange

    def __enter__(self):
        if not self.exchange.from_account and not self.exchange.to_account:
            """
                Such strange select was done in order to prevent deadlocks.

                Thread #1 (Exchange #1)             Thread #2 (Exchange #2) - opposite exchange
                Lock ETC account (from_account)
                                                    Lock BTC account (from_account)

                Lock BTC account (to_account) <---'lock' because BTC account was already locked

                                                    Lock ETC account (to_account) <--- dead lock

            """
            accounts = Account.objects.select_for_update().filter(owner__pk=self.exchange.owner_id,
                                                                  currency__in=[self.exchange.from_currency,
                                                                                self.exchange.to_currency])
            for account in accounts:
                if account.currency == self.exchange.from_currency:
                    self.exchange.from_account = account
                if account.currency == self.exchange.to_currency:
                    self.exchange.to_account = account

        return self.exchange

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_val:
            self.exchange.from_account.update(amount=self.exchange.from_account.amount)
            self.exchange.to_account.update(amount=self.exchange.to_account.amount)
            self.exchange.save()


class opposites:
    def __init__(self, exchange):
        self.exchange = exchange
        self.converted_price = decimal.Decimal("1.0") / self.exchange.price
        self.opposites = []

    def __iter__(self):
        return self

    def get_opposite(self):
        opposite = self.opposites.pop()

        if self.exchange.owner_id == opposite.owner_id:
            """
                If we process the same users that means that exchanges are opposite
                and we should not block the same accounts twice.
            """
            opposite.from_account = self.exchange.to_account
            opposite.to_account = self.exchange.from_account
        return opposite

    def __next__(self):
        try:
            """
                Get first non-blocked exchange which suit out conditions (price, status, currency)
            """
            opposite = Exchange.objects.raw(' SELECT *'
                                            ' FROM absortium_exchange'
                                            ' WHERE status = %s AND pg_try_advisory_xact_lock(id) AND price <= %s AND from_currency = %s'
                                            ' FOR UPDATE'
                                            ' LIMIT 1', [constants.EXCHANGE_PENDING,
                                                         self.converted_price,
                                                         self.exchange.to_currency])[0]

        except IndexError:
            raise StopIteration()

        if self.exchange.owner_id == opposite.owner_id:
            """
                If we process the same users that means that exchanges are opposite
                and we should not block the same accounts twice.
            """
            opposite.from_account = self.exchange.to_account
            opposite.to_account = self.exchange.from_account

        return opposite
