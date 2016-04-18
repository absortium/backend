__author__ = 'andrew.shvv@gmail.com'

from django.contrib.auth import get_user_model
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN, HTTP_405_METHOD_NOT_ALLOWED

from absortium.tests.base import AbsoritumUnitTest
from core.utils.logging import getLogger

logger = getLogger(__name__)


class DepositTest(AbsoritumUnitTest):
    def test_permissions(self, *args, **kwargs):
        account_pk, _ = self.create_account('btc')
        deposit_pk, _ = self.create_deposit(account_pk=account_pk)

        # Create hacker user
        User = get_user_model()
        hacker = User(username="hacker")
        hacker.save()

        # Authenticate hacker
        self.client.force_authenticate(hacker)

        # Try to get deposits from another account
        url = '/api/accounts/{account_pk}/deposits/'.format(account_pk=account_pk)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

        # Try to create deposit in another account
        # TODO: this operation should be granted only for notification service
        data = {
            'amount': '0.0111',
        }
        url = '/api/accounts/{account_pk}/deposits/'.format(account_pk=account_pk)
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

        # Try to get deposit info from another account
        url = '/api/accounts/{account_pk}/deposits/{deposit_pk}/'.format(account_pk=account_pk,
                                                                         deposit_pk=deposit_pk)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

        # Try to delete deposit from another account
        # TODO: this operation should be granted at all
        url = '/api/accounts/{account_pk}/deposits/{deposit_pk}/'.format(account_pk=account_pk,
                                                                         deposit_pk=deposit_pk)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, HTTP_405_METHOD_NOT_ALLOWED)

    def test_malformed(self, *args, **kwargs):
        trash_account_pk = "129381728763"
        trash_deposit_pk = "972368423423"

        # Try to get deposit info from uncreated account
        url = '/api/accounts/{account_pk}/deposits/{deposit_pk}/'.format(account_pk=trash_account_pk,
                                                                         deposit_pk=trash_deposit_pk)

        # Create an account and try to get uncreated deposit
        account_pk, _ = self.create_account('btc')
        url = '/api/accounts/{account_pk}/deposits/{deposit_pk}/'.format(account_pk=account_pk,
                                                                         deposit_pk=trash_deposit_pk)

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_malformed_amount_price(self):
        account_pk, _ = self.create_account('btc')
        malformed_amount = "*asa1&^*%^&$*%EOP"

        # Create deposit should assert if deposit response code is not 200
        with self.assertRaises(AssertionError):
            self.create_deposit(account_pk=account_pk, amount=malformed_amount)
