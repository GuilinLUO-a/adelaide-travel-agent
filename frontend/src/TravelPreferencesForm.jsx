import { useState } from 'react'

export default function TravelPreferencesForm() {
    const [form, setForm] = useState({
        destination: '',
        start_date: '',
        end_date: '',
        budget_aud: '',
        travellers: '1',
        interests: '',
    })

    const [isSubmitting, setIsSubmitting] = useState(false)
    const [errorMessage, setErrorMessage] = useState('')
    const [acceptedPreferences, setAcceptedPreferences] = useState(null)

    function handleChange(event) {
        const { name, value } = event.target

        setForm((previous) => ({
            ...previous,
            [name]: value,
        }))
        setErrorMessage('')
        setAcceptedPreferences(null)
    }

    async function handleSubmit(event) {
        event.preventDefault()

        if (isSubmitting) return

        setIsSubmitting(true)
        setErrorMessage('')
        setAcceptedPreferences(null)

        const payload = {
            destination: form.destination,
            start_date: form.start_date,
            end_date: form.end_date,
            budget_aud: Number(form.budget_aud),
            travellers: Number(form.travellers),
            interests: form.interests
                .split(',')
                .map((interest) => interest.trim())
                .filter((interest) => interest !== ''),
        }

        const controller = new AbortController()
        const timeout = setTimeout(() => controller.abort(), 5000)

        try {
            const response = await fetch('/api/trip-preferences', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
                signal: controller.signal,
            })

            if (response.status === 422) {
                const data = await response.json()

                const labels = {
                    destination: 'Destination',
                    start_date: 'Start date',
                    end_date: 'End date',
                    budget_aud: 'Budget',
                    travellers: 'Travellers',
                    interests: 'Interests',
                }

                const messages = data.detail.map((issue) => {
                    const label = labels[issue.loc[1]] || 'Trip preferences'
                    return `${label}: ${issue.msg}`
                })

                setErrorMessage(messages.join(' '))
                return
            }

            if (!response.ok) {
                setErrorMessage(
                    'Could not submit preferences. Check that the backend is running and try again.'
                )
                return
            }

            const data = await response.json()
            setAcceptedPreferences(data)
        } catch (error) {
            setErrorMessage(
                error.name === 'AbortError'
                    ? 'The request took too long. Please try again.'
                    : 'Could not connect. Check that the backend is running and try again.'
            )
        } finally {
            clearTimeout(timeout)
            setIsSubmitting(false)
        }
    }

    return (
        <section>
            <h2>Your travel preferences</h2>

            {/* event.preventDefault() stops the browser 
    from refreshing the page when the form is submitted.*/}
            <form onSubmit={handleSubmit}>
                <fieldset disabled={isSubmitting}>
                    <legend>Trip details</legend>
                    <p>
                        <label>
                            Destination
                            <br />
                            <input
                                name="destination"
                                value={form.destination}
                                onChange={handleChange}
                                placeholder="Adelaide"
                                required
                            />
                        </label>
                    </p>

                    <p>
                        <label>
                            Start date
                            <br />
                            <input
                                type="date"
                                name="start_date"
                                value={form.start_date}
                                onChange={handleChange}
                                required
                            />
                        </label>
                    </p>

                    <p>
                        <label>
                            End date
                            <br />
                            <input
                                type="date"
                                name="end_date"
                                value={form.end_date}
                                onChange={handleChange}
                                min={form.start_date || undefined}
                                required
                            />
                        </label>
                    </p>

                    <p>
                        <label>
                            Total trip budget (AUD, all travellers)
                            <br />
                            <input
                                type="number"
                                name="budget_aud"
                                value={form.budget_aud}
                                onChange={handleChange}
                                min="0"
                                step="any"
                                required
                            />
                        </label>
                    </p>

                    <p>
                        <label>
                            Number of travellers
                            <br />
                            <input
                                type="number"
                                name="travellers"
                                value={form.travellers}
                                onChange={handleChange}
                                min="1"
                                step="1"
                                required
                            />
                        </label>
                    </p>

                    <p>
                        <label>
                            Interests (optional, separated by commas)
                            <br />
                            <input
                                name="interests"
                                value={form.interests}
                                onChange={handleChange}
                                placeholder="food, museums"
                            />
                        </label>
                    </p>
                    <button type="submit">
                        {isSubmitting ? 'Submitting...' : 'Submit preferences'}
                    </button>
                </fieldset>
            </form>
            {isSubmitting && <p role="status">Submitting your preferences...</p>}

            {errorMessage && <p role="alert">{errorMessage}</p>}

            {acceptedPreferences && (
                <section>
                    <h3>Preferences accepted</h3>
                    <dl>
                        <dt>Destination</dt>
                        <dd>{acceptedPreferences.destination}</dd>

                        <dt>Dates</dt>
                        <dd>
                            {acceptedPreferences.start_date} to {acceptedPreferences.end_date}
                        </dd>

                        <dt>Total budget</dt>
                        <dd>AUD {acceptedPreferences.budget_aud}</dd>

                        <dt>Travellers</dt>
                        <dd>{acceptedPreferences.travellers}</dd>

                        <dt>Interests</dt>
                        <dd>
                            {acceptedPreferences.interests.length > 0
                                ? acceptedPreferences.interests.join(', ')
                                : 'None specified'}
                        </dd>
                    </dl>
                </section>
            )}
        </section>
    )
}