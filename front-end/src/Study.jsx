'use client';

import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { useEffect, useRef, useState } from 'react';
import { WorkspaceLayout } from './App.jsx';
import { loadStudy, loadProgress, sourceHref, submitCheckpoint, completeLesson } from './study.js';
import { proofHref } from './proof.js';

export default function Study() {
  const query = useSearchParams().toString();
  return <StudyFlow key={query} query={query} />;
}

function StudyFlow({ query }) {
  const [state, setState] = useState({ loading: true });
  const [revision, setRevision] = useState(0);
  const [refreshing, setRefreshing] = useState(false);
  const [saving, setSaving] = useState(false);
  const lock = useRef(false);
  const alive = useRef(true);
  useEffect(() => { alive.current = true; return () => { alive.current = false; }; }, []);
  useEffect(() => {
    const controller = new AbortController(); setState({ loading: true });
    Promise.all([loadStudy(query, { signal: controller.signal }),
      loadProgress({ signal: controller.signal }).then((progress) => ({ progress })).catch((error) => ({ progress: null, progressError: error.message }))])
      .then(([data, progress]) => { if (!controller.signal.aborted) setState({ ...data, ...progress }); })
      .catch((error) => { if (!controller.signal.aborted) setState({ error: error.message }); });
    return () => controller.abort();
  }, [query, revision]);
  async function refreshProgress() {
    setRefreshing(true);
    try {
      const progress = await loadProgress();
      if (alive.current) setState((s) => ({ ...s, progress, progressError: '' }));
    } catch (error) {
      if (alive.current) setState((s) => ({ ...s, progress: null, progressError: error.message }));
    } finally { if (alive.current) setRefreshing(false); }
  }
  async function complete(lessonId) {
    if (lock.current) throw new Error('Completion lain masih diproses.');
    lock.current = true; setSaving(true);
    try {
      const receipt = await completeLesson(lessonId);
      if (alive.current) await refreshProgress();
      return receipt;
    } catch (error) {
      if (alive.current) setState((s) => ({ ...s, progress: null, progressError: 'Completion belum dapat dipastikan. Perbarui progress sebelum mencoba lagi.' }));
      throw error;
    } finally { lock.current = false; if (alive.current) setSaving(false); }
  }
  const params = new URLSearchParams(query); params.delete('learn');
  const suffix = params.size ? `?${params}` : '';
  const skillProgress = state.progress?.skills.find((s) => s.skill === state.skill?.id);
  return <WorkspaceLayout><section className="workspace-content study-content">
    <p className="eyebrow">04 / BELAJAR DENGAN ARAH</p><h1>{state.skill?.title || 'Materi dan study plan'}</h1>
    <p className="intro">Materi tetap di situs penerbit. Progressio memberi arah membaca dan latihan; selesai mempelajari materi bukan bukti lulus assessment atau credential.</p>
    <nav className="profile-actions" aria-label="Navigasi materi"><Link href={`/roadmap${suffix}`}>Kembali ke roadmap</Link><Link href={`/catalog${suffix}`}>Kembali ke target</Link></nav>
    {state.loading && <p role="status">Memuat materi dan progress…</p>}
    {state.error && <div className="error-summary" role="alert"><p>{state.error}</p><button className="button secondary" onClick={() => setRevision((n) => n + 1)}>Coba lagi</button></div>}
    {state.skill && <>
      <section className="profile-card" aria-labelledby="study-progress"><h2 id="study-progress">Aktivitas belajar, bukan evidence</h2>
        <Link className="button primary" href={proofHref(query, state.skill.id)}>Uji skill melalui assessment</Link>
        <p>Target: {state.target.title}. Skill yang dipelajari: {state.skill.title}.</p>
        <p className="hint">Completion adalah laporan aktivitasmu. Backend memberi XP dan dapat menaikkan mastery belajar hingga 70; ini tidak mengukur penguasaan melalui assessment. Checkpoint hanya feedback sementara, tidak tersimpan dan tidak memberi XP/completion.</p>
        {state.progress ? <dl><div><dt>Materi skill ini selesai</dt><dd>{state.lessons.filter((l) => state.progress.completed_lesson_ids.includes(l.id)).length} / {state.lessons.length}</dd></div>
          <div><dt>Mastery skill tersimpan / XP skill</dt><dd>{skillProgress?.mastery ?? 0} / 100 · {skillProgress?.xp ?? 0} XP</dd></div>
          <div><dt>Total XP akun</dt><dd>{state.progress.total_xp}</dd></div><div><dt>Total completion akun</dt><dd>{state.progress.completed_lessons_count}</dd></div></dl> : <p>Progress belum tersedia. Status completion tidak dapat dipastikan.</p>}
        {state.progressError && <p className="error-summary" role="alert">{state.progressError}</p>}
        <button className="button secondary" disabled={saving || refreshing} onClick={refreshProgress}>{refreshing ? 'Memuat progress…' : 'Perbarui progress'}</button>
      </section>
      {!state.lessons.length && <p className="notice" role="status">Belum ada materi untuk skill ini. Administrator perlu menambahkan sumber dan study plan.</p>}
      {state.lessons.map((lesson) => <LessonCard key={lesson.id} lesson={lesson} steps={state.steps.filter((s) => s.lesson === lesson.id)}
        completed={state.progress ? state.progress.completed_lesson_ids.includes(lesson.id) : null} disabled={saving || refreshing} onComplete={complete} />)}
    </>}
  </section></WorkspaceLayout>;
}

