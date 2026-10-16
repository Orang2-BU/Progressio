'use client';

import Link from 'next/link';
import { useSearchParams, useRouter } from 'next/navigation';
import { useEffect, useRef, useState } from 'react';
import { FocusLayout, WorkspaceLayout } from './App.jsx';
import { ProgressBar } from './ui.jsx';
import { request } from './api.js';
import { loadTarget } from './catalog.js';
import { validateQuestions, diagnosticPayload, validateAttempt, isQuestionAnswered, updateQuestionAnswer,
  getAnsweredQuestionCount, findFirstUnansweredQuestion, isUncertainDiagnosticSubmission,
  getDiagnosticFocusTarget, diagnosticRadarGeometry } from './diagnostic.js';

export function DiagnosticLoadState({ state, result, suffix = '', onRetry }) {
  if (state.loading) return <p role="status">Memuat diagnostic…</p>;
  if (state.error) return <div className="error-summary" role="alert"><p>{state.error}</p><button className="button secondary" type="button" onClick={onRetry}>Coba lagi</button></div>;
  if (result && state.empty) return <div className="diagnostic-empty"><h2>Belum ada hasil untuk career track ini</h2><p>Mulai attempt baru untuk mengukur titik awalmu.</p><Link className="button primary" href={`/diagnostic${suffix}`}>Mulai diagnostic</Link></div>;
  if (!result && state.data?.length === 0) return <div className="diagnostic-empty" role="status"><h2>Belum ada soal diagnostic</h2><p>Career track ini belum memiliki soal. Pilih target lain atau hubungi administrator.</p><Link href={`/catalog${suffix}`}>Pilih target lain</Link></div>;
  return null;
}

export function DiagnosticRecovery({ uncertain, suffix, onRetry }) {
  if (!uncertain) return null;
  return <div className="notice" role="status"><p>Pengiriman mungkin sudah tersimpan. Periksa hasil terbaru sebelum membuat attempt lain; jawabanmu tetap ada di halaman ini.</p>
    <Link className="button secondary" href={`/diagnostic/result${suffix}`}>Periksa hasil terbaru</Link>
    <button type="button" className="button secondary" onClick={onRetry}>Saya memilih mengirim attempt baru</button></div>;
}

export function DiagnosticResultView({ data, target, suffix }) {
  const radar = diagnosticRadarGeometry(data.skill_scores);
  const polygon = (points) => points.map(({ x, y }) => `${x},${y}`).join(' ');
  return <div className="diagnostic-result">
    <article className="diagnostic-result-celebration">
      <p className="eyebrow">HASIL SERVER / ATTEMPT #{data.id}</p><h2>Titik awalmu sudah tercatat</h2><p className="diagnostic-overall-score">{data.overall_score}<span> / 100</span></p>
      <p>Selesai {new Intl.DateTimeFormat('id-ID', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(data.completed_at))}</p>
      <p className="hint">Ini ringkasan attempt terbaru, bukan reward atau hasil credential. Mastery tersimpan tidak diturunkan oleh attempt yang lebih rendah.</p>
    </article>
    <section className="diagnostic-skill-map" aria-labelledby="diagnostic-skill-title">
      <div className="diagnostic-result-heading"><div><p className="eyebrow">PETA SKILL</p><h2 id="diagnostic-skill-title">Pengukuran per skill</h2></div><p className="hint">Sumber: hasil attempt terbaru</p></div>
      <p className="sr-only">Ringkasan grafik skor per skill juga tersedia sebagai daftar di bawah.</p>
      <div className="diagnostic-score-layout">
      {radar && <figure className="diagnostic-radar">
        <svg viewBox="0 0 200 200" role="img" aria-label={`Peta radar skor untuk ${data.skill_scores.length} skill. Nomor sumbu cocok dengan nomor pada daftar.`}>
          <title>Peta skor diagnostic per skill</title>
          {radar.rings.map((ring, index) => <polygon key={index} points={polygon(ring)} fill="none" stroke="var(--line)" strokeWidth="1" />)}
          {radar.axes.map((axis, index) => <line key={index} x1="100" y1="100" x2={axis.x} y2={axis.y} stroke="var(--line)" strokeWidth="1" />)}
          <polygon points={polygon(radar.values)} fill="var(--selected)" fillOpacity=".7" stroke="var(--selected-line)" strokeWidth="2" />
          {radar.values.map((value, index) => <g key={index}>
            <circle cx={value.x} cy={value.y} r="3.5" fill="var(--selected-line)" />
            <text x={radar.labels[index].x} y={radar.labels[index].y} textAnchor={radar.labels[index].x < 88 ? 'end' : radar.labels[index].x > 112 ? 'start' : 'middle'} dominantBaseline="middle">{index + 1}</text>
          </g>)}
        </svg>
        <figcaption>Skala 0–100 · nomor sesuai urutan daftar</figcaption>
      </figure>}
      <ul className="diagnostic-scores">{data.skill_scores.map((skill, index) => {
        const isRecommended = data.recommended_skill_ids.includes(skill.skill_id);
        return <li key={skill.skill_id}>
          <div className="diagnostic-skill-heading"><strong><span className="diagnostic-skill-index" aria-hidden="true">{String(index + 1).padStart(2, '0')}</span>{skill.skill_title}</strong><span>{isRecommended ? 'Prioritas pengembangan' : 'Tidak direkomendasikan pada attempt ini'}</span></div>
          <div className="diagnostic-score-bar" role="progressbar" aria-label={`Skor ${skill.skill_title}`} aria-valuemin="0" aria-valuemax="100" aria-valuenow={skill.score} aria-valuetext={`${skill.score} dari 100`}><span style={{ width: `${skill.score}%` }} /></div>
          <p>{skill.score} / 100</p>
        </li>;
      })}</ul>
      </div>
    </section>
    <p className="notice">Cakupan: seluruh career track {target?.track.title || ''}. Rekomendasi skill berasal dari server. Roadmap memakai mastery tersimpan dan prasyarat; skor attempt ini tidak mengubah mastery secara otomatis.</p>
    <div className="diagnostic-result-actions"><Link className="button primary" href={`/roadmap${suffix}`}>Lihat roadmap target</Link><Link className="button secondary" href={`/diagnostic${suffix}`}>Ulangi diagnostic</Link></div>
  </div>;
}

