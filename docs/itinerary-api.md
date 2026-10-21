# Itinerary Generation API

## Endpoint

`POST /api/itinerary/generate`

Generates a suggested day-by-day itinerary from validated travel preferences.

## Request

The request uses the same TravelPreferences structure as Module 2.

```json
{
  "destination": "Adelaide",
  "start_date": "2026-11-10",
  "end_date": "2026-11-11",
  "budget_aud": 400,
  "travellers": 2,
  "interests": ["museums", "food"]
}
```

## Successful response

Status: `200 OK`

```json
{
  "destination": "Adelaide",
  "start_date": "2026-11-10",
  "end_date": "2026-11-11",
  "total_budget_aud": 400,
  "travellers": 2,
  "days": [
    {
      "day_number": 1,
      "date": "2026-11-10",
      "allocated_budget_aud": 200,
      "activities": [
        {"period": "morning", "title": "Explore a museum"},
        {"period": "afternoon", "title": "Discover local food"},
        {"period": "evening", "title": "Explore the city"}
      ]
    },
    {
      "day_number": 2,
      "date": "2026-11-11",
      "allocated_budget_aud": 200,
      "activities": [
        {"period": "morning", "title": "Visit a cultural attraction"},
        {"period": "afternoon", "title": "Explore local markets"},
        {"period": "evening", "title": "Enjoy a relaxed evening"}
      ]
    }
  ]
}
```

## Generation rules

- Include every date from start_date through end_date, inclusive.
- Support single-day trips.
- Provide suggested activities for each day.
- Use interests to influence activity selection.
- The sum of daily allocations must not exceed budget_aud.
- Budget allocations are planning values, not verified prices.
- Use deterministic generation for Module 3.
- No external AI API or live attraction data is required.

## Error responses

- `422 Unprocessable Entity`: Invalid travel preferences.
- `500 Internal Server Error`: Unexpected itinerary generation failure.

Connection failures and request timeouts will be handled by React.

## Out of scope

- Real-time attraction information and prices.
- Database storage.
- Maps, bookings, voice calls and LLM integration.