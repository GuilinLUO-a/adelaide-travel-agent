import { useEffect } from 'react'
import {
    useMap,
    useMapsLibrary,
} from '@vis.gl/react-google-maps'

export default function FitMapToPlaces({ places }) {
    const map = useMap()
    const core = useMapsLibrary('core')

    useEffect(() => {
        if (!map || !core || places.length === 0) {
            return
        }

        const bounds = new core.LatLngBounds()

        for (const place of places) {
            bounds.extend({
                lat: place.location.latitude,
                lng: place.location.longitude,
            })
        }

        const northEast = bounds.getNorthEast()
        const southWest = bounds.getSouthWest()

        if (northEast.equals(southWest)) {
            map.setCenter(bounds.getCenter())
            map.setZoom(15)
            return
        }

        map.fitBounds(bounds, 48)
    }, [map, core, places])

    return null
}