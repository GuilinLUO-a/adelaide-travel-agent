from itinerary import generate_itinerary, get_activity_categories
from models import Activity, ItineraryResponse, Place, TravelPreferences
from providers.base import PlaceProvider, PlaceProviderError


MOCK_WARNING = "Development mode: attached places are mock examples."


def generate_enriched_itinerary(
    preferences: TravelPreferences,
    provider: PlaceProvider,
) -> ItineraryResponse:
    base = generate_itinerary(**preferences.model_dump())
    response = ItineraryResponse.model_validate(base)

    if preferences.destination.strip().lower() != "adelaide":
        response.warnings.append(
            "Place enrichment currently supports Adelaide only. "
            "Generic activity suggestions are shown."
        )
        return response

    # These results exist only while constructing this response.
    results_by_category: dict[str, list[Place] | None] = {}

    for day in response.days:
        categories = get_activity_categories(
            preferences.interests, day.day_number
        )
        used_place_ids: set[str] = set()

        for index, activity in enumerate(day.activities):
            category = categories[index]

            if category not in results_by_category:
                try:
                    results_by_category[category] = provider.search_places(
                        destination=preferences.destination,
                        category=category,
                    )
                except PlaceProviderError:
                    results_by_category[category] = None
                    response.warnings.append(
                        f"Could not load {category} places. "
                        "Activity suggestions are retained."
                    )
                else:
                    if not results_by_category[category]:
                        response.warnings.append(
                            f"No {category} place candidates were found."
                        )

            candidates = results_by_category[category]
            selected = None

            if candidates is None:
                status = "provider_error"
            else:
                for candidate in candidates:
                    if candidate.place_id not in used_place_ids:
                        selected = candidate
                        break

                if selected is None:
                    status = "not_found"

                    if candidates:
                        response.warnings.append(
                            f"No unused {category} place candidate is available "
                            f"for day {day.day_number}, {activity.period}."
                        )
                else:
                    status = "available"
                    used_place_ids.add(selected.place_id)

                    if (
                        selected.source.provider == "mock"
                        and MOCK_WARNING not in response.warnings
                    ):
                        response.warnings.append(MOCK_WARNING)

            activity_data = activity.model_dump()
            activity_data["place_status"] = status
            activity_data["place"] = selected

            day.activities[index] = Activity.model_validate(activity_data)

    return response