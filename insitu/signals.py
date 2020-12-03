from collections import defaultdict
from django.db.models.signals import post_save
import django.dispatch

data_provider_updated = django.dispatch.Signal()
requirement_updated = django.dispatch.Signal()


# delete index for soft deleted objects
product_deleted = django.dispatch.Signal()
requirement_deleted = django.dispatch.Signal()
data_deleted = django.dispatch.Signal()
data_provider_deleted = django.dispatch.Signal()


class DisableSignals(object):
    def __init__(self, disabled_signals=None):
        self.stashed_signals = defaultdict(list)
        self.disabled_signals = disabled_signals or [
            post_save,
        ]

    def __enter__(self):
        for signal in self.disabled_signals:
            self.disconnect(signal)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for signal in list(self.stashed_signals.keys()):
            self.reconnect(signal)

    def disconnect(self, signal):
        self.stashed_signals[signal] = signal.receivers
        signal.receivers = []

    def reconnect(self, signal):
        signal.receivers = self.stashed_signals.get(signal, [])
        del self.stashed_signals[signal]
