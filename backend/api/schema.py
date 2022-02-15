"""GraphQL schema."""
from typing import Any
import graphene
from graphene_django import DjangoObjectType
from django.db.models import Min, Max
from datetime import datetime
from api.models import TemperatureModel


class TemperatureType(DjangoObjectType):
    class Meta:
        model = TemperatureModel
        fields = (
            "timestamp",
            "value",
        )


class TemperatureStatisticsNode(graphene.ObjectType):
    min = graphene.Decimal()
    max = graphene.Decimal()


class Query(graphene.ObjectType):
    current_temperature = graphene.Field(TemperatureType)
    temperature_statistics = graphene.Field(
        TemperatureStatisticsNode,
        after=graphene.DateTime(required=False),
        before=graphene.DateTime(required=False),
    )

    def resolve_current_temperature(root, info: Any) -> TemperatureModel:
        """Return the last registered temperature in db."""
        return TemperatureModel.objects.order_by("-timestamp").first()

    def resolve_temperature_statistics(
        root, info: Any, after: datetime = None, before: datetime = None
    ) -> TemperatureStatisticsNode:
        query = TemperatureModel.objects
        if after:
            query = query.filter(timestamp__gte=after)
        if before:
            query = query.filter(timestamp__lte=before)
        result = query.aggregate(Min("value"), Max("value"))
        return TemperatureStatisticsNode(
            min=result.get("value__min"), max=result.get("value__max")
        )


schema = graphene.Schema(query=Query)
