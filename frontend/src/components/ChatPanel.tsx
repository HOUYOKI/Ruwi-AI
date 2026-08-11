import { useState, type FormEvent } from "react";
import { ApiError, askRuwi } from "../api/client";

interface Exchange {
  question: string;
  answer: string;
}

const QUESTION_MAX_LENGTH = 2000;

export default function ChatPanel({ artifactId }: { artifactId: number }) {
  const [question, setQuestion] = useState("");
  const [exchanges, setExchanges] = useState<Exchange[]>([]);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed || pending) return;

    setPending(true);
    setError(null);
    try {
      const { answer } = await askRuwi(artifactId, trimmed);
      setExchanges((prev) => [...prev, { question: trimmed, answer }]);
      setQuestion("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Ruwi couldn't respond. Please try again.");
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="flex flex-col border-t border-neutral-800 pt-6">
      <h2 className="text-xs tracking-[0.2em] text-neutral-500 uppercase">Ask Ruwi</h2>

      {exchanges.length > 0 && (
        <div className="mt-4 flex flex-col gap-4">
          {exchanges.map((exchange, i) => (
            <div key={i} className="flex flex-col gap-1.5">
              <p className="text-sm font-medium text-neutral-200">{exchange.question}</p>
              <p className="text-sm leading-relaxed text-neutral-400">{exchange.answer}</p>
            </div>
          ))}
        </div>
      )}

      {pending && <p className="mt-4 text-sm text-neutral-500">Ruwi is connecting eras…</p>}

      {error && (
        <p className="mt-4 rounded-sm border border-red-900/60 bg-red-950/30 px-3 py-2 text-sm text-red-400">
          {error}
        </p>
      )}

      <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={pending}
          maxLength={QUESTION_MAX_LENGTH}
          placeholder="How does this connect to other civilizations?"
          className="flex-1 rounded-sm border border-neutral-800 bg-neutral-900/60 px-3 py-2 text-sm text-neutral-100 placeholder:text-neutral-600 focus:border-amber-400/50 focus:outline-none disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={pending || !question.trim()}
          className="rounded-sm border border-amber-400/30 bg-amber-400/10 px-4 py-2 text-sm font-medium text-amber-300 transition-colors hover:bg-amber-400/20 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {pending ? "Asking…" : "Ask"}
        </button>
      </form>
    </div>
  );
}
