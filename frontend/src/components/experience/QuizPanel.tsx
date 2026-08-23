import { useMemo, useState } from "react";
import type { QuizQuestion } from "../../types/experience";

export default function QuizPanel({ questions }: { questions: QuizQuestion[] }) {
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const answered = Object.keys(answers).length;
  const score = useMemo(
    () => questions.filter((question) => answers[question.id] === question.correct_index).length,
    [answers, questions],
  );

  if (questions.length === 0) return null;

  return (
    <section aria-labelledby="quiz-title" className="rounded-lg border border-neutral-800 bg-neutral-900/40 p-6 sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs tracking-[0.24em] text-amber-400/80 uppercase">Test your eye</p>
          <h3 id="quiz-title" className="mt-2 font-serif text-3xl text-neutral-50">What did you discover?</h3>
        </div>
        <p className="rounded-full border border-neutral-700 px-4 py-2 text-sm text-neutral-300">
          Score {score}/{questions.length}
        </p>
      </div>

      <div className="mt-7 space-y-8">
        {questions.map((question, questionIndex) => {
          const selected = answers[question.id];
          const hasAnswered = selected !== undefined;
          return (
            <fieldset key={question.id}>
              <legend className="text-lg font-medium leading-7 text-neutral-100">
                {questionIndex + 1}. {question.prompt}
              </legend>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                {question.choices.map((choice, choiceIndex) => {
                  const isSelected = selected === choiceIndex;
                  const isCorrect = hasAnswered && choiceIndex === question.correct_index;
                  return (
                    <button
                      key={choice}
                      type="button"
                      disabled={hasAnswered}
                      onClick={() => setAnswers((current) => ({ ...current, [question.id]: choiceIndex }))}
                      className={`min-h-14 rounded-md border px-5 py-3 text-left text-base transition ${
                        isCorrect
                          ? "border-emerald-500/70 bg-emerald-500/10 text-emerald-200"
                          : isSelected
                            ? "border-red-500/60 bg-red-500/10 text-red-200"
                            : "border-neutral-700 bg-neutral-950/60 text-neutral-300 hover:border-amber-400/50 hover:text-neutral-50 disabled:opacity-60"
                      }`}
                    >
                      {choice}
                    </button>
                  );
                })}
              </div>
              {hasAnswered && (
                <p className="mt-3 text-sm leading-6 text-neutral-400" role="status">
                  {selected === question.correct_index ? "Correct. " : "Not quite. "}
                  {question.explanation}
                </p>
              )}
            </fieldset>
          );
        })}
      </div>

      {answered === questions.length && (
        <div className="mt-8 flex flex-wrap items-center justify-between gap-4 border-t border-neutral-800 pt-6">
          <p className="text-lg text-neutral-100">You found {score} of {questions.length} answers.</p>
          <button
            type="button"
            onClick={() => setAnswers({})}
            className="min-h-12 rounded-md border border-amber-400/40 px-5 py-2 text-sm font-medium text-amber-200 hover:bg-amber-400/10"
          >
            Try again
          </button>
        </div>
      )}
    </section>
  );
}
