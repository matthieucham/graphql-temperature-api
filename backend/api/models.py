from django.db import models


class TemperatureModel(models.Model):
    """Model for temperature readings."""

    # timestamp of the reading, set by the consumer at consume time.
    timestamp = models.DateTimeField()
    # read temperature value.
    value = models.DecimalField(max_digits=18, decimal_places=15)
