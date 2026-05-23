function FieldLabel({ children }) {
  return <label className="mb-2 block text-sm font-semibold text-slate-700">{children}</label>;
}

export default function TripForm({ form, setForm, onSubmit, onValidateLocation, validation, loading }) {
  const updateField = (field, value) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  return (
    <form
      onSubmit={onSubmit}
      className="rounded-[2rem] border border-white/60 bg-white/85 p-6 shadow-glow backdrop-blur-xl md:p-8"
    >
      <div className="mb-8">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-amber-600">Trip Builder</p>
        <h2 className="mt-3 text-3xl font-bold text-slate-950 md:text-4xl">Plan food, places, and pace in one shot.</h2>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">
          Enter your destination and preferences. The backend validates the location first, then generates a budget-aware itinerary.
        </p>
      </div>

      <div className="grid gap-5 md:grid-cols-2">
        <div className="md:col-span-2">
          <FieldLabel>Location</FieldLabel>
          <div className="flex flex-col gap-3 md:flex-row">
            <input
              value={form.location}
              onChange={(event) => updateField('location', event.target.value)}
              onBlur={onValidateLocation}
              placeholder="Try Goa, Jaipur, Tokyo..."
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-950 outline-none transition focus:border-amber-500 focus:bg-white"
            />
            <button
              type="button"
              onClick={onValidateLocation}
              className="rounded-2xl border border-slate-200 bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
            >
              Validate
            </button>
          </div>
          <div className="mt-3 min-h-[2rem] text-sm">
            {validation.status === 'checking' && <p className="text-slate-500">Checking destination with Gemini...</p>}
            {validation.status === 'valid' && <p className="text-emerald-700">{validation.message}</p>}
            {validation.status === 'invalid' && (
              <div className="space-y-2 text-rose-700">
                <p>{validation.message}</p>
                {validation.suggestions?.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {validation.suggestions.map((suggestion) => (
                      <button
                        key={suggestion}
                        type="button"
                        onClick={() => updateField('location', suggestion)}
                        className="rounded-full border border-rose-200 bg-rose-50 px-3 py-1 text-xs font-semibold transition hover:bg-rose-100"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        <div>
          <FieldLabel>Number of People</FieldLabel>
          <input
            type="number"
            min="1"
            value={form.people}
            onChange={(event) => updateField('people', event.target.value)}
            className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-950 outline-none transition focus:border-amber-500 focus:bg-white"
          />
        </div>

        <div>
          <FieldLabel>Number of Days</FieldLabel>
          <input
            type="number"
            min="1"
            max="14"
            value={form.days}
            onChange={(event) => updateField('days', event.target.value)}
            className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-950 outline-none transition focus:border-amber-500 focus:bg-white"
          />
        </div>

        <div>
          <FieldLabel>Budget</FieldLabel>
          <select
            value={form.budgetPreset}
            onChange={(event) => updateField('budgetPreset', event.target.value)}
            className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-950 outline-none transition focus:border-amber-500 focus:bg-white"
          >
            <option>Low</option>
            <option>Medium</option>
            <option>High</option>
          </select>
        </div>

        <div>
          <FieldLabel>Custom Budget Amount</FieldLabel>
          <input
            value={form.budgetAmount}
            onChange={(event) => updateField('budgetAmount', event.target.value)}
            placeholder="Optional amount in INR/USD"
            className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-950 outline-none transition focus:border-amber-500 focus:bg-white"
          />
        </div>

        <div className="md:col-span-2">
          <FieldLabel>Favorites / Preferences</FieldLabel>
          <textarea
            rows="4"
            value={form.preferences}
            onChange={(event) => updateField('preferences', event.target.value)}
            placeholder="Examples: beaches, spicy food, museums, nightlife, street food"
            className="w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-950 outline-none transition focus:border-amber-500 focus:bg-white"
          />
        </div>
      </div>

      <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-slate-500">The chatbot keeps the current trip context for the full session.</p>
        <button
          type="submit"
          disabled={loading}
          className="rounded-2xl bg-gradient-to-r from-amber-500 via-orange-500 to-rose-500 px-6 py-3 text-sm font-bold text-white shadow-lg shadow-orange-200 transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? 'Generating itinerary...' : 'Generate itinerary'}
        </button>
      </div>
    </form>
  );
}
