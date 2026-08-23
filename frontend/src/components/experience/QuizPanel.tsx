import { useMemo, useState } from "react";
import type { QuizQuestion } from "../../types/experience";
import { useTranslation } from "react-i18next";

export default function QuizPanel({ questions }: { questions: QuizQuestion[] }) {
  const { t } = useTranslation();
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const answered = Object.keys(answers).length;
  const score = useMemo(
    () => questions.filter((question) => answers[question.id] === question.correct_index).length,
    [answers, questions],
  );

  if (questions.length === 0) return null;

  return (
    <section aria-labelledby="quiz-title" className="rounded-lg border border-border bg-surface/40 p-6 sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs tracking-[0.24em] text-gold/80 uppercase">{t("experience.quiz")}</p>
          <h3 id="quiz-title" className="mt-2 font-display text-3xl text-text">{t("experience.whatDiscovered")}</h3>
        </div>
        <p className="rounded-full border border-border px-4 py-2 text-sm text-text-muted">
          {t("experience.score")} {score}/{questions.length}
        </p>
      </div>

      <div className="mt-7 space-y-8">
        {questions.map((question, questionIndex) => {
          const selected = answers[question.id];
          const hasAnswered = selected !== undefined;
          return (
            <fieldset key={question.id}>
              <legend className="text-lg font-medium leading-7 text-text">
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
                      className={`min-h-14 rounded-md border px-5 py-3 text-start text-base transition ${
                        isCorrect
                          ? "border-accent-teal/70 bg-accent-teal/10 text-text"
                          : isSelected
                            ? "border-accent-red/60 bg-accent-red/10 text-text"
                            : "border-border bg-bg/60 text-text-muted hover:border-gold/50 hover:text-text disabled:opacity-60"
                      }`}
                    >
                      {choice}
                    </button>
                  );
                })}
              </div>
              {hasAnswered && (
                <p className="mt-3 text-sm leading-6 text-text-muted" role="status">
                  {selected === question.correct_index ? `${t("experience.correct")}. ` : `${t("experience.incorrect")}. `}
                  {question.explanation}
                </p>
              )}
            </fieldset>
          );
        })}
      </div>

      {answered === questions.length && (
        <div className="mt-8 flex flex-wrap items-center justify-between gap-4 border-t border-border pt-6">
          <p className="text-lg text-text">{t("experience.result", { score, total: questions.length })}</p>
          <button
            type="button"
            onClick={() => setAnswers({})}
            className="min-h-12 rounded-md border border-gold/40 px-5 py-2 text-sm font-medium text-gold hover:bg-gold/10"
          >
            {t("experience.tryAgain")}
          </button>
        </div>
      )}
    </section>
  );
}
