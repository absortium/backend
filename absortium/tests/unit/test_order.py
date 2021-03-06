from django.contrib.auth import get_user_model
from rest_framework.status import HTTP_404_NOT_FOUND

from absortium import constants
from absortium.tests.base import AbsoritumUnitTest
from core.utils.logging import getLogger

__author__ = "andrew.shvv@gmail.com"

logger = getLogger(__name__)


class BaseTest(AbsoritumUnitTest):
    def setUp(self):
        super().setUp()
        self.publishments_flush()

        self.primary_btc_account = self.get_account("btc")
        self.primary_eth_account = self.get_account("eth")

        self.make_deposit(self.primary_btc_account, amount="10.0")
        self.check_account_amount(self.primary_btc_account, amount="10.0")

        # Create some another user
        User = get_user_model()
        some_user = User(username="some_user")
        some_user.save()

        self.some_user = some_user

        # Authenticate some another user
        self.client.force_authenticate(self.some_user)

        self.some_eth_account = self.get_account("eth")
        self.some_btc_account = self.get_account("btc")

        self.make_deposit(self.some_eth_account, amount="20.0")
        self.check_account_amount(self.some_eth_account, amount="20.0")

        self.client.force_authenticate(self.user)


class CreateTest(BaseTest):
    def test_orders_count(self):
        """
            Check that we get only orders which belong to the user.
        """
        self.create_order(price="1", status="init")
        self.create_order(price="1", status="init")
        self.assertEqual(len(self.get_orders()), 2)

        self.client.force_authenticate(self.some_user)
        self.assertEqual(len(self.get_orders()), 0)

    def test_to_amount(self):
        """
            Check that we get only orders which belong to the user.
        """
        self.create_order(total="1", price="1", status="init")
        self.create_order(total="1", price="1", status="init")
        self.assertEqual(len(self.get_orders()), 2)

    def test_orders_count_with_different_currency(self):
        """
            Check that we get only orders which belong to the user.
        """
        self.make_deposit(self.primary_eth_account, amount="10.0")

        self.create_order(order_type=constants.ORDER_SELL, amount="1", price="1", status="init")
        self.assertEqual(len(self.get_orders(constants.ORDER_SELL)), 1)
        self.assertEqual(len(self.get_orders(constants.ORDER_BUY)), 0)

        self.create_order(order_type=constants.ORDER_BUY, price="0.5", status="init")
        self.assertEqual(len(self.get_orders(constants.ORDER_SELL)), 1)
        self.assertEqual(len(self.get_orders(constants.ORDER_BUY)), 1)

    def test_buy_order_creation(self):
        self.create_order(order_type=constants.ORDER_BUY, total="1.0", status=constants.ORDER_INIT)

        self.check_account_amount(self.primary_btc_account, amount="9.0")
        self.check_account_amount(self.primary_eth_account, amount="0.0")

    def test_sell_order_creation(self):
        self.client.force_authenticate(self.some_user)
        self.create_order(order_type=constants.ORDER_SELL, price="0.5", amount="2.0", status=constants.ORDER_INIT)

        self.check_account_amount(self.some_btc_account, amount="0.0")
        self.check_account_amount(self.some_eth_account, amount="18.0")

    def test_run_out_deposit(self):
        """
            Create orders without money
        """
        with self.assertRaises(AssertionError):
            self.create_order(price="2.0", amount="999")

        self.check_account_amount(self.primary_btc_account, amount="10.0")
        self.check_account_amount(self.primary_eth_account, amount="0.0")

    def test_simple_order(self):
        """
            Create orders which will be processed fully
        """

        self.create_order(order_type=constants.ORDER_BUY, price="0.5", amount="20", status=constants.ORDER_INIT)

        self.client.force_authenticate(self.some_user)
        self.create_order(order_type=constants.ORDER_SELL, price="0.5", amount="20")
        self.check_account_amount(self.some_btc_account, amount="10.0")
        self.check_account_amount(self.some_eth_account, amount="0.0")
        self.assertEqual(len(self.get_orders(constants.ORDER_SELL)), 1)

        self.client.force_authenticate(self.user)
        self.check_account_amount(self.primary_eth_account, amount="20.0")
        self.check_account_amount(self.primary_btc_account, amount="0.0")
        self.assertEqual(len(self.get_orders(constants.ORDER_BUY)), 1)

    def test_multiple_orders(self):
        """
            Create orders which will be processed fully
        """

        self.create_order(order_type=constants.ORDER_BUY, price="0.5", amount="8", status=constants.ORDER_INIT)
        self.create_order(order_type=constants.ORDER_BUY, price="0.5", amount="8", status=constants.ORDER_INIT)
        self.create_order(order_type=constants.ORDER_BUY, price="0.5", amount="4", status=constants.ORDER_INIT)

        self.client.force_authenticate(self.some_user)
        self.create_order(order_type=constants.ORDER_SELL, price="0.5", amount="20")
        self.check_account_amount(self.some_btc_account, amount="10.0")
        self.check_account_amount(self.some_eth_account, amount="0.0")
        self.assertEqual(len(self.get_orders(constants.ORDER_SELL)), 3)

        self.client.force_authenticate(self.user)
        self.check_account_amount(self.primary_eth_account, amount="20.0")
        self.check_account_amount(self.primary_btc_account, amount="0.0")
        self.assertEqual(len(self.get_orders(constants.ORDER_BUY)), 3)

    def test_order_pending(self):
        """
            Create orders which will not be fully processed
        """
        self.create_order(order_type=constants.ORDER_BUY, price="0.5", amount="16.0", status=constants.ORDER_INIT)

        self.client.force_authenticate(self.some_user)
        self.create_order(order_type=constants.ORDER_SELL, price="0.5", amount="20.0", status="pending")
        self.check_account_amount(self.some_eth_account, amount="0.0")
        self.check_account_amount(self.some_btc_account, amount="8.0")

        self.client.force_authenticate(self.user)
        self.check_account_amount(self.primary_btc_account, amount="2.0")
        self.check_account_amount(self.primary_eth_account, amount="16.0")

    def test_same_account(self):
        """
            Create opposite orders on the same account
        """
        self.make_deposit(self.primary_eth_account, amount="20.0")

        self.create_order(order_type=constants.ORDER_BUY, price="0.5", amount="20.0", status=constants.ORDER_INIT)
        self.check_account_amount(self.primary_btc_account, amount="0.0")

        self.create_order(order_type=constants.ORDER_SELL, price="0.5", amount="20.0", status=constants.ORDER_INIT)

        self.check_account_amount(self.primary_btc_account, amount="0.0")
        self.check_account_amount(self.primary_eth_account, amount="0.0")

    def test_with_two_orders_with_diff_price(self):
        """
            Create create two orders with different price and then one opposite with smaller price.
        """
        self.create_order(order_type=constants.ORDER_BUY, price="0.5", total="5.0", status=constants.ORDER_INIT)
        self.create_order(order_type=constants.ORDER_BUY, price="1.0", total="5.0", status=constants.ORDER_INIT)

        self.client.force_authenticate(self.some_user)
        self.create_order(order_type=constants.ORDER_SELL, price="0.1", amount="15.0", status=constants.ORDER_COMPLETED)
        self.check_account_amount(self.some_eth_account, amount="5.0")
        self.check_account_amount(self.some_btc_account, amount="10.0")

        self.client.force_authenticate(self.user)
        self.check_account_amount(self.primary_btc_account, amount="0.0")
        self.check_account_amount(self.primary_eth_account, amount="15.0")

    def test_sell_with_small_amount(self):
        self.client.force_authenticate(self.some_user)

        amount = constants.ORDER_MIN_TOTAL_AMOUNT - constants.ORDER_MIN_TOTAL_AMOUNT / 10

        with self.assertRaises(AssertionError):
            self.create_order(order_type=constants.ORDER_SELL, total=amount)
        self.check_account_amount(self.some_eth_account, amount="20.0")

    def test_buy_with_small_amount(self):
        amount = constants.ORDER_MIN_TOTAL_AMOUNT - constants.ORDER_MIN_TOTAL_AMOUNT / 10

        with self.assertRaises(AssertionError):
            self.create_order(price="0.1", total=amount)
        self.check_account_amount(self.primary_btc_account, amount="10.0")


