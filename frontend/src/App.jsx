import { useState } from 'react';
import { apiRequest } from './lib/api';
import TripForm from './components/TripForm';
import ItineraryBoard from './components/ItineraryBoard';
import ChatWidget from './components/ChatWidget';

const initialForm = {
  location: 'Goa',
  people: 2,
  preferences: 'beaches, spicy food, museums',
  budgetPreset: 'Medium',
  budgetAmount: '',
  days: 3,
};

const seedMessages = [
  {
    role: 'assistant',
    content: 'Generate a trip plan first, then ask me to add a beach day, make it cheaper, or find better food spots.',
  },
];

export default function App() {
  const [form, setForm] = useState(initialForm);
  const [validation, setValidation] = useState({ status: 'idle', message: '', suggestions: [] });
  const [itinerary, setItinerary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [chatOpen, setChatOpen] = useState(false);
  const [chatLoading, setChatLoading] = useState(false);
  const [messages, setMessages] = useState(seedMessages);

  const tripContext = itinerary || null;

  const validateLocation = async () => {
    const location = form.location.trim();
    if (!location) {
      setValidation({ status: 'invalid', message: 'Location is required.', suggestions: [] });
      return null;
    }

    setValidation({ status: 'checking', message: '', suggestions: [] });
    try {
      const result = await apiRequest('/validate-location', {
        method: 'POST',
        body: { location },
      });

      if (result.valid) {
        setValidation({
          status: 'valid',
          message: result.message || 'Location verified successfully.',
          suggestions: result.suggestions || [],
        });
        if (result.canonical_location) {
          setForm((current) => ({ ...current, location: result.canonical_location }));
        }
        return result;
      }

      setValidation({
        status: 'invalid',
        message: result.message || 'This location could not be verified.',
        suggestions: result.suggestions || [],
      });
      return result;
    } catch (requestError) {
      setValidation({ status: 'invalid', message: requestError.message, suggestions: [] });
      return null;
    }
  };

  const generateItinerary = async (event) => {
    event.preventDefault();
    setError('');

    const validationResult = await validateLocation();
    if (!validationResult || !validationResult.valid) {
      setError('Please use a valid location or pick one of the suggested alternatives.');
      return;
    }

    const payload = {
      location: form.location.trim(),
      people: Number(form.people),
      preferences: form.preferences,
      budget: form.budgetAmount.trim() || form.budgetPreset,
      days: Number(form.days),
    };

    setLoading(true);
    try {
      const response = await apiRequest('/generate-itinerary', {
        method: 'POST',
        body: payload,
      });

      setItinerary(response.itinerary);
      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          content: `Trip plan ready for ${response.itinerary.location}. Ask me to refine any day, food choice, or budget level.`,
        },
      ]);
      setChatOpen(true);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  const sendChatMessage = async (message) => {
    if (!tripContext) {
      setMessages((current) => [
        ...current,
        { role: 'assistant', content: 'Generate an itinerary first so I can keep the trip context.' },
      ]);
      return;
    }

    const nextMessages = [...messages, { role: 'user', content: message }];
    setMessages(nextMessages);
    setChatLoading(true);

    try {
      const response = await apiRequest('/chat', {
        method: 'POST',
        body: {
          message,
          tripContext,
          history: nextMessages,
        },
      });

      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          content: response.reply || 'I have updated the trip context.',
        },
      ]);
    } catch (requestError) {
      setMessages((current) => [
        ...current,
        { role: 'assistant', content: requestError.message },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <main className="min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top_left,_rgba(251,191,36,0.24),_transparent_28%),radial-gradient(circle_at_top_right,_rgba(244,114,182,0.18),_transparent_24%),linear-gradient(180deg,_#fff7ed_0%,_#f8fafc_40%,_#e2e8f0_100%)] text-slate-950">
      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-8 px-4 py-6 sm:px-6 lg:px-8 lg:py-10">
        <header className="flex flex-col gap-6 rounded-[2rem] border border-white/60 bg-white/75 p-6 shadow-glow backdrop-blur-xl md:flex-row md:items-center md:justify-between md:p-8">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.32em] text-amber-600">Food & Travel Assistant</p>
            <h1 className="mt-3 max-w-3xl text-4xl font-black tracking-tight text-slate-950 md:text-6xl">Plan the day, eat well, and keep the whole trip flexible.</h1>
            <p className="mt-4 max-w-3xl text-base leading-7 text-slate-600">
              React frontend, Flask backend, and Gemini-powered itinerary generation with live location validation and a persistent trip chatbot.
            </p>
          </div>
          <div className="grid grid-cols-3 gap-3 text-sm">
            <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3">
              <p className="text-slate-500">Validate</p>
              <p className="mt-1 font-bold">Location</p>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3">
              <p className="text-slate-500">Generate</p>
              <p className="mt-1 font-bold">Itinerary</p>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3">
              <p className="text-slate-500">Chat</p>
              <p className="mt-1 font-bold">Trip tweaks</p>
            </div>
          </div>
        </header>

        <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <TripForm
            form={form}
            setForm={setForm}
            onSubmit={generateItinerary}
            onValidateLocation={validateLocation}
            validation={validation}
            loading={loading}
          />

          <div className="space-y-4">
            {error ? (
              <div className="rounded-[1.75rem] border border-rose-200 bg-rose-50 p-5 text-rose-800 shadow-glow">
                <p className="text-sm font-semibold uppercase tracking-[0.28em] text-rose-500">Error</p>
                <p className="mt-2 text-sm leading-6">{error}</p>
              </div>
            ) : null}
            <ItineraryBoard itinerary={itinerary} />
          </div>
        </div>
      </div>

      <ChatWidget
        open={chatOpen}
        setOpen={setChatOpen}
        messages={messages}
        onSend={sendChatMessage}
        loading={chatLoading}
        tripLabel={tripContext ? `${tripContext.location} · ${tripContext.days} day plan` : ''}
      />
    </main>
  );
}
