import { useMemo, useState } from 'react'
import {
    APIProvider,
    AdvancedMarker,
    Map,
    Polyline,
} from '@vis.gl/react-google-maps'

import FitMapToPlaces from './FitMapToPlaces'
import WarningList from './WarningList'

function collectPlaces(itinerary) {
    const places = []
    const seenIds = new Set()

    for (const day of itinerary.days) {
        for (const activity of day.activities) {
            const place = activity.place

            if (activity.place_status !== 'available' || !place) {
                continue
            }

            if (seenIds.has(place.place_id)) {
                continue
            }

            seenIds.add(place.place_id)
            places.push(place)
        }
    }

    return places
}

function collectMapRoutes(itinerary) {
    const entries = []

    for (const day of itinerary.days) {
        for (const route of day.routes ?? []) {
            if (
                route.status !== 'available'
                || route.source?.provider !== 'google_routes'
                || !route.encoded_polyline
            ) {
                continue
            }

            entries.push({
                key: `${day.date}-${route.from_period}-${route.to_period}`,
                route,
            })
        }
    }

    return entries
}

export default function ItineraryMap({ itinerary }) {
    const [hasLoadError, setHasLoadError] = useState(false)

    const apiKey =
        import.meta.env.VITE_GOOGLE_MAPS_API_KEY?.trim()

    const places = useMemo(
        () => collectPlaces(itinerary),
        [itinerary]
    )

    const routeEntries = useMemo(
        () => collectMapRoutes(itinerary),
        [itinerary]
    )

    const mapRouteWarnings = [
        ...new Set(
            routeEntries.flatMap(
                (entry) => entry.route.warnings ?? []
            )
        ),
    ]

    if (places.length === 0) {
        return <p>No place locations are available to display.</p>
    }

    if (!apiKey) {
        return (
            <p>
                The map is unavailable because it has not been configured.
            </p>
        )
    }

    if (hasLoadError) {
        return (
            <p role="status">
                The map could not be loaded.
                Your itinerary is still available.
            </p>
        )
    }

    const firstPlace = places[0]

    const hasMockPlaces = places.some(
        (place) => place.source?.provider === 'mock'
    )

    return (
        <section aria-label="Trip map">
            <h4>Trip map</h4>

            <p>
                Showing {places.length} distinct place locations.
            </p>

            {hasMockPlaces && (
                <p>
                    Mock place markers show synthetic locations
                    for development.
                </p>
            )}

            {routeEntries.length > 0 ? (
                <p>
                    Blue lines show {routeEntries.length} available walking
                    journeys across all trip days.
                </p>
            ) : (
                <p>
                    Route geometry is unavailable.
                    See the walking-route summaries below.
                </p>
            )}

            <WarningList
                warnings={mapRouteWarnings}
                title="Map route notes"
            />

            <APIProvider
                apiKey={apiKey}
                onError={() => setHasLoadError(true)}
            >
                <Map
                    mapId="DEMO_MAP_ID"
                    defaultCenter={{
                        lat: firstPlace.location.latitude,
                        lng: firstPlace.location.longitude,
                    }}
                    defaultZoom={13}
                    gestureHandling="cooperative"
                    style={{
                        width: '100%',
                        height: '360px',
                    }}
                >
                    <FitMapToPlaces places={places} />

                    {routeEntries.map((entry) => (
                        <Polyline
                            key={entry.key}
                            encodedPath={entry.route.encoded_polyline}
                            strokeColor="#1967d2"
                            strokeOpacity={0.85}
                            strokeWeight={5}
                            clickable={false}
                        />
                    ))}

                    {places.map((place) => (
                        <AdvancedMarker
                            key={place.place_id}
                            position={{
                                lat: place.location.latitude,
                                lng: place.location.longitude,
                            }}
                            title={place.name}
                        />
                    ))}
                </Map>
            </APIProvider>
        </section>
    )
}