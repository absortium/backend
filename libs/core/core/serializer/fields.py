import six
from rest_framework import serializers

__author__ = 'andrew.shvv@gmail.com'


class MyDecimalField(serializers.DecimalField):
    def validate_precision(self, value):
        try:
            return super().validate_precision(value)
        except serializers.ValidationError:
            return round(value, self.decimal_places)


class MySerializerMethodField(serializers.SerializerMethodField):
    def __init__(self, read_only=True, method_name=None, **kwargs):
        self.method_name = method_name
        kwargs['source'] = '*'
        kwargs['read_only'] = read_only
        super(serializers.SerializerMethodField, self).__init__(**kwargs)


class MyChoiceField(serializers.Field):
    """
        This class used for translation incoming strings values to
        integer representation by the given mapping dict.
    """

    def __init__(self, choices, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.to_internal = choices
        self.to_repr = {value: key for key, value in choices.items()}

    def to_internal_value(self, data):
        if not isinstance(data, six.text_type):
            msg = 'Incorrect type. Expected a string, but got %s'
            raise serializers.ValidationError(msg % type(data).__name__)

        data = data.lower()
        if data not in self.to_internal.keys():
            raise serializers.ValidationError("Malformed data '{}'".format(data))

        return self.to_internal[data]

    def to_representation(self, value):
        if not isinstance(value, six.integer_types):
            msg = 'Incorrect type. Expected a int, but got %s'
            raise serializers.ValidationError(msg % type(value).__name__)

        return self.to_repr[value]