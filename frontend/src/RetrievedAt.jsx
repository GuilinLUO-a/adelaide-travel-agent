const adelaideFormatter = new Intl.DateTimeFormat('en-AU', {
    dateStyle: 'medium',
    timeStyle: 'long',
    timeZone: 'Australia/Adelaide',
})

export default function RetrievedAt({ timestamp }) {
    const date = timestamp ? new Date(timestamp) : null

    if (!date || Number.isNaN(date.getTime())) {
        return (
            <p className="retrieved-at">
                Retrieval time unavailable.
            </p>
        )
    }

    return (
        <p className="retrieved-at">
            Retrieved:{' '}
            <time dateTime={timestamp}>
                {adelaideFormatter.format(date)}
            </time>
        </p>
    )
}