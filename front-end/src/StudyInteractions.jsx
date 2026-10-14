'use client';

import { useEffect, useRef, useState } from 'react';
import { completeLesson, sourceHref, submitCheckpoint } from './study.js';

export function StudyInteractionBoundary({ lesson, steps, completed, disabled, linkBroken = false, onComplete = completeLesson, onSubmitCheckpoint = submitCheckpoint }) {
  return <>
    {steps.length ? <div className="study-plan-content">
      {steps.map((step, index) => <article className="study-step-panel" key={step.id}>
        <div className="study-step-panel-heading"><span>LANGKAH {index + 1}</span><span>{step.estimated_minutes} menit</span></div>
        <p className="study-step-prompt">{step.prompt}</p>
        {!linkBroken && sourceHref(step.study_url) ? <a href={sourceHref(step.study_url)} target="_blank" rel="noopener noreferrer">Buka bagian materi terkait (tab baru)</a> : <p className="study-muted">Tautan bagian materi tidak tersedia atau tercatat broken.</p>}
        {step.checkpoint_question ? <Checkpoint step={step} onSubmitCheckpoint={onSubmitCheckpoint} /> : <p className="study-muted">Belum ada checkpoint pada langkah ini.</p>}
      </article>)}
    </div> : <div className="study-empty"><h3>Study plan belum tersedia</h3><p>Materi penerbit tetap dapat dibuka. Administrator belum menambahkan langkah belajar untuk lesson ini.</p></div>}
    <LessonCompletion lesson={lesson} completed={completed} disabled={disabled} onComplete={onComplete} />
  </>;
}

function LessonCompletion({ lesson, completed, disabled, onComplete }) {
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const lock = useRef(false);
  const alive = useRef(true);
  useEffect(() => { alive.current = true; return () => { alive.current = false; }; }, []);
  async function submitCompletion() {
    if (lock.current || disabled || completed !== false) return;
    lock.current = true; setBusy(true); setError(''); setMessage('');
    try {
      const receipt = await onComplete(lesson.id);
      if (alive.current) setMessage(`Server mencatat aktivitas lesson. ${receipt.xp_earned} XP pada receipt${receipt.newly_completed ? '.' : '; lesson ini sudah pernah tercatat, tanpa reward baru.'}`);
    } catch (issue) { if (alive.current) setError(issue.message); }
    finally { lock.current = false; if (alive.current) setBusy(false); }
  }
  return <section className="study-completion" aria-labelledby="study-completion-title">
    <div><p className="eyebrow">LAPORAN AKTIVITAS</p><h3 id="study-completion-title">Sudah mempelajari materi ini?</h3>
      <p>{completed === null ? 'Status completion belum dapat dipastikan. Perbarui progress server sebelum mencatat aktivitas.' : completed ? 'Lesson sudah tercatat selesai. Ini laporan aktivitas belajar, bukan kelulusan assessment.' : 'Completion mencatat aktivitas belajar di server. Checkpoint tidak wajib dan tidak menambah XP.'}</p></div>
    <button className="button primary" disabled={disabled || busy || completed !== false} onClick={submitCompletion}>
      {busy ? 'Mencatat di server…' : completed ? 'Lesson sudah tercatat' : 'Tandai lesson selesai'}
    </button>
    {message && <p className="study-receipt" role="status">{message}</p>}{error && <p className="error-summary" role="alert">{error}</p>}
  </section>;
}

function Checkpoint({ step, onSubmitCheckpoint }) {
  const [answer, setAnswer] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);
  const lock = useRef(false);
  const alive = useRef(true);
  const summary = useRef(null);
  useEffect(() => { alive.current = true; return () => { alive.current = false; }; }, []);
  useEffect(() => { if (error) summary.current?.focus(); }, [error]);
  async function submit(event) {
    event.preventDefault();
    if (lock.current) return;
    lock.current = true; setBusy(true); setError(null); setFeedback(null);
    try { const result = await onSubmitCheckpoint(step.id, answer); if (alive.current) setFeedback(result); }
    catch (issue) { if (alive.current) setError(issue); }
    finally { lock.current = false; if (alive.current) setBusy(false); }
  }
  return <form onSubmit={submit} noValidate aria-busy={busy} className="study-checkpoint">
    <div className="study-checkpoint-heading"><span>CHECKPOINT</span><span>Feedback sementara</span></div>
    <h4>{step.checkpoint_question}</h4>
    {error && <div className="error-summary" ref={summary} tabIndex="-1" role="alert"><p>{error.message}</p><a href={`#study-answer-${step.id}`} onClick={(event) => { event.preventDefault(); document.getElementById(`study-answer-${step.id}`)?.focus(); }}>Periksa jawaban checkpoint</a></div>}
    <div className="field"><label htmlFor={`study-answer-${step.id}`}>Jawaban singkat</label>
      <input id={`study-answer-${step.id}`} value={answer} maxLength={255} disabled={busy}
        aria-invalid={Boolean(error?.fields?.answer)} aria-describedby={`study-answer-hint-${step.id}${error?.fields?.answer ? ` study-answer-error-${step.id}` : ''}`}
        onChange={(event) => { setAnswer(event.target.value); setFeedback(null); }} />
      <p className="hint" id={`study-answer-hint-${step.id}`}>Teks singkat, maksimal 255 karakter. Jawaban dan feedback tidak disimpan saat halaman dimuat ulang.</p>
      {error?.fields?.answer && <p className="field-error" id={`study-answer-error-${step.id}`}>{error.fields.answer}</p>}
    </div>
    <button className="button secondary compact" type="submit" disabled={busy || !answer.trim()}>{busy ? 'Memeriksa…' : 'Periksa jawaban'}</button>
    {feedback && <p className={`study-feedback${feedback.correct ? ' is-correct' : ' is-incorrect'}`} role="status"><strong>{feedback.correct ? 'Jawaban sesuai.' : 'Belum sesuai; coba lagi.'}</strong> {feedback.feedback}</p>}
  </form>;
}
