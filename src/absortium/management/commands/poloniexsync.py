from django.conf import settings
from django.core.management.base import BaseCommand

from absortium.poloniexsync import App

__author__ = 'andrew.shvv@gmail.com'


class Command(BaseCommand):
    help = 'Sync Poloniex orders and create Poloniex exchanges'

    def handle(self, *args, **options):
        app = App(api_key=settings.POLONIEX_API_KEY, api_sec=settings.POLONIEX_API_SECRET)
        app.run()
