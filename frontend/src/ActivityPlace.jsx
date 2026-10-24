import RetrievedAt from './RetrievedAt'

const PLACE_MESSAGES = {
    not_requested: 'Place lookup was not performed for this activity.',
    not_found: 'No matching place was found.',
    provider_error: 'Place information is temporarily unavailable.',
}

export default function ActivityPlace({ activity }) {
    if (activity.place_status !== 'available' || !activity.place) {
        return (
            <div className="activity-place">
                <p>{activity.title}</p>
                <p>
                    {PLACE_MESSAGES[activity.place_status]
                        ?? 'Place information is unavailable.'}
                </p>
            </div>
        )
    }

    const place = activity.place
    const isMock = place.source.provider === 'mock'

    return (
        <div className="activity-place">
            <p><strong>{place.name}</strong></p>
            <p>{place.address}</p>

            {isMock ? (
                <p>Mock place — synthetic development data.</p>
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

            <RetrievedAt timestamp={place.source.retrieved_at} />
            {place.source.attributions.map((attribution, index) => (
                <p key={`${attribution.label}-${index}`}>
                    {attribution.url ? (
                        <a
                            href={attribution.url}
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            {attribution.label}
                        </a>
                    ) : (
                        attribution.label
                    )}
                </p>
            ))}
        </div>
    )
}