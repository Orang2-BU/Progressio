'use client';

import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { useEffect, useRef, useState } from 'react';
import { WorkspaceLayout } from './App.jsx';
import { Button, Icon, JourneyTracker, LoadingState, Notice } from './ui.jsx';
import { loadStudy, loadProgress, sourceHref, submitCheckpoint, completeLesson, summarizeLessonProgress, pickActiveLesson, studyJourneyStatuses } from './study.js';
import { proofHref } from './proof.js';

export default function Study() {
  const query = useSearchParams().toString();
  return <StudyFlow key={query} query={query} />;
}

function StudyFlow({ query }) {
  const [state, setState] = useState({ loading: true });
  const [revision, setRevision] = useState(0);
  const [activeLessonId, setActiveLessonId] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [saving, setSaving] = useState(false);
  const lock = useRef(false);
  const alive = useRef(true);

  useEffect(() => { alive.current = true; return () => { alive.current = false; }; }, []);
  useEffect(() => {
    const controller = new AbortController();
    setState({ loading: true });
    setActiveLessonId(null);
    Promise.all([
      loadStudy(query, { signal: controller.signal }),
      loadProgress({ signal: controller.signal }).then((progress) => ({ progress }))
        .catch((error) => ({ progress: null, progressError: error.message })),
    ]).then(([data, progress]) => {
      if (!controller.signal.aborted) setState({ ...data, ...progress });
    }).catch((error) => {
      if (!controller.signal.aborted) setState({ error: error.message });
    });
    return () => controller.abort();
  }, [query, revision]);

  useEffect(() => {
    if (activeLessonId !== null || !state.lessons?.length) return;
    const initialLesson = pickActiveLesson(state.lessons, state.progress?.completed_lesson_ids ?? null, null);
    if (initialLesson) setActiveLessonId(initialLesson.id);
  }, [activeLessonId, state.lessons, state.progress]);

  async function refreshProgress() {
    setRefreshing(true);
    try {
      const progress = await loadProgress();
      if (alive.current) setState((current) => ({ ...current, progress, progressError: '' }));
    } catch (error) {
      if (alive.current) setState((current) => ({ ...current, progress: null, progressError: error.message }));
    } finally { if (alive.current) setRefreshing(false); }
  }

  async function complete(lessonId) {
    if (lock.current) throw new Error('Completion lain masih diproses.');
    lock.current = true;
    setActiveLessonId(lessonId);
    setSaving(true);
    try {
      const receipt = await completeLesson(lessonId);
      if (alive.current) await refreshProgress();
      return receipt;
    } catch (error) {
      if (alive.current) setState((current) => ({ ...current, progress: null, progressError: 'Completion belum dapat dipastikan. Perbarui progress sebelum mencoba lagi.' }));
      throw error;
    } finally { lock.current = false; if (alive.current) setSaving(false); }
  }

  const params = new URLSearchParams(query);
  params.delete('learn');
  const suffix = params.size ? `?${params}` : '';
  const completion = state.progress ? summarizeLessonProgress(state.lessons, state.progress.completed_lesson_ids) : null;
  const skillProgress = state.progress?.skills.find((skill) => skill.skill === state.skill?.id);
  const activeLesson = pickActiveLesson(state.lessons || [], state.progress?.completed_lesson_ids ?? null, activeLessonId);
  const activeSteps = activeLesson ? state.steps.filter((step) => step.lesson === activeLesson.id) : [];

  return <WorkspaceLayout><section className="workspace-content study-content">
    <nav className="study-breadcrumb" aria-label="Breadcrumb">
      <Link href={`/roadmap${suffix}`}>Roadmap</Link><span aria-hidden="true">/</span>
      <span>{state.target?.title || 'Target'}</span><span aria-hidden="true">/</span>
      <span aria-current="page">Ruang belajar</span>
    </nav>
    <JourneyTracker statuses={studyJourneyStatuses(Boolean(state.target && state.skill))} className="study-journey" />

    {state.loading && <LoadingState>Memuat materi dan progress…</LoadingState>}
    {state.error && <Notice tone="error" title="Materi belum dapat dimuat">
      <p>{state.error}</p><button className="button secondary compact" onClick={() => setRevision((value) => value + 1)}>Coba lagi</button>
    </Notice>}

    {state.skill && <>
      <header className="study-heading">
        <div className="study-heading-copy">
          <p className="eyebrow">04 / RUANG BELAJAR · {state.target.title}</p>
          <h1>{state.skill.title}</h1>
          <p className="intro">Baca materi dari penerbit, ikuti study plan, lalu laporkan aktivitas lesson. Checkpoint memberi feedback sementara; kelulusan skill ditentukan melalui assessment.</p>
          <div className="study-heading-links">
            <Link href={`/roadmap${suffix}`}>Kembali ke roadmap</Link>
            <Link href={proofHref(query, state.skill.id)}>Buka assessment skill</Link>
          </div>
        </div>
        <section className="study-progress-card" aria-labelledby="study-progress-title">
          <div className="study-progress-top"><p id="study-progress-title" className="eyebrow">PROGRES MATERI</p>
            {completion ? <strong>{completion.completed} / {completion.total}</strong> : <strong>Belum diketahui</strong>}</div>
          {completion && <div className="study-progress-track" role="progressbar" aria-label="Materi lesson selesai" aria-valuemin="0" aria-valuemax={completion.total || 1} aria-valuenow={completion.completed}>
            <span style={{ width: `${completion.percentage}%` }} />
          </div>}
          <p>{state.progress ? `${state.progress.total_xp} XP total dari server` : 'Progress server belum tersedia.'}</p>
        </section>
      </header>

      {state.progressError && <Notice tone="warning" title="Status completion belum dapat dipastikan">
        <p>{state.progressError} Progress lesson, XP, dan receipt diperbarui dari server.</p>
        <button className="button secondary compact" disabled={refreshing || saving} onClick={refreshProgress}>{refreshing ? 'Memuat progress…' : 'Coba perbarui progress'}</button>
      </Notice>}

      <div className="study-workspace">
        <aside className="study-materials" aria-labelledby="study-materials-title">
          <div className="study-pane-heading"><div><p className="eyebrow">MATERI SKILL</p><h2 id="study-materials-title">Daftar materi</h2></div>
            <span>{state.lessons.length} lesson</span></div>
          {!state.lessons.length ? <p className="study-empty">Belum ada materi untuk skill ini. Administrator perlu menambahkan sumber dan study plan.</p> :
            <ol className="study-material-list">
              {state.lessons.map((lesson, index) => {
                const isActive = activeLesson?.id === lesson.id;
                const isComplete = state.progress?.completed_lesson_ids.includes(lesson.id);
                return <li key={lesson.id}>
                  <button type="button" className={`study-material-item${isActive ? ' is-active' : ''}`} aria-current={isActive ? 'step' : undefined}
                    onClick={() => setActiveLessonId(lesson.id)}>
                    <span className={`study-material-number${isComplete ? ' is-complete' : ''}`}>{isComplete ? <Icon name="check" size={17}/> : String(index + 1).padStart(2, '0')}</span>
                    <span className="study-material-copy"><span className="study-material-title">{lesson.title}</span>
                      <span className="study-material-meta">{lesson.content_type} · {lesson.duration ? `${lesson.duration} menit` : 'durasi belum dicatat'}</span>
                      <span className="study-material-meta">{isComplete ? 'Selesai tercatat di server' : state.progress ? 'Belum tercatat selesai' : 'Status belum diketahui'}</span>
                    </span><Icon name="arrow" size={17}/>
                  </button>
                </li>;
              })}
            </ol>}
          <p className="study-pane-note">Catatan dan riwayat belum tersedia.</p>
        </aside>

        <section className="study-plan-pane" aria-labelledby="study-plan-title">
          {activeLesson ? <>
            <div className="study-plan-header"><div><p className="eyebrow">STUDY PLAN · {activeLesson.content_type}</p>
              <h2 id="study-plan-title">{activeLesson.title}</h2></div>
              <span className="study-estimate">{activeLesson.duration ? `${activeLesson.duration} menit` : 'Durasi belum dicatat'}</span>
            </div>
            <div className="study-source-card">
              <div><p className="study-source-label">SUMBER BELAJAR</p><h3>{activeLesson.provider || 'Penerbit belum dicatat'}</h3>
                <p>{activeLesson.license ? `Lisensi: ${activeLesson.license}` : 'Lisensi belum dicatat'}</p></div>
              <SourceLink url={activeLesson.content_url} broken={activeLesson.link_status === 'broken'}>Buka materi penerbit</SourceLink>
              {sourceHref(activeLesson.license_url) && <a href={sourceHref(activeLesson.license_url)} target="_blank" rel="noopener noreferrer">Baca ketentuan lisensi</a>}
              <p className="study-source-status">{activeLesson.license_verified ? 'Lisensi ditandai terverifikasi oleh pengelola.' : 'Lisensi belum diverifikasi pengelola.'} {activeLesson.attribution_required ? 'Attribution diperlukan.' : 'Attribution tidak ditandai wajib.'} Status tautan: {activeLesson.link_status || 'belum diperiksa'}.</p>
            </div>

            {activeSteps.length ? <div className="study-plan-content" key={activeLesson.id}>
              {activeSteps.map((step, index) => <article className="study-step-panel" key={step.id}>
                <div className="study-step-panel-heading"><span>LANGKAH {index + 1}</span><span>{step.estimated_minutes} menit</span></div>
                <p className="study-step-prompt">{step.prompt}</p>
                {sourceHref(step.study_url) && activeLesson.link_status !== 'broken' ? <a href={sourceHref(step.study_url)} target="_blank" rel="noopener noreferrer">Buka bagian materi terkait (tab baru)</a> : <p className="study-muted">Tautan bagian materi tidak tersedia atau tercatat broken.</p>}
                {step.checkpoint_question ? <Checkpoint step={step}/> : <p className="study-muted">Belum ada checkpoint pada langkah ini.</p>}
              </article>)}
            </div> : <div className="study-empty"><h3>Study plan belum tersedia</h3><p>Materi penerbit tetap dapat dibuka. Administrator belum menambahkan langkah belajar untuk lesson ini.</p></div>}

            <LessonCompletion key={activeLesson.id} lesson={activeLesson} completed={state.progress ? state.progress.completed_lesson_ids.includes(activeLesson.id) : null}
              disabled={saving || refreshing || !state.progress} onComplete={complete}/>
            {skillProgress && <p className="study-skill-stats">Mastery belajar tersimpan {skillProgress.mastery} / 100 · XP skill {skillProgress.xp}. Ini bukan hasil assessment.</p>}
          </> : <div className="study-empty"><h2 id="study-plan-title">Pilih materi untuk mulai belajar</h2><p>Belum ada lesson yang tersedia pada skill ini.</p></div>}
        </section>
      </div>
    </>}
  </section></WorkspaceLayout>;
}

