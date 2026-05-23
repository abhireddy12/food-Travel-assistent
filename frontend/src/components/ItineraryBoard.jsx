import { useState } from 'react';

function DetailModal({ item, type, onClose }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-3xl bg-white shadow-2xl">
        {/* Header with Close Button */}
        <div className="sticky top-0 flex items-center justify-between border-b border-slate-200 bg-gradient-to-r from-slate-950 to-slate-800 px-6 py-4 text-white">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-slate-300">
              {type === 'food' ? '🍽️ Food Details' : '📍 Place Details'}
            </p>
            <h2 className="mt-2 text-3xl font-bold">{item.name}</h2>
          </div>
          <button
            onClick={onClose}
            className="rounded-full bg-white/20 p-2 hover:bg-white/30 transition"
          >
            <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Image Section */}
        {item.image && (
          <div className="relative w-full overflow-hidden bg-slate-200">
            <img
              src={item.image}
              alt={item.name}
              className="h-96 w-full object-cover"
              onError={(e) => {
                e.target.parentElement.innerHTML = '<div className="h-96 w-full flex items-center justify-center bg-gradient-to-br from-slate-300 to-slate-400"><p className="text-slate-600 font-semibold">Image loading...</p></div>';
              }}
            />
          </div>
        )}

        {/* Content Section */}
        <div className="space-y-6 p-6 md:p-8">
          {/* Main Description */}
          <div className="space-y-3">
            <h3 className="text-2xl font-bold text-slate-950">About</h3>
            <p className="leading-relaxed text-slate-700 text-lg">
              {item.description}
            </p>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
            {/* Cuisine/Category */}
            {item.cuisine && (
              <div className="rounded-2xl bg-gradient-to-br from-slate-100 to-slate-50 p-4 border border-slate-200">
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-600">
                  {type === 'food' ? '🥘 Cuisine' : '🏛️ Category'}
                </p>
                <p className="mt-2 text-lg font-semibold text-slate-900">{item.cuisine}</p>
              </div>
            )}

            {/* Cost */}
            {item.cost && (
              <div className={`rounded-2xl p-4 border ${
                type === 'food'
                  ? 'bg-gradient-to-br from-rose-50 to-rose-100 border-rose-200'
                  : 'bg-gradient-to-br from-amber-50 to-amber-100 border-amber-200'
              }`}>
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-600">
                  💰 Est. Cost
                </p>
                <p className={`mt-2 text-lg font-bold ${
                  type === 'food' ? 'text-rose-700' : 'text-amber-700'
                }`}>
                  {item.cost}
                </p>
              </div>
            )}

            {/* Recommendation */}
            <div className="rounded-2xl bg-gradient-to-br from-blue-50 to-blue-100 p-4 border border-blue-200">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-blue-700">
                ⭐ Rating
              </p>
              <p className="mt-2 text-lg font-bold text-blue-900">4.5/5</p>
            </div>
          </div>

          {/* Pro Tips Section */}
          <div className="space-y-3 rounded-2xl bg-blue-50 border-l-4 border-blue-400 p-4">
            <p className="flex items-start gap-3">
              <span className="text-xl">💡</span>
              <span className="text-sm text-blue-900">
                <strong>Best Time to Visit:</strong> Early morning or evening for the best experience. Book in advance during peak seasons.
              </span>
            </p>
            <p className="flex items-start gap-3">
              <span className="text-xl">📸</span>
              <span className="text-sm text-blue-900">
                <strong>Photography Tip:</strong> Golden hour (sunrise/sunset) provides the best lighting for photos.
              </span>
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              onClick={onClose}
              className="flex-1 rounded-2xl bg-slate-100 px-4 py-3 font-semibold text-slate-900 hover:bg-slate-200 transition"
            >
              ← Back to Itinerary
            </button>
            <button
              onClick={() => window.open(`https://maps.google.com/maps/search/${item.name}`, '_blank')}
              className="flex-1 rounded-2xl bg-blue-500 px-4 py-3 font-semibold text-white hover:bg-blue-600 transition"
            >
              🗺️ Get Directions
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function SlotCard({ slot, type }) {
  const [selectedItem, setSelectedItem] = useState(null);

  return (
    <>
      <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-slate-500">{slot.title}</p>
            {slot.timestamp && <p className="mt-1 text-xs text-slate-500">{slot.timestamp}</p>}
          </div>
        </div>
        <p className="mt-2 text-sm text-slate-700">{slot.description}</p>

        <div className="mt-4">
          {type === 'food' && slot.food && slot.food.length > 0 && (
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-rose-700">🍽️ Food & Dining</p>
              <div className="mt-3 space-y-3">
                {slot.food.map((food, idx) => (
                  <div key={`${food.name}-${idx}`} className="rounded-2xl border border-rose-100 bg-white p-3">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <h4 className="font-semibold text-slate-950">{food.name}</h4>
                        <p className="mt-1 text-sm text-slate-600">{food.cuisine}</p>
                      </div>
                      <button
                        onClick={() => setSelectedItem(food)}
                        className="flex-shrink-0 rounded-full bg-rose-100 px-3 py-1 text-xs font-semibold text-rose-700 hover:bg-rose-200 transition"
                      >
                        View
                      </button>
                    </div>
                    <div className="mt-2 flex items-center justify-between">
                      <span className="rounded-full bg-rose-50 px-3 py-1 text-xs font-semibold text-rose-700">{food.cost}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {type === 'places' && slot.places && slot.places.length > 0 && (
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-amber-700">📍 Places to Visit</p>
              <div className="mt-3 space-y-3">
                {slot.places.map((place, idx) => (
                  <div key={`${place.name}-${idx}`} className="rounded-2xl border border-amber-100 bg-white p-3">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <h4 className="font-semibold text-slate-950">{place.name}</h4>
                        <p className="mt-1 text-sm text-slate-600">{place.description}</p>
                      </div>
                      <button
                        onClick={() => setSelectedItem(place)}
                        className="flex-shrink-0 rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-700 hover:bg-amber-200 transition"
                      >
                        View
                      </button>
                    </div>
                    <div className="mt-2 flex items-center justify-between">
                      <span className="rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700">{place.cost}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {selectedItem && (
        <DetailModal
          item={selectedItem}
          type={type}
          onClose={() => setSelectedItem(null)}
        />
      )}
    </>
  );
}

export default function ItineraryBoard({ itinerary }) {
  const [viewMode, setViewMode] = useState('food');
  const days = itinerary?.days_plan || [];

  if (!itinerary) {
    return (
      <section className="rounded-[2rem] border border-dashed border-slate-300 bg-white/70 p-8 text-slate-500 shadow-glow">
        <h3 className="text-xl font-semibold text-slate-950">Your itinerary will appear here</h3>
        <p className="mt-2 max-w-2xl text-sm leading-6">
          Validate the location and generate a trip plan to see a full day-by-day layout with places, food, and cost estimates.
        </p>
      </section>
    );
  }

  return (
    <section className="space-y-5">
      <div className="rounded-[2rem] bg-slate-950 px-6 py-7 text-white shadow-glow md:px-8">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-amber-300">Generated Plan</p>
            <h3 className="mt-2 text-3xl font-bold md:text-4xl">{itinerary.location}</h3>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-300">{itinerary.summary}</p>
          </div>
          <div className="grid grid-cols-3 gap-3 text-sm">
            <div className="rounded-2xl bg-white/10 px-4 py-3">
              <p className="text-slate-300">Days</p>
              <p className="mt-1 text-lg font-bold">{itinerary.days}</p>
            </div>
            <div className="rounded-2xl bg-white/10 px-4 py-3">
              <p className="text-slate-300">People</p>
              <p className="mt-1 text-lg font-bold">{itinerary.people}</p>
            </div>
            <div className="rounded-2xl bg-white/10 px-4 py-3">
              <p className="text-slate-300">Budget</p>
              <p className="mt-1 text-lg font-bold">{itinerary.budget}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Toggle Buttons */}
      <div className="flex gap-3 rounded-2xl bg-white/70 p-3 shadow-glow">
        <button
          onClick={() => setViewMode('food')}
          className={`flex-1 rounded-xl px-4 py-3 font-semibold transition ${
            viewMode === 'food'
              ? 'bg-rose-500 text-white shadow-md'
              : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
          }`}
        >
          🍽️ Food Journey
        </button>
        <button
          onClick={() => setViewMode('places')}
          className={`flex-1 rounded-xl px-4 py-3 font-semibold transition ${
            viewMode === 'places'
              ? 'bg-amber-500 text-white shadow-md'
              : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
          }`}
        >
          📍 Tourist Places
        </button>
      </div>

      <div className="space-y-4">
        {days.map((day, index) => {
          const dayData = viewMode === 'food' ? day.food : day.places;
          return (
            <details
              key={`${day.food?.day || day.places?.day}-${index}`}
              open={index === 0}
              className="overflow-hidden rounded-[1.75rem] border border-white/70 bg-white/90 shadow-glow"
            >
              <summary className="cursor-pointer list-none px-6 py-5 outline-none transition hover:bg-slate-50 md:px-8">
                <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.28em] text-amber-700">Day {dayData.day}</p>
                    <h4 className="mt-1 text-2xl font-bold text-slate-950">{dayData.title}</h4>
                  </div>
                  <p className="max-w-2xl text-sm text-slate-600">{dayData.summary}</p>
                </div>
              </summary>
              <div className="space-y-4 border-t border-slate-200 px-6 py-6 md:px-8">
                <SlotCard slot={dayData.morning} type={viewMode} />
                <SlotCard slot={dayData.afternoon} type={viewMode} />
                <SlotCard slot={dayData.evening} type={viewMode} />
              </div>
            </details>
          );
        })}
      </div>
    </section>
  );
}
