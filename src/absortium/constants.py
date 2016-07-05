import decimal

__author__ = 'andrew.shvv@gmail.com'

SELL = 0
BUY = 1
AVAILABLE_ORDER_TYPES = {
    'sell': SELL,
    'buy': BUY
}

EXCHANGE_INIT = 0
EXCHANGE_PENDING = 1
EXCHANGE_COMPLETED = 2

AVAILABLE_TASK_STATUS = {
    'init': EXCHANGE_INIT,
    'pending': EXCHANGE_PENDING,
    'completed': EXCHANGE_COMPLETED
}

SYSTEM_OWN = 0
SYSTEM_POLONIEX = 1

AVAILABLE_SYSTEMS = {
    'own': SYSTEM_OWN,
    'poloniex': SYSTEM_POLONIEX,
}

CELERY_RETRY_COUNTDOWN = 0.1
CELERY_MAX_RETRIES = 1000

BTC = 0
ETH = 1
AVAILABLE_CURRENCIES = {
    'btc': BTC,
    'eth': ETH
}

POLONIEX_OFFER_MODIFIED = "orderBookModify"
POLONIEX_OFFER_CREATED = "newTrade"
POLONIEX_OFFER_REMOVED = "orderBookRemove"

EPS = decimal.Decimal(1 / 10 ** 8)

ACCOUNT_POOL_LENGTH = 5

MAX_DIGITS = 17
DECIMAL_PLACES = 8

OFFER_MAX_DIGITS = MAX_DIGITS + (MAX_DIGITS - DECIMAL_PLACES)
ACCOUNT_MAX_DIGITS = OFFER_MAX_DIGITS

USERNAME_LENGTH = 30

MARKET_INFO_DELTA = 24
MARKET_INFO_COUNT_OF_EXCHANGES = 10

TOPIC_OFFERS = "offers_{from_currency}_{to_currency}"
TOPIC_HISTORY = "history_{from_currency}_{to_currency}"
TOPIC_MARKET_INFO = "marketinfo"

DEFAULT_AMOUNT = 0

WITHDRAW_AMOUNT_MIN_VALUE = decimal.Decimal(1 / 10 ** 3)
DEPOSIT_AMOUNT_MIN_VALUE = 0
PRICE_MIN_VALUE = decimal.Decimal(1 / 10 ** 8)
PRICE_MAX_VALUE = 5000
EXCHANGE_AMOUNT_MIN_VALUE = round(decimal.Decimal(0.001), 3)
WEI_IN_ETH = 10 ** 18

COINBASE_PAYMENT_NOTIFICATION = "wallet:addresses:new-payment"
