from django.contrib import admin
from api.models import TemperatureModel


@admin.register(TemperatureModel)
class TemperatureAdmin(admin.ModelAdmin):
    """Admin interface for debug purposes."""

    list_display = (
        "timestamp",
        "value",
    )
