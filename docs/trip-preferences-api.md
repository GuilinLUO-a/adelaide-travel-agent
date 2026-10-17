# Travel Preferences API

## Endpoint
`POST /api/trip-preferences`

Receives and validates a traveller's trip preferences.

## Example request
```json
{
  "destination": "Sydney",
  "start_date": "2026-11-10",
  "end_date": "2026-11-14",
  "budget_aud": 1200,
  "travellers": 2,
  "interests": ["beaches", "food"]
}
```
## Successful response
Status:`200 OK`

```json
{
    "destination": "Sydney",
    "start_date": "2026-11-10",
    "end_date": "2026-11-14",
    "budget_aud": 1200,
    "travellers": 2,
    "interests": ["beaches","food"]
}
```
## Validation rules
- Destination must not be empty or contain only spaces.
- Start date and end date must be valid dates.
- End date must be the same as or later than the start date.
- Total budget in AUD must be greater than `0`.
- Travellers must be a whole number greater than `0`.
- Interests are optional.
- If interests are omitted, they default to an empty list: `[]`.

## Invalid request examples
- Destination `" "` → rejected with `422`.
- Budget `0` → rejected with `422`.
- Travellers `1.5` → rejected with `422`.
- End date before start date → rejected with `422`.
- Interests omitted → accepted with `200`, using `[]`.