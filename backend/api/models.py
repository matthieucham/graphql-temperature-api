from django.db import models


class Temperature(models.Model):
    """Model for temperature readings."""

    # timestamp of the reading, set by the consumer at consume time.
    timestamp = models.DateTimeField()
    # read temperature value.
    value = models.DecimalField(max_digits=18, decimal_places=15)


class ReadConfig(models.Model):
    """Model for feed reading configuration."""

    config_key = models.CharField(primary_key=True, max_length=24)
    config_value = models.CharField(max_length=256)
