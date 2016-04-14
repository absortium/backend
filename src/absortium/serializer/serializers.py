__author__ = 'andrew.shvv@gmail.com'

from django.contrib.auth.models import User, Group
from rest_framework import serializers

from absortium import constants
from absortium.model.models import Account, Exchange, Offer, Deposit, Withdrawal
from absortium.serializer.fields import MyChoiceField


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `exclude_fields` argument that
    controls which fields should be excluded from serialization.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        exclude_fields = kwargs.pop('exclude_fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if exclude_fields:
            # Drop any fields that are not specified in the `fields` argument.
            disallowed = set(exclude_fields)

            for field_name in disallowed:
                self.fields.pop(field_name)


class OfferSerializer(DynamicFieldsModelSerializer):
    primary_currency = MyChoiceField(choices=constants.AVAILABLE_CURRENCIES)
    secondary_currency = MyChoiceField(choices=constants.AVAILABLE_CURRENCIES)

    amount = serializers.DecimalField(max_digits=constants.OFFER_MAX_DIGITS,
                                      decimal_places=constants.DECIMAL_PLACES,
                                      min_value=constants.AMOUNT_MIN_VALUE)
    price = serializers.DecimalField(max_digits=constants.MAX_DIGITS,
                                     decimal_places=constants.DECIMAL_PLACES,
                                     min_value=constants.PRICE_MIN_VALUE)

    class Meta:
        model = Offer
        fields = ('primary_currency', 'secondary_currency', 'amount', 'price')
        read_only_fields = ('amount', 'price')


class AccountSerializer(serializers.ModelSerializer):
    currency = MyChoiceField(choices=constants.AVAILABLE_CURRENCIES)

    class Meta:
        model = Account
        fields = ('pk', 'address', 'currency', 'amount')
        read_only_fields = ('address', 'amount')


class ExchangeSerializer(serializers.ModelSerializer):
    currency = MyChoiceField(choices=constants.AVAILABLE_CURRENCIES)

    amount = serializers.DecimalField(max_digits=constants.MAX_DIGITS,
                                      decimal_places=constants.DECIMAL_PLACES,
                                      min_value=constants.AMOUNT_MIN_VALUE)
    price = serializers.DecimalField(max_digits=constants.MAX_DIGITS,
                                     decimal_places=constants.DECIMAL_PLACES,
                                     min_value=constants.PRICE_MIN_VALUE)

    account = serializers.ReadOnlyField(source='account.username')

    class Meta:
        model = Exchange
        fields = ('pk', 'currency', 'amount', 'price', 'account', 'created')


class DepositSerializer(serializers.ModelSerializer):
    currency = MyChoiceField(choices=constants.AVAILABLE_CURRENCIES, read_only=True)
    address = serializers.ReadOnlyField(source='account.address')

    amount = serializers.DecimalField(max_digits=constants.MAX_DIGITS,
                                      decimal_places=constants.DECIMAL_PLACES,
                                      min_value=constants.AMOUNT_MIN_VALUE)



    class Meta:
        model = Deposit
        fields = ('pk', 'currency', 'address',  'amount', 'created')


class WithdrawSerializer(serializers.ModelSerializer):
    currency = MyChoiceField(choices=constants.AVAILABLE_CURRENCIES, read_only=True)

    address = serializers.CharField()
    amount = serializers.DecimalField(max_digits=constants.MAX_DIGITS,
                                      decimal_places=constants.DECIMAL_PLACES,
                                      min_value=constants.AMOUNT_MIN_VALUE)

    class Meta:
        model = Withdrawal
        fields = ('pk', 'currency', 'address', 'amount', 'created')