function SourceLink({ url, broken, children }) {
  const href = sourceHref(url);
  return href && !broken ? <a className="button secondary" href={href} target="_blank" rel="noopener noreferrer">{children} (tab baru)</a> : <p className="hint">Tautan sumber tidak tersedia, tidak aman, atau terakhir tercatat broken.</p>;
}

function LessonCard({ lesson, steps, completed, disabled, onComplete }) {
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const lock = useRef(false);
  const alive = useRef(true);
  useEffect(() => { alive.current = true; return () => { alive.current = false; }; }, []);
  async function complete() {
    if (lock.current || disabled || completed !== false) return;
    lock.current = true; setBusy(true); setError(''); setMessage('');
    try {
      const receipt = await onComplete(lesson.id);
      if (alive.current) setMessage(`Server mencatat completion. XP diterima: ${receipt.xp_earned}. ${receipt.newly_completed ? 'Aktivitas baru.' : 'Sudah tercatat sebelumnya; bukan reward baru.'}`);
    } catch (issue) { if (alive.current) setError(issue.message); }
    finally { lock.current = false; if (alive.current) setBusy(false); }
  }
  return <section className="profile-card study-lesson" aria-labelledby={`lesson-${lesson.id}`}>
    <p className="eyebrow">{lesson.content_type} / {lesson.duration > 0 ? `${lesson.duration} MENIT` : 'DURASI BELUM DICATAT'}</p><h2 id={`lesson-${lesson.id}`}>{lesson.title}</h2>
    <p>Penerbit: {lesson.provider || 'Belum dicatat'} · Lisensi yang dicatat: {lesson.license || 'Belum dicatat'}</p>
    <p className="hint">{lesson.license_verified ? 'Lisensi ditandai terverifikasi oleh pengelola.' : 'Lisensi belum diverifikasi pengelola; jangan menyalin atau mengunggah ulang materi.'}
      {' '}{lesson.attribution_required ? 'Attribution diperlukan.' : 'Attribution tidak ditandai wajib.'} Status tautan terakhir: {lesson.link_status || 'belum diperiksa'}.</p>
    <div className="profile-actions"><SourceLink url={lesson.content_url} broken={lesson.link_status === 'broken'}>Buka materi di penerbit</SourceLink>
      {sourceHref(lesson.license_url) && <a href={sourceHref(lesson.license_url)} target="_blank" rel="noopener noreferrer">Ketentuan lisensi (tab baru)</a>}</div>
    {steps.length ? steps.map((step, index) => <div className="study-step" key={step.id}><h3>Bagian belajar {index + 1}</h3><p>{step.prompt}</p>
      <p className="hint">Estimasi {step.estimated_minutes} menit.</p><SourceLink url={step.study_url} broken={lesson.link_status === 'broken'}>Buka bagian yang dipelajari</SourceLink>
      {step.checkpoint_question ? <Checkpoint step={step} /> : <p className="hint">Belum ada checkpoint pada langkah ini.</p>}
    </div>) : <p className="notice">Belum ada study plan untuk materi ini. Tautan materi tetap dapat dibuka.</p>}
    <div className="profile-actions"><p className="hint" role="status">{completed === null ? 'Completion belum dapat dipastikan.' : completed ? 'Selesai mempelajari — tercatat di server, bukan assessment lulus.' : 'Belum tercatat selesai mempelajari.'}</p>
      <button className="button primary" disabled={disabled || busy || completed !== false} onClick={complete}>{busy ? 'Mencatat di server…' : completed ? 'Sudah tercatat selesai' : 'Tandai saya selesai mempelajari'}</button></div>
    {message && <p className="notice" role="status">{message}</p>}{error && <p className="error-summary" role="alert">{error}</p>}
  </section>;
}

function Checkpoint({ step }) {
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
    event.preventDefault(); if (lock.current) return;
    lock.current = true; setBusy(true); setError(null); setFeedback(null);
    try { const result = await submitCheckpoint(step.id, answer); if (alive.current) setFeedback(result); }
    catch (issue) { if (alive.current) setError(issue); }
    finally { lock.current = false; if (alive.current) setBusy(false); }
  }
  return <form onSubmit={submit} noValidate aria-busy={busy} className="checkpoint-form">
    <h4>Checkpoint latihan</h4><p>{step.checkpoint_question}</p>
    {error && <div className="error-summary" ref={summary} tabIndex="-1" role="alert"><p>{error.message}</p><a href={`#answer-${step.id}`} onClick={(e) => { e.preventDefault(); document.getElementById(`answer-${step.id}`)?.focus(); }}>Periksa jawaban checkpoint</a></div>}
    <div className="field"><label htmlFor={`answer-${step.id}`}>Jawaban checkpoint</label><input id={`answer-${step.id}`} value={answer} maxLength={255} disabled={busy}
      aria-invalid={Boolean(error?.fields?.answer)} aria-describedby={`answer-hint-${step.id}${error?.fields?.answer ? ` answer-error-${step.id}` : ''}`}
      onChange={(e) => { setAnswer(e.target.value); setFeedback(null); }} />
      <p className="hint" id={`answer-hint-${step.id}`}>Jawaban teks singkat, maksimal 255 karakter. Dinilai oleh server; feedback hilang saat halaman ditutup.</p>
      {error?.fields?.answer && <p className="field-error" id={`answer-error-${step.id}`}>{error.fields.answer}</p>}</div>
    <button className="button secondary" type="submit" disabled={busy}>{busy ? 'Memeriksa…' : 'Periksa jawaban'}</button>
    {feedback && <p className="notice" role="status"><strong>{feedback.correct ? 'Jawaban sesuai.' : 'Belum sesuai; coba lagi.'}</strong> {feedback.feedback}</p>}
  </form>;
}
