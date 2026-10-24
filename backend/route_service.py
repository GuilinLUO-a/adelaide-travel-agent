from models import ItineraryResponse, Route
from providers.route_base import RouteProvider, RouteProviderError


def enrich_itinerary_routes(
    itinerary: ItineraryResponse,
    provider: RouteProvider,
) -> ItineraryResponse:
    data = itinerary.model_dump()
    warnings = data["warnings"]

    period_pairs = [
        ("morning", "afternoon"),
        ("afternoon", "evening"),
    ]

    for day_index, day in enumerate(itinerary.days):
        activities = {
            activity.period: activity
            for activity in day.activities
        }
        routes = []

        for from_period, to_period in period_pairs:
            origin_activity = activities.get(from_period)
            destination_activity = activities.get(to_period)
            label = f"Day {day.day_number}: {from_period} to {to_period}"

            if (
                origin_activity is None
                or destination_activity is None
                or origin_activity.place is None
                or destination_activity.place is None
            ):
                warnings.append(
                    f"{label}: walking route skipped because a place is missing."
                )
                continue

            origin = origin_activity.place
            destination = destination_activity.place

            try:
                route = provider.compute_route(
                    origin=origin,
                    destination=destination,
                    from_period=from_period,
                    to_period=to_period,
                )
            except RouteProviderError:
                route = Route(
                    from_period=from_period,
                    to_period=to_period,
                    from_place_id=origin.place_id,
                    to_place_id=destination.place_id,
                    status="provider_error",
                )
                warnings.append(
                    f"{label}: walking route information is temporarily unavailable."
                )

            if route.status == "not_found":
                warnings.append(f"{label}: no walking route was found.")

            if route.source is not None and route.source.provider == "mock":
                notice = "Mock walking routes use synthetic distances and durations."
                if notice not in warnings:
                    warnings.append(notice)

            routes.append(route.model_dump())

        data["days"][day_index]["routes"] = routes

    return ItineraryResponse.model_validate(data)