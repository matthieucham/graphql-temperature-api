"""GraphQL schema."""
from typing import Any, Optional
import graphene
from graphene_django import DjangoObjectType
from django.db.models import Min, Max
from datetime import datetime
from api.models import Temperature, ReadConfig
from django.core.exceptions import ValidationError


class TemperatureType(DjangoObjectType):
    class Meta:
        model = Temperature
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

    def resolve_current_temperature(root, info: Any) -> Optional[Temperature]:
        """Return the last registered temperature in db."""
        return Temperature.objects.order_by("-timestamp").first()

    def resolve_temperature_statistics(
        root, info: Any, after: datetime = None, before: datetime = None
    ) -> TemperatureStatisticsNode:
        query = Temperature.objects.all()
        if after:
            query = query.filter(timestamp__gte=after)
        if before:
            query = query.filter(timestamp__lte=before)
        result = query.aggregate(Min("value"), Max("value"))
        return TemperatureStatisticsNode(
            min=result.get("value__min"), max=result.get("value__max")
        )


class ToggleFeedInput(graphene.InputObjectType):
    """Input for ToggleFeed mutation."""

    # An enum would be better suited here but I have to stick to the specs.
    status = graphene.String(required=True)


class ToggleFeed(graphene.Mutation):
    """Mutation to toggle the feed reading (on/off)."""

    class Arguments:
        input = ToggleFeedInput(required=True)

    status = graphene.String()

    def mutate(root, info: Any, input: ToggleFeedInput) -> "ToggleFeed":
        cleaninput = input.get("status", "").lower()
        if cleaninput not in ("on", "off"):
            raise ValidationError("status must be 'on' or 'off'.")
        val, _ = ReadConfig.objects.update_or_create(
            config_key="status", defaults={"config_value": cleaninput}
        )
        return ToggleFeed(status=val.config_value)


class Mutation(graphene.ObjectType):
    toggle_feed = ToggleFeed.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
