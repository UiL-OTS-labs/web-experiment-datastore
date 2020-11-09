from django.apps import AppConfig


class ExperimentsConfig(AppConfig):
    name = 'experiments'

    def ready(self):
        # Make sure our signals are connected on startup. The NOQA turns off
        # the annoying 'unused import' warning.
        import experiments.signals # NOQA
