
from datetime import date

import pytest

from itinerary import (
    get_trip_dates,
    generate_activities,
    allocate_daily_budgets,
    generate_itinerary,
)


def test_trip_dates_include_end_date():
    result = get_trip_dates(
        date(2026, 11, 10),
        date(2026, 11, 12),
    )

    assert len(result) == 3
    assert result[-1] == date(2026, 11, 12)


def test_single_day_trip():
    result = get_trip_dates(
        date(2026, 11, 10),
        date(2026, 11, 10),
    )

    assert result == [date(2026, 11, 10)]


def test_activities_match_interests():
    activities = generate_activities(
        ["museums", "food"], 1
    )

    assert len(activities) == 3
    assert activities[0]["period"] == "morning"
    assert activities[0]["title"] == "Visit a museum"
    assert activities[1]["title"] == "Explore a food market"


def test_default_activities():
    activities = generate_activities([], 1)

    assert len(activities) == 3
    assert activities[0]["title"] == "Explore the city centre"


def test_budget_allocation():
    result = allocate_daily_budgets(100, 3)

    assert result == [33.34, 33.33, 33.33]
    assert round(sum(result), 2) == 100


def test_invalid_date_range():
    with pytest.raises(ValueError):
        get_trip_dates(
            date(2026, 11, 12),
            date(2026, 11, 10),
        )


def test_complete_itinerary():
    result = generate_itinerary(
        destination="Adelaide",
        start_date=date(2026, 11, 10),
        end_date=date(2026, 11, 12),
        budget_aud=300,
        travellers=2,
        interests=["food", "museums"],
    )

    assert result["destination"] == "Adelaide"
    assert result["travellers"] == 2
    assert len(result["days"]) == 3

    assert result["days"][0]["day_number"] == 1
    assert result["days"][0]["date"] == date(2026, 11, 10)

    total_cents = sum(
        round(day["allocated_budget_aud"] * 100)
        for day in result["days"]
    )
    assert total_cents == 30000