export default function Diagnostic({ result = false }) {
  const query = useSearchParams().toString();
  return <DiagnosticFlow key={`${result}:${query}`} query={query} result={result} />;
}

function DiagnosticFlow({ query, result }) {
  const router = useRouter();
  const [state, setState] = useState({ loading: true });
  const [revision, setRevision] = useState(0);
  const [answers, setAnswers] = useState({});
  const [questionIndex, setQuestionIndex] = useState(0);
  const [issue, setIssue] = useState(null);
  const [busy, setBusy] = useState(false);
  const [uncertain, setUncertain] = useState(false);
  const [confirmExit, setConfirmExit] = useState(false);
  const lock = useRef(false);
  const alive = useRef(true);
  const summary = useRef(null);
  const questionPrompt = useRef(null);
  const pendingQuestionFocus = useRef(null);
  const exitConfirmation = useRef(null);
  const exitDialogTrigger = useRef(null);
  const exitDialogWasOpen = useRef(false);
  const submitController = useRef(null);
  const suffix = query ? `?${query}` : '';
  const target = state.target;
  const data = state.data;
  const currentQuestion = data?.[questionIndex];

  useEffect(() => {
    alive.current = true;
    return () => {
      alive.current = false;
      submitController.current?.abort();
    };
  }, []);
  useEffect(() => {
    const focusTarget = getDiagnosticFocusTarget({ promptFocusRequested: pendingQuestionFocus.current, issue });
    if (focusTarget === 'prompt') {
      questionPrompt.current?.focus();
      pendingQuestionFocus.current = null;
    } else if (focusTarget === 'summary') summary.current?.focus();
  }, [issue, questionIndex, data]);
  useEffect(() => {
    if (!confirmExit) return undefined;
    exitDialogWasOpen.current = true;
    exitConfirmation.current?.focus();
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') setConfirmExit(false);
      if (event.key === 'Tab') {
        const controls = exitConfirmation.current?.querySelectorAll('button:not(:disabled)');
        if (!controls?.length) return;
        const first = controls[0];
        const last = controls[controls.length - 1];
        if (event.shiftKey && (document.activeElement === first || document.activeElement === exitConfirmation.current)) { event.preventDefault(); last.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [confirmExit]);
  useEffect(() => {
    if (!confirmExit && exitDialogWasOpen.current) {
      exitDialogWasOpen.current = false;
      exitDialogTrigger.current?.focus();
    }
  }, [confirmExit]);
  useEffect(() => {
    const controller = new AbortController();
    setState({ loading: true });
    (async () => {
      const target = await loadTarget(query, { signal: controller.signal });
      let data;
      try {
        data = await request(result ? `diagnostics/latest?career_track=${target.track.id}` : `diagnostics/${target.track.id}`, { signal: controller.signal });
      } catch (error) {
        if (result && error.status === 404) {
          if (!controller.signal.aborted) setState({ target, empty: true });
          return;
        }
        throw error;
      }
      data = result ? validateAttempt(data, target.track.id) : validateQuestions(data);
      if (!controller.signal.aborted) {
        pendingQuestionFocus.current = true;
        setState({ target, data });
      }
    })().catch((error) => { if (!controller.signal.aborted) setState({ error: error.message }); });
    return () => controller.abort();
  }, [query, result, revision]);

  function navigateToQuestion(index) {
    pendingQuestionFocus.current = true;
    setQuestionIndex(index);
    setIssue(null);
  }

  async function submit(event) {
    event.preventDefault();
    if (lock.current || uncertain) return;
    const missingQuestionIndex = findFirstUnansweredQuestion(state.data, answers);
    if (missingQuestionIndex >= 0) {
      pendingQuestionFocus.current = true;
      setIssue({ message: 'Jawab semua soal, atau pilih Belum tahu.', fields: Object.fromEntries(state.data
        .filter((question) => !isQuestionAnswered(answers, question.id))
        .map((question) => [question.id, 'Pilih satu jawaban.'])) });
      setQuestionIndex(missingQuestionIndex);
      return;
    }
    if (questionIndex !== state.data.length - 1) {
      setQuestionIndex(state.data.length - 1);
      return;
    }
    let body;
    try { body = diagnosticPayload(state.data, answers); }
    catch (error) { setIssue(error); return; }
    lock.current = true;
    setBusy(true);
    setIssue(null);
    const controller = new AbortController();
    submitController.current = controller;
    try {
      const data = await request(`diagnostics/${state.target.track.id}/submit`, { method: 'POST', body, signal: controller.signal });
      validateAttempt(data, state.target.track.id);
      if (alive.current && !controller.signal.aborted) router.push(`/diagnostic/result${suffix}`);
    } catch (error) {
      if (alive.current && !controller.signal.aborted) {
        setIssue(error);
        setUncertain(isUncertainDiagnosticSubmission(error));
        setBusy(false);
      }
      lock.current = false;
    } finally {
      if (submitController.current === controller) submitController.current = null;
    }
  }

  function requestExit() {
    if (Object.keys(answers).length) {
      exitDialogTrigger.current = document.activeElement;
      setConfirmExit(true);
    }
    else router.push(`/catalog${suffix}`);
  }

  const answeredCount = !result && data ? getAnsweredQuestionCount(data, answers) : 0;
  const missing = issue?.fields || {};
  const Shell = result ? WorkspaceLayout : FocusLayout;
  const shellProps = result ? {} : { onRequestExit: requestExit, completed: answeredCount, total: data?.length || 0 };

  return <Shell {...shellProps}>
    {!result && confirmExit && <div className="diagnostic-exit-backdrop">
      <section className="diagnostic-exit-dialog" role="alertdialog" aria-modal="true" aria-labelledby="diagnostic-exit-title" aria-describedby="diagnostic-exit-copy" tabIndex="-1" ref={exitConfirmation}>
        <h2 id="diagnostic-exit-title">Keluar dari diagnostic?</h2>
        <p id="diagnostic-exit-copy">Jawaban yang sudah kamu pilih belum dikirim dan akan hilang jika keluar.</p>
        <div className="diagnostic-exit-actions"><button type="button" className="button secondary" onClick={() => setConfirmExit(false)}>Lanjut menjawab</button>
          <button type="button" className="button primary" onClick={() => router.push(`/catalog${suffix}`)}>Keluar</button></div>
      </section>
    </div>}
    <section className={`workspace-content diagnostic-content${result ? ' diagnostic-result-page' : ' diagnostic-focus-page'}`}>
      {result && <>
        <p className="eyebrow">02 / UKUR TITIK AWAL</p><h1>Hasil diagnostic terbaru</h1>
        <p className="intro">Penilaian seluruh career track ini berasal dari server. Diagnostic mengukur titik awal; hasil ini tidak memberikan XP, credential, atau bukti kelulusan.</p>
        <div className="profile-actions"><Link href={`/catalog${suffix}`}>Kembali ke target</Link><Link href={`/diagnostic${suffix}`}>Ulangi diagnostic</Link></div>
      </>}
      <DiagnosticLoadState state={state} result={result} suffix={suffix} onRetry={() => setRevision(revision + 1)} />
      {target && <p className="notice">Target: {target.title}. Cakupan diagnostic: seluruh career track {target.track.title}, bukan hanya skill atau competency pilihan.</p>}
      {!result && currentQuestion && <form className="diagnostic-quiz" onSubmit={submit} noValidate aria-busy={busy}>
        <div className="diagnostic-question-toolbar">
          <div><p className="eyebrow">02 / UKUR TITIK AWAL</p><p className="diagnostic-question-count">Soal {questionIndex + 1} dari {data.length}</p></div>
          <nav aria-label="Navigasi soal" className="diagnostic-navigator"><span className="eyebrow">NAVIGASI SOAL</span><ol>
            {data.map((question, index) => {
              const isAnswered = isQuestionAnswered(answers, question.id);
              const isCurrent = index === questionIndex;
              return <li key={question.id}><button type="button" className="diagnostic-nav-button" aria-label={`Soal ${index + 1}, ${isCurrent ? 'sedang dikerjakan' : isAnswered ? 'dijawab' : 'belum dijawab'}`} aria-current={isCurrent ? 'step' : undefined} onClick={() => navigateToQuestion(index)}>
                {isAnswered ? <span aria-hidden="true">✓</span> : index + 1}</button></li>;
            })}
          </ol></nav>
        </div>
        {issue && <div className="error-summary" role="alert" tabIndex="-1" ref={summary}><strong>{issue.message}</strong>
          {data.some((question) => missing[question.id]) && <ul>{data.filter((question) => missing[question.id]).map((question) => {
            const index = data.indexOf(question);
            return <li key={question.id}><button type="button" onClick={() => navigateToQuestion(index)}>{`Soal ${index + 1}: ${missing[question.id]}`}</button></li>;
          })}</ul>}{missing.answers && <p>{missing.answers}</p>}
        </div>}
        <p className="hint diagnostic-answer-count">{answeredCount} dari {data.length} soal sudah diisi. “Belum tahu” dikirim sebagai jawaban kosong dan dinilai salah oleh server.</p>
        <fieldset className="diagnostic-question-card" disabled={busy} aria-describedby={missing[currentQuestion.id] ? `error-${currentQuestion.id}` : undefined}>
          <legend className="sr-only">{currentQuestion.prompt}</legend>
          <p className="diagnostic-skill-label">Skill · {currentQuestion.skill_title}</p>
          <h1 ref={questionPrompt} tabIndex="-1">{currentQuestion.prompt}</h1>
          <div className="diagnostic-answer-options">
            {[...currentQuestion.options, { value: '', label: 'Belum tahu' }].map((option, index) => (
              <label className="diagnostic-answer-card" key={`${option.value}-${index}`}>
                <input id={index === 0 ? `answer-${currentQuestion.id}` : undefined} type="radio" name={`question-${currentQuestion.id}`} value={option.value}
                  checked={isQuestionAnswered(answers, currentQuestion.id) && answers[currentQuestion.id] === option.value}
                  aria-invalid={Boolean(missing[currentQuestion.id])} aria-describedby={missing[currentQuestion.id] ? `error-${currentQuestion.id}` : undefined}
                  onChange={() => { setAnswers((previous) => updateQuestionAnswer(previous, currentQuestion.id, option.value)); setIssue(null); }} />
                <span className="diagnostic-answer-index" aria-hidden="true">{index < 26 ? String.fromCharCode(65 + index) : '•'}</span><span>{option.label}</span>
              </label>))}
          </div>
          {missing[currentQuestion.id] && <p className="field-error" id={`error-${currentQuestion.id}`}>{missing[currentQuestion.id]}</p>}
        </fieldset>
        <DiagnosticRecovery uncertain={uncertain} suffix={suffix} onRetry={() => { setUncertain(false); setIssue(null); }} />
        <div className="focus-actions diagnostic-question-actions">
          <button type="button" className="button secondary" onClick={() => questionIndex > 0 ? navigateToQuestion(questionIndex - 1) : requestExit()}>{questionIndex > 0 ? 'Sebelumnya' : 'Keluar'}</button>
          <button type="button" className="button secondary" disabled={busy} onClick={() => { setAnswers((previous) => updateQuestionAnswer(previous, currentQuestion.id, '')); if (questionIndex < data.length - 1) navigateToQuestion(questionIndex + 1); }}>{questionIndex === data.length - 1 ? 'Tandai belum tahu' : 'Belum tahu'}</button>
          {questionIndex < data.length - 1
            ? <button type="button" className="button primary" disabled={busy} onClick={() => navigateToQuestion(questionIndex + 1)}>Lanjut</button>
            : <button type="submit" className="button primary" disabled={busy || uncertain}>{busy ? 'Menilai di server…' : 'Kirim jawaban'}</button>}
        </div>
      </form>}
      {result && data && <DiagnosticResultView data={data} target={target} suffix={suffix} />}
    </section>
  </Shell>;
}
