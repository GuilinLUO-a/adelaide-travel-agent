
from datetime import date, timedelta
from decimal import Decimal, ROUND_DOWN

def get_trip_dates(start_date: date, end_date: date) -> list[date]:

    if end_date < start_date:
        raise ValueError("End date must be on or after start date.")

    total_days = (end_date - start_date).days + 1

    trip_dates = []

    for offset in range(total_days):
        current_date = start_date + timedelta(days=offset)
        trip_dates.append(current_date)

    return trip_dates


# Activity ideas organised by interest.
# Each list has ideas for morning, afternoon and evening.

ACTIVITY_IDEAS = {
    "museums": [
        "Visit a museum",
        "Explore a history exhibition",
        "Discover a local gallery",
    ],
    "food": [
        "Try a local cafe",
        "Explore a food market",
        "Enjoy a local restaurant",
    ],
    "nature": [
        "Explore a local park",
        "Visit a botanical garden",
        "Take a relaxing nature walk",
    ],
    "beaches": [
        "Take a coastal walk",
        "Relax at the beach",
        "Enjoy a seaside sunset",
    ],
}

DEFAULT_IDEAS = [
    "Explore the city centre",
    "Visit a local attraction",
    "Enjoy a relaxed evening",
]


def generate_activities(
    interests: list[str], day_number: int
) -> list[dict[str, str]]:

    if day_number < 1:
        raise ValueError("Day number must be positive.")

    # Match interests to the categories we currently support.
    matching_interests = [
        interest.strip().lower()
        for interest in interests
        if interest.strip().lower() in ACTIVITY_IDEAS
    ]

    periods = ["morning", "afternoon", "evening"]
    activities = []

    for index, period in enumerate(periods):

        if matching_interests:
            category_index = (
                day_number - 1 + index
            ) % len(matching_interests)

            category = matching_interests[category_index]
            title = ACTIVITY_IDEAS[category][index]
        else:
            title = DEFAULT_IDEAS[index]

        activities.append({
            "period": period,
            "title": title,
        })

    return activities


def allocate_daily_budgets(
    total_budget_aud: float, number_of_days: int
) -> list[float]:

    if number_of_days <= 0:
        raise ValueError("Number of days must be positive.")

    if total_budget_aud <= 0:
        raise ValueError("Budget must be positive.")

    # Convert dollars into whole cents.
    budget_cents = int(
        (Decimal(str(total_budget_aud)) * 100)
        .to_integral_value(rounding=ROUND_DOWN)
    )

    # Divide cents across days.
    base_cents, remainder = divmod(
        budget_cents, number_of_days
    )

    daily_budgets = []

    for day_index in range(number_of_days):
        cents = base_cents

        if day_index < remainder:
            cents += 1

        daily_budgets.append(cents / 100)

    return daily_budgets


def generate_itinerary(
    destination: str,
    start_date: date,
    end_date: date,
    budget_aud: float,
    travellers: int,
    interests: list[str],
) -> dict:

    # 1. Generate all dates.
    trip_dates = get_trip_dates(start_date, end_date)

    # 2. Allocate the budget between dates.
    daily_budgets = allocate_daily_budgets(
        budget_aud, len(trip_dates)
    )

    # 3. Build the daily itinerary.
    days = []

    for day_number, (trip_date, daily_budget) in enumerate(
        zip(trip_dates, daily_budgets), start=1
    ):
        activities = generate_activities(
            interests, day_number
        )

        days.append({
            "day_number": day_number,
            "date": trip_date,
            "allocated_budget_aud": daily_budget,
            "activities": activities,
        })

    # 4. Return the complete itinerary.
    return {
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "total_budget_aud": budget_aud,
        "travellers": travellers,
        "days": days,
    }
