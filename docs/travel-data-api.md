# Travel Data Contract — Module 4

## Goal

Extend POST /api/itinerary/generate with place information,
source metadata, routes, and warnings.

Preserve the existing travel preferences, dates, activity titles,
and daily budget allocations.

Adelaide is the initial destination supported for place and route
enrichment. Other destinations retain generic suggestions, with
place lookups marked not_requested and an explanatory warning.

## Request

Keep the existing TravelPreferences request structure unchanged.

The initial route mode is walking.

## Place model

A usable place contains:

- place_id: non-empty provider identifier.
- name: non-empty display name.
- address: non-empty display address.
- location.latitude: finite number between -90 and 90.
- location.longitude: finite number between -180 and 180.
- source: source metadata.

Mock IDs are development identifiers, not real provider place IDs.

## Source model

- provider: mock, google_places, or google_routes.
- retrieved_at: timezone-aware ISO 8601 timestamp.
- attributions: list of attribution objects.

Each attribution contains:

- label: display text.
- url: attribution URL, or null when no URL is supplied.

For mock responses, retrieved_at records when the response was
produced.

A retrieval timestamp does not guarantee current opening hours,
availability, or suitability for a future visit.

## Activity extension

Preserve:

- period
- title

Add:

- place_status
- place

Supported place_status values:

- not_requested: no lookup was attempted.
- available: a usable place is attached.
- not_found: the lookup completed without a usable match.
- provider_error: the lookup failed or returned invalid data.

place must contain a valid Place when status is available.
Otherwise, place must be null.

## Day extension

Preserve the existing day fields.

Add:

- routes: list of route objects.

Only request routes between consecutive activities when both
activities have usable places.

Do not connect across an activity with missing place information.

## Route model

- from_period: starting activity period.
- to_period: destination activity period.
- from_place_id: starting place identifier.
- to_place_id: destination place identifier.
- travel_mode: walking for the initial implementation.
- status: available, not_found, or provider_error.
- distance_meters: non-negative finite number, or null.
- duration_seconds: non-negative finite number, or null.
- is_estimate: true for travel estimates.
- encoded_polyline: encoded route geometry, or null.
- source: source metadata, or null.

An available route requires distance, duration, and source.

An unavailable route has null distance, duration, geometry,
and source.

A missing polyline does not prevent displaying available distance
and duration information.

## Response extension

Preserve the existing top-level response fields.

Add:

- warnings: list of user-readable strings.

Use an empty list when there are no warnings.

## Example enriched response

This example uses synthetic mock data. Its names, addresses,
identifiers, coordinates, and route values are illustrative.

The timestamp is an example, not a value to hardcode.

```json
{
  "destination": "Adelaide",
  "start_date": "2026-11-10",
  "end_date": "2026-11-10",
  "total_budget_aud": 150,
  "travellers": 1,
  "days": [
    {
      "day_number": 1,
      "date": "2026-11-10",
      "allocated_budget_aud": 150,
      "activities": [
        {
          "period": "morning",
          "title": "Visit a museum",
          "place_status": "available",
          "place": {
            "place_id": "mock-museum-1",
            "name": "Example Museum",
            "address": "Example museum address, Adelaide",
            "location": {
              "latitude": -34.92,
              "longitude": 138.60
            },
            "source": {
              "provider": "mock",
              "retrieved_at": "2026-10-22T10:00:00Z",
              "attributions": []
            }
          }
        },
        {
          "period": "afternoon",
          "title": "Explore a food market",
          "place_status": "available",
          "place": {
            "place_id": "mock-market-1",
            "name": "Example Market",
            "address": "Example market address, Adelaide",
            "location": {
              "latitude": -34.93,
              "longitude": 138.60
            },
            "source": {
              "provider": "mock",
              "retrieved_at": "2026-10-22T10:00:00Z",
              "attributions": []
            }
          }
        },
        {
          "period": "evening",
          "title": "Discover a local gallery",
          "place_status": "not_found",
          "place": null
        }
      ],
      "routes": [
        {
          "from_period": "morning",
          "to_period": "afternoon",
          "from_place_id": "mock-museum-1",
          "to_place_id": "mock-market-1",
          "travel_mode": "walking",
          "status": "available",
          "distance_meters": 1400,
          "duration_seconds": 1080,
          "is_estimate": true,
          "encoded_polyline": null,
          "source": {
            "provider": "mock",
            "retrieved_at": "2026-10-22T10:00:00Z",
            "attributions": []
          }
        }
      ]
    }
  ],
  "warnings": [
    "Development mode: place and route data are mock examples.",
    "No suitable place was found for the evening activity on day 1.",
    "The afternoon-to-evening route was skipped because the evening activity has no place."
  ]
}
```

## Missing information and failures

- Preserve the generic itinerary when enrichment fails.
- Use null for unavailable objects or values.
- Do not substitute zero for unknown distances or durations.
- Do not invent provider IDs, addresses, or coordinates.
- Identify mock information through its source.
- Return explanatory warnings for unavailable enrichment.
- Keep request validation errors as HTTP 422.
- Allow HTTP 200 when a valid itinerary is returned with partial
  enrichment and warnings.
- Do not expose API keys or raw provider error responses.

## Estimates and limitations

- allocated_budget_aud is a planning allocation.
- It is not a verified price or activity cost.
- Route durations are estimates.
- Attached places are suggestions.
- Place matching does not verify opening hours for the visit.
- Route information alone does not prove that the entire daily
  schedule is feasible.

## Development and testing

- Support mock providers.
- Automated tests must not require live provider requests.
- Test successful enrichment, empty results, malformed responses,
  provider failures, and preservation of the original itinerary.