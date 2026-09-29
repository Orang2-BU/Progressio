'use client';

import Link from 'next/link';
import { useSearchParams, useRouter } from 'next/navigation';
import { useEffect, useRef, useState } from 'react';
import { WorkspaceLayout } from './App.jsx';
import { request } from './api.js';
import { diagnosticTarget, validateQuestions, diagnosticPayload, validateAttempt } from './diagnostic.js';

export default function Diagnostic({ result = false }) {
  const query = useSearchParams().toString();
  // A URL change starts a separate quiz; answers never leak into another target.
  return <DiagnosticFlow key={`${result}:${query}`} query={query} result={result} />;
}

function DiagnosticFlow({ query, result }) {
  const router = useRouter();
  const [state, setState] = useState({ loading: true });
  const [revision, setRevision] = useState(0);
  const [answers, setAnswers] = useState({});
  const [issue, setIssue] = useState(null);
  const [busy, setBusy] = useState(false);
  const [uncertain, setUncertain] = useState(false);
  const lock = useRef(false);
  const alive = useRef(true);
  const summary = useRef(null);
  const suffix = query ? `?${query}` : '';
  useEffect(() => { alive.current = true; return () => { alive.current = false; }; }, []);
  useEffect(() => { if (issue) summary.current?.focus(); }, [issue]);
  useEffect(() => {
    const controller = new AbortController();
    setState({ loading: true });
    (async () => {
      const target = await diagnosticTarget(query, { signal: controller.signal });
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
      if (!controller.signal.aborted) setState({ target, data });
    })().catch((error) => { if (!controller.signal.aborted) setState({ error: error.message }); });
    return () => controller.abort();
  }, [query, result, revision]);
  async function submit(event) {
    event.preventDefault();
    if (lock.current || uncertain) return;
    let body;
    try { body = diagnosticPayload(state.data, answers); }
    catch (error) { setIssue(error); return; }
    lock.current = true; setBusy(true); setIssue(null);
    try {
      const data = await request(`diagnostics/${state.target.track.id}/submit`, { method: 'POST', body });
      validateAttempt(data, state.target.track.id);
      if (alive.current) router.push(`/diagnostic/result${suffix}`);
    } catch (error) {
      if (alive.current) {
        setIssue(error);
        // No idempotency endpoint: a lost response may still have created an attempt.
        setUncertain(!error.status || error.status >= 500 || (error.status >= 200 && error.status < 300));
        setBusy(false);
      }
      lock.current = false;
    }
  }
  const target = state.target;
  const data = state.data;
  const missing = issue?.fields || {};
  return <WorkspaceLayout><section className="workspace-content diagnostic-content">
    <p className="eyebrow">02 / UKUR TITIK AWAL</p><h1>{result ? 'Hasil diagnostic terbaru' : 'Kenali kemampuanmu hari ini.'}</h1>
    <p className="intro">Diagnostic adalah pengukuran awal, bukan credential atau bukti lulus assessment. Penilaian dilakukan oleh server dan tidak memberikan XP.</p>
    <div className="profile-actions"><Link href={`/catalog${suffix}`}>Kembali ke target</Link>
      <Link href={result ? `/diagnostic${suffix}` : `/diagnostic/result${suffix}`}>{result ? 'Mulai attempt baru' : 'Lihat hasil terbaru'}</Link></div>
    {state.loading && <p role="status">Memuat diagnostic…</p>}
    {state.error && <div className="error-summary" role="alert"><p>{state.error}</p><button className="button secondary" onClick={() => setRevision(revision + 1)}>Coba lagi</button></div>}
    {target && <p className="notice">Target: {target.title}. Cakupan diagnostic: seluruh {target.track.title}, bukan hanya skill/competency pilihan.</p>}
    {state.empty && <p role="status">Belum ada hasil untuk career track ini. Mulai attempt baru untuk mengukur titik awal.</p>}
    {!result && data?.length === 0 && <p role="status">Belum ada soal diagnostic untuk career track ini. Pilih target lain atau hubungi administrator.</p>}
    {!result && data?.length > 0 && <form onSubmit={submit} noValidate aria-busy={busy}>
      {issue && <div className="error-summary" role="alert" tabIndex="-1" ref={summary}><strong>{issue.message}</strong>
        <ul>{data.filter((q) => missing[q.id]).map((q) => <li key={q.id}><a href={`#question-${q.id}`} onClick={(e) => { e.preventDefault(); document.getElementById(`question-${q.id}`)?.focus(); }}>Soal {data.indexOf(q) + 1}: {missing[q.id]}</a></li>)}</ul>
        {missing.answers && <p>{missing.answers}</p>}
      </div>}
      <p className="hint">{Object.keys(answers).length} / {data.length} dijawab. Pilih “Belum tahu” jika belum yakin; pilihan ini dinilai salah. Jawaban belum tersimpan sebelum dikirim.</p>
      {data.map((q, index) => <fieldset key={q.id} className="diagnostic-question profile-card" disabled={busy}>
        <legend>{index + 1}. {q.prompt}</legend><p className="hint">Skill: {q.skill_title}</p>
        {[...q.options, { value: '', label: 'Belum tahu' }].map((o, i) => <label className="target-option" key={o.value}>
          <input id={i === 0 ? `question-${q.id}` : undefined} type="radio" name={`question-${q.id}`} value={o.value}
            checked={Object.hasOwn(answers, q.id) && answers[q.id] === o.value} aria-invalid={Boolean(missing[q.id])}
            aria-describedby={missing[q.id] ? `error-${q.id}` : undefined} onChange={() => setAnswers({ ...answers, [q.id]: o.value })} />{o.label}</label>)}
        {missing[q.id] && <p className="field-error" id={`error-${q.id}`}>{missing[q.id]}</p>}
      </fieldset>)}
      {uncertain && <div className="notice" role="status"><p>Pengiriman mungkin sudah tersimpan. Periksa hasil terbaru sebelum membuat attempt lain; jawabanmu tetap ada di halaman ini.</p>
        <Link className="button secondary" href={`/diagnostic/result${suffix}`}>Periksa hasil terbaru</Link>
        <button type="button" className="button secondary" onClick={() => { setUncertain(false); setIssue(null); }}>Saya memilih mengirim attempt baru</button></div>}
      <button type="submit" className="button primary" disabled={busy || uncertain}>{busy ? 'Menilai di server…' : 'Kirim jawaban'}</button>
    </form>}
    {result && data && <div className="profile-card diagnostic-result">
      <p className="eyebrow">HASIL SERVER / ATTEMPT #{data.id}</p><h2>{data.overall_score} / 100</h2>
      <p>Selesai {new Intl.DateTimeFormat('id-ID', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(data.completed_at))}</p>
      <p className="hint">Ini snapshot attempt terbaru. Mastery tersimpan tidak diturunkan oleh attempt yang lebih rendah. Hasil ini belum membuktikan kelayakan credential.</p>
      <h3>Pengukuran per skill</h3><ul className="diagnostic-scores">{data.skill_scores.map((s) => <li key={s.skill_id}><strong>{s.skill_title}</strong><span>{s.score} / 100 · {s.correct_answers}/{s.total_questions} benar</span>
        <small>{data.recommended_skill_ids.includes(s.skill_id) ? 'Prioritas pengembangan menurut server' : 'Tidak masuk rekomendasi pengembangan pada attempt ini'}</small></li>)}</ul>
      <p>Roadmap berdasarkan hasil dan prasyarat akan disambungkan pada fase berikutnya.</p>
      <button className="button secondary" onClick={() => setRevision(revision + 1)}>Muat ulang hasil terbaru</button>
    </div>}
  </section></WorkspaceLayout>;
}
