export default function WarningList({
    warnings = [],
    title = 'Itinerary notes',
}) {
    if (warnings.length === 0) {
        return null
    }

    return (
        <section
            className="itinerary-warnings"
            aria-label={title}
        >
            <h4>{title}</h4>

            <ul>
                {warnings.map((warning, index) => (
                    <li key={`${index}-${warning}`}>
                        {warning}
                    </li>
                ))}
            </ul>
        </section>
    )
}