function SourceLink({ url, broken, children }) {
  const href = sourceHref(url);
  return href && !broken ? <a className="button secondary compact" href={href} target="_blank" rel="noopener noreferrer">{children} (tab baru)</a> : <p className="study-muted">Tautan sumber tidak tersedia, tidak aman, atau terakhir tercatat broken.</p>;
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
    event.preventDefault();
    if (lock.current) return;
    lock.current = true; setBusy(true); setError(null); setFeedback(null);
    try { const result = await submitCheckpoint(step.id, answer); if (alive.current) setFeedback(result); }
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
        onChange={(event) => { setAnswer(event.target.value); setFeedback(null); }}/>
      <p className="hint" id={`study-answer-hint-${step.id}`}>Teks singkat, maksimal 255 karakter. Jawaban dan feedback tidak disimpan saat halaman dimuat ulang.</p>
      {error?.fields?.answer && <p className="field-error" id={`study-answer-error-${step.id}`}>{error.fields.answer}</p>}
    </div>
    <button className="button secondary compact" type="submit" disabled={busy || !answer.trim()}>{busy ? 'Memeriksa…' : 'Periksa jawaban'}</button>
    {feedback && <p className={`study-feedback${feedback.correct ? ' is-correct' : ' is-incorrect'}`} role="status"><strong>{feedback.correct ? 'Jawaban sesuai.' : 'Belum sesuai; coba lagi.'}</strong> {feedback.feedback}</p>}
  </form>;
}