class MalformedTest(BaseTest):
    def test_order_readonly_status(self):
        # check that we can't set the order status
        extra_data = {
            'status': constants.ORDER_PENDING
        }

        self.create_order(price="1.0", amount="10.0", status=constants.ORDER_INIT, extra_data=extra_data)

    def test_malformed(self, *args, **kwargs):
        trash_order_pk = "972368423423"

        # Create an account and try to get uncreated order
        account = self.get_account("btc")
        url = "/api/orders/{order_pk}/".format(order_pk=trash_order_pk)

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    # TODO: Create test that checks incorrect primary, secondary currency, price, amount etc
    def test_malformed_amount(self):
        malformed_amount = "(*YGV*T^C%D"
        with self.assertRaises(AssertionError):
            self.create_order(amount=malformed_amount, status='init')

    def test_malformed_pair(self):
        malformed_pair = "(*YGV*T^C%D"
        with self.assertRaises(AssertionError):
            self.create_order(pair=malformed_pair, status='init')

    def test_malformed_type(self):
        malformed_type = "(*YGV*T^C%D"
        with self.assertRaises(AssertionError):
            self.create_order(order_type=malformed_type, status="init")

    def test_malformed_price(self):
        malformed_price = "(*YGV*T^C%D"
        with self.assertRaises(AssertionError):
            self.create_order(price=malformed_price, status=constants.ORDER_INIT)


