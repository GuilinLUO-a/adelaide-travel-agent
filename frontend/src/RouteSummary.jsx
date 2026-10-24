import RetrievedAt from './RetrievedAt'
import WarningList from './WarningList'

const PERIOD_LABELS = {
    morning: 'Morning',
    afternoon: 'Afternoon',
    evening: 'Evening',
}

const ROUTE_MESSAGES = {
    not_found: 'No walking route was found between these places.',
    provider_error: 'Walking route information is temporarily unavailable.',
}

function formatDistance(meters) {
    if (!Number.isFinite(meters) || meters < 0) {
        return 'Distance unavailable'
    }

    return meters < 1000
        ? `${Math.round(meters)} m`
        : `${(meters / 1000).toFixed(2)} km`
}

function formatDuration(seconds) {
    if (!Number.isFinite(seconds) || seconds < 0) {
        return 'Duration unavailable'
    }

    if (seconds > 0 && seconds < 60) {
        return 'Less than 1 min'
    }

    return `${Math.round(seconds / 60)} min`
}

export default function RouteSummary({ route }) {
    return (
        <article className="activity-place route-summary">
            <p>
                <strong>
                    {PERIOD_LABELS[route.from_period] ?? route.from_period}
                    {' → '}
                    {PERIOD_LABELS[route.to_period] ?? route.to_period}
                </strong>
            </p>

            {route.status === 'available' ? (
                <>
                    <p>
                        Estimated walk:{' '}
                        {formatDistance(route.distance_meters)}
                        {' · '}
                        {formatDuration(route.duration_seconds)}
                    </p>

                    {route.source.provider === 'mock' ? (
                        <p>
                            Mock route — synthetic distance and duration.
                        </p>
                    ) : (
                        <p>
                            <span
                                className="google-maps-attribution"
                                translate="no"
                            >
                                Google Maps
                            </span>
                        </p>
                    )}

                    <RetrievedAt
                        timestamp={route.source.retrieved_at}
                    />
                </>
            ) : (
                <p>
                    {ROUTE_MESSAGES[route.status]
                        ?? 'Walking route information is unavailable.'}
                </p>
            )}

            <WarningList
                warnings={route.warnings}
                title="Route notes"
            />
        </article>
    )
}