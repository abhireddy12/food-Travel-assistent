import { useEffect, useRef, useState } from 'react';

export default function ChatWidget({ open, setOpen, messages, onSend, loading, tripLabel }) {
  const [draft, setDraft] = useState('');
  const viewportRef = useRef(null);

  useEffect(() => {
    if (viewportRef.current) {
      viewportRef.current.scrollTop = viewportRef.current.scrollHeight;
    }
  }, [messages, open]);

  const submitMessage = async (event) => {
    event.preventDefault();
    const value = draft.trim();
    if (!value) {
      return;
    }

    await onSend(value);
    setDraft('');
  };

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen((current) => !current)}
        className="fixed bottom-5 right-5 z-40 rounded-full bg-slate-950 px-5 py-4 text-sm font-semibold text-white shadow-2xl shadow-slate-400 transition hover:scale-105"
      >
        {open ? 'Close chat' : 'Trip chat'}
      </button>

      {open && (
        <section className="fixed bottom-24 right-5 z-40 flex h-[32rem] w-[min(92vw,24rem)] flex-col overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-glow">
          <header className="border-b border-slate-200 bg-slate-950 px-5 py-4 text-white">
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-amber-300">Gemini Trip Assistant</p>
            <h3 className="mt-1 text-lg font-bold">Plan changes and quick questions</h3>
            <p className="mt-1 text-xs text-slate-300">{tripLabel || 'No trip generated yet'}</p>
          </header>

          <div ref={viewportRef} className="flex-1 space-y-4 overflow-y-auto bg-slate-50 px-4 py-4">
            {messages.map((message, index) => (
              <div
                key={`${message.role}-${index}`}
                className={`max-w-[90%] rounded-3xl px-4 py-3 text-sm leading-6 ${
                  message.role === 'user'
                    ? 'ml-auto bg-slate-950 text-white'
                    : 'mr-auto border border-slate-200 bg-white text-slate-700'
                }`}
              >
                {message.content}
              </div>
            ))}
            {loading && <div className="mr-auto rounded-3xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-500">Thinking...</div>}
          </div>

          <form onSubmit={submitMessage} className="border-t border-slate-200 bg-white p-4">
            <div className="flex gap-2">
              <input
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                placeholder="Add a beach day, cheaper option, street food..."
                className="min-w-0 flex-1 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-950 outline-none transition focus:border-amber-500 focus:bg-white"
              />
              <button
                type="submit"
                disabled={loading}
                className="rounded-2xl bg-amber-500 px-4 py-3 text-sm font-bold text-white transition hover:bg-amber-600 disabled:cursor-not-allowed disabled:opacity-60"
              >
                Send
              </button>
            </div>
          </form>
        </section>
      )}
    </>
  );
}