class ApproveTest(BaseTest):
    def test_approve(self):
        order = self.create_order(order_type=constants.ORDER_BUY,
                                  price="0.5",
                                  amount="20",
                                  need_approve=True,
                                  status=constants.ORDER_INIT)

        self.client.force_authenticate(self.some_user)
        self.create_order(order_type=constants.ORDER_SELL,
                          price="0.5",
                          amount="20",
                          status=constants.ORDER_APPROVING)

        # Unless order is not approved it should not be processed
        self.check_account_amount(self.some_btc_account, amount="0.0")
        self.check_account_amount(self.some_eth_account, amount="0.0")

        self.client.force_authenticate(self.user)
        self.check_account_amount(self.primary_eth_account, amount="0.0")
        self.check_account_amount(self.primary_btc_account, amount="0.0")

        # After approve order should be processed
        self.approve_order(pk=order['pk'])

        self.client.force_authenticate(self.some_user)
        self.check_account_amount(self.some_btc_account, amount="10.0")
        self.check_account_amount(self.some_eth_account, amount="0.0")

        self.client.force_authenticate(self.user)
        self.check_account_amount(self.primary_eth_account, amount="20.0")
        self.check_account_amount(self.primary_btc_account, amount="0.0")

    def test_user_cancel_during_approve(self):
        order = self.create_order(order_type=constants.ORDER_BUY,
                                  price="0.5",
                                  amount="20",
                                  need_approve=True,
                                  status=constants.ORDER_INIT)

        self.client.force_authenticate(self.some_user)
        self.create_order(order_type=constants.ORDER_SELL,
                          price="0.5",
                          amount="20",
                          status=constants.ORDER_APPROVING)

        # Unless order is not approved it should not be processed
        self.check_account_amount(self.some_eth_account, amount="0.0")
        self.check_account_amount(self.some_btc_account, amount="0.0")

        # Cancel order
        self.client.force_authenticate(self.user)
        self.check_account_amount(self.primary_eth_account, amount="0.0")
        self.check_account_amount(self.primary_btc_account, amount="0.0")
        self.cancel_order(pk=order['pk'])
        self.check_account_amount(self.primary_eth_account, amount="0.0")
        self.check_account_amount(self.primary_btc_account, amount="10.0")
        self.check_order(order_type=constants.ORDER_BUY,
                         price="0.5",
                         amount="20",
                         status=constants.ORDER_CANCELED)

        self.client.force_authenticate(self.some_user)
        self.check_account_amount(self.some_eth_account, amount="0.0")
        self.check_account_amount(self.some_btc_account, amount="0.0")
        self.check_order(order_type=constants.ORDER_SELL,
                         price="0.5",
                         amount="20",
                         status=constants.ORDER_PENDING)

    def test_double_side_approve(self):
        first_order = self.create_order(order_type=constants.ORDER_BUY,
                                        price="0.5",
                                        amount="20",
                                        need_approve=True,
                                        status=constants.ORDER_INIT)

        self.client.force_authenticate(self.some_user)
        second_order = self.create_order(order_type=constants.ORDER_SELL,
                                         price="0.5",
                                         amount="20",
                                         need_approve=True,
                                         status=constants.ORDER_APPROVING)

        self.check_account_amount(self.some_eth_account, amount="0.0")
        self.check_account_amount(self.some_btc_account, amount="0.0")

        self.client.force_authenticate(self.user)
        self.check_account_amount(self.primary_eth_account, amount="0.0")
        self.check_account_amount(self.primary_btc_account, amount="0.0")

        self.approve_order(pk=first_order['pk'])

        self.check_account_amount(self.primary_eth_account, amount="0.0")
        self.check_account_amount(self.primary_btc_account, amount="0.0")

        self.client.force_authenticate(self.some_user)
        self.check_account_amount(self.some_eth_account, amount="0.0")
        self.check_account_amount(self.some_btc_account, amount="0.0")

        self.approve_order(pk=second_order['pk'])
        self.check_account_amount(self.some_eth_account, amount="0.0")
        self.check_account_amount(self.some_btc_account, amount="10.0")

        self.client.force_authenticate(self.user)
        self.check_account_amount(self.primary_eth_account, amount="20.0")
        self.check_account_amount(self.primary_btc_account, amount="0.0")

    def test_another_user_cancel_during_approve(self):
        self.create_order(order_type=constants.ORDER_BUY,
                          price="0.5",
                          amount="20",
                          need_approve=True,
                          status=constants.ORDER_INIT)

        self.client.force_authenticate(self.some_user)
        order = self.create_order(order_type=constants.ORDER_SELL,
                                  price="0.5",
                                  amount="20",
                                  status=constants.ORDER_APPROVING)

        # Unless order is not approved it should not be processed
        self.check_account_amount(self.some_eth_account, amount="0.0")
        self.check_account_amount(self.some_btc_account, amount="0.0")

        self.cancel_order(pk=order['pk'])
        self.check_account_amount(self.some_eth_account, amount="20.0")
        self.check_account_amount(self.some_btc_account, amount="0.0")

        self.check_order(order_type=constants.ORDER_SELL,
                         price="0.5",
                         amount="20",
                         status=constants.ORDER_CANCELED)

        self.client.force_authenticate(self.user)
        self.check_account_amount(self.primary_eth_account, amount="0.0")
        self.check_account_amount(self.primary_btc_account, amount="0.0")
        self.check_order(order_type=constants.ORDER_BUY,
                         price="0.5",
                         amount="20",
                         status=constants.ORDER_PENDING)


