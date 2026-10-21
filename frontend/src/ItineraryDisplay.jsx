
import './ItineraryDisplay.css'

const PERIOD_LABELS = {
    morning: 'Morning',
    afternoon: 'Afternoon',
    evening: 'Evening',
}

function formatMoney(amount) {
    return new Intl.NumberFormat('en-AU', {
        style: 'currency',
        currency: 'AUD',
    }).format(amount)
}

export default function ItineraryDisplay({ itinerary }) {
    return (
        <section className="itinerary">
            <h3>Your {itinerary.destination} Itinerary</h3>

            <p className="itinerary-summary">
                {itinerary.start_date} to {itinerary.end_date}
                {' · '}
                {itinerary.travellers}{' '}
                {itinerary.travellers === 1
                    ? 'traveller'
                    : 'travellers'}
                {' · '}
                Total budget: {formatMoney(itinerary.total_budget_aud)}
            </p>

            <div className="itinerary-days">
                {itinerary.days.map((day) => (
                    <article className="itinerary-day" key={day.date}>
                        <div className="itinerary-day-header">
                            <h4>
                                Day {day.day_number} — {day.date}
                            </h4>

                            <p>
                                {formatMoney(day.allocated_budget_aud)}
                                {' '}allocated
                            </p>
                        </div>

                        <ul className="itinerary-activities">
                            {day.activities.map((activity, index) => (
                                <li key={`${activity.period}-${index}`}>
                                    <strong>
                                        {PERIOD_LABELS[activity.period]
                                            ?? activity.period}:
                                    </strong>
                                    {' '}{activity.title}
                                </li>
                            ))}
                        </ul>
                    </article>
                ))}
            </div>

            <p className="itinerary-note">
                Daily budgets are planning allocations,
                not verified activity prices.
            </p>
        </section>
    )
}