class CancelTest(BaseTest):
    def test_cancel(self):
        order = self.create_order(order_type=constants.ORDER_BUY, total="1.0", status=constants.ORDER_INIT)
        self.cancel_order(pk=order['pk'])

        self.check_account_amount(self.primary_btc_account, amount="10.0")
        self.check_account_amount(self.primary_eth_account, amount="0.0")

        self.assertEqual(len(self.get_orders()), 1)


class LockTest(BaseTest):
    def test_lock(self):
        order = self.create_order(order_type=constants.ORDER_BUY,
                                  amount="1.0",
                                  price="1.0",
                                  status=constants.ORDER_INIT)

        self.lock_order(pk=order['pk'])
        self.check_order(pk=order['pk'], status=constants.ORDER_LOCKED)

        self.client.force_authenticate(self.some_user)
        opposite_order = self.create_order(order_type=constants.ORDER_SELL,
                                           amount="1.0",
                                           price="1.0",
                                           status=constants.ORDER_INIT)

        self.client.force_authenticate(self.user)
        self.unlock_order(pk=order['pk'])
        self.check_order(pk=order['pk'], status=constants.ORDER_COMPLETED)

        self.client.force_authenticate(self.some_user)
        self.check_order(pk=opposite_order['pk'], status=constants.ORDER_COMPLETED)

    def test_lock_while_approving(self):
        order = self.create_order(order_type=constants.ORDER_BUY,
                                  amount="1.0",
                                  price="1.0",
                                  status=constants.ORDER_INIT)

        self.client.force_authenticate(self.some_user)
        opposite_order = self.create_order(order_type=constants.ORDER_SELL,
                                           amount="1.0",
                                           price="1.0",
                                           need_approve=True,
                                           status=constants.ORDER_APPROVING)

        self.client.force_authenticate(self.user)

        with self.assertRaises(AssertionError):
            self.lock_order(pk=order['pk'])


class PriorityTest(BaseTest):
    def test_first_created_order_is_prior(self):
        order = self.create_order(order_type=constants.ORDER_BUY,
                                  amount="1.0",
                                  price="1.0",
                                  status=constants.ORDER_INIT)

        self.create_order(order_type=constants.ORDER_BUY,
                          amount="1.0",
                          price="1.0",
                          status=constants.ORDER_INIT)

        self.client.force_authenticate(self.some_user)
        self.create_order(order_type=constants.ORDER_SELL,
                          amount="1.0",
                          price="1.0",
                          status=constants.ORDER_COMPLETED)

        self.client.force_authenticate(self.user)
        self.check_order(pk=order['pk'], status=constants.ORDER_COMPLETED)

    def test_price_priority(self):
        self.create_order(order_type=constants.ORDER_BUY,
                          amount="1.0",
                          price="1.0",
                          status=constants.ORDER_INIT)

        order = self.create_order(order_type=constants.ORDER_BUY,
                                  amount="1.0",
                                  price="1.1",
                                  status=constants.ORDER_INIT)

        self.client.force_authenticate(self.some_user)
        self.create_order(order_type=constants.ORDER_SELL,
                          amount="1.0",
                          price="1.0",
                          status=constants.ORDER_COMPLETED)

        self.client.force_authenticate(self.user)
        self.check_order(pk=order['pk'], status=constants.ORDER_COMPLETED)


class UpdateTest(BaseTest):
    def test_simple(self):
        order = self.create_order(order_type=constants.ORDER_BUY,
                                  amount="1.0",
                                  price="1.0",
                                  status=constants.ORDER_INIT)

        self.update_order(pk=order['pk'], price="2.0", amount="1.0")
        self.check_order(pk=order['pk'], price="2.0", amount="1.0", total="2.0")

    def test_not_enough_money(self):
        order = self.create_order(order_type=constants.ORDER_BUY,
                                  amount="1.0",
                                  price="1.0",
                                  status=constants.ORDER_INIT)

        with self.assertRaises(AssertionError):
            self.update_order(pk=order['pk'], amount="999.0")

    def test_not_init_and_pending_status(self):
        self.create_order(order_type=constants.ORDER_BUY,
                          price="1.0",
                          amount="1.0",
                          status=constants.ORDER_INIT)

        self.client.force_authenticate(self.some_user)
        order = self.create_order(order_type=constants.ORDER_SELL, price="1.0", amount="1.0")

        with self.assertRaises(AssertionError):
            self.update_order(pk=order['pk'], amount="2.0")


class NotificationTest(BaseTest):
    def test_notification(self):
        self.create_order(order_type=constants.ORDER_BUY, total="5.0", price="0.5", status=constants.ORDER_INIT)
        self.create_order(order_type=constants.ORDER_BUY, total="5.0", price="0.5", status=constants.ORDER_INIT)

        self.client.force_authenticate(self.some_user)
        self.create_order(order_type=constants.ORDER_SELL, price="0.5", amount="20.0")

        self.check_account_amount(self.some_btc_account, amount="10.0")
        self.check_account_amount(self.some_eth_account, amount="0.0")

        self.client.force_authenticate(self.user)
        self.check_account_amount(self.primary_btc_account, amount="0.0")
        self.check_account_amount(self.primary_eth_account, amount="20.0")

        self.assertEqual(len(self.get_publishments("history_btc_eth_sell")), 2)
        self.assertEqual(len(self.get_publishments("history_btc_eth_buy")), 2)
