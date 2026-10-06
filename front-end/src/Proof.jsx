'use client';

import Link from 'next/link';
import { useSearchParams, useRouter } from 'next/navigation';
import { useEffect, useRef, useState } from 'react';
import { WorkspaceLayout } from './App.jsx';
import { request } from './api.js';
import { loadAssessments, assessmentPayload, submitAssessment, recoverSubmission, loadCredentials, loadVerification, proofHref, resultLabel } from './proof.js';
import { sourceHref } from './study.js';

export default function Proof({ mode = 'assessment', credentialId }) {
  const query = useSearchParams().toString();
  return <ProofFlow key={`${mode}-${credentialId}-${query}`} mode={mode} query={query} credentialId={credentialId} />;
}

function ErrorSummary({ issue, links = {} }) {
  const ref = useRef(null);
  useEffect(() => { if (issue) ref.current?.focus(); }, [issue]);
  return issue ? <div className="error-summary" role="alert" tabIndex="-1" ref={ref}><p>{issue.message}</p>
    {Object.entries(issue.fields || {}).filter(([key]) => links[key]).map(([key, message]) => <p key={key}><a href={`#${links[key]}`} onClick={(e) => { e.preventDefault(); document.getElementById(links[key])?.focus(); }}>{message}</a></p>)}</div> : null;
}

function ProofFlow({ mode, query, credentialId }) {
  const [state, setState] = useState({ loading: true });
  const [revision, setRevision] = useState(0);
  const [busy, setBusy] = useState(false);
  const [issue, setIssue] = useState(null);
  const lock = useRef(false); const alive = useRef(true); const router = useRouter();
  useEffect(() => { alive.current = true; return () => { alive.current = false; }; }, []);
  useEffect(() => {
    const controller = new AbortController(); setState({ loading: true });
    const options = { signal: controller.signal };
    (mode === 'verify' ? loadVerification(credentialId, options) : mode === 'credentials' ? loadCredentials(query, options) : loadAssessments(query, options))
      .then((data) => { if (!controller.signal.aborted) setState({ data }); })
      .catch((error) => { if (!controller.signal.aborted) setState({ error }); });
    return () => controller.abort();
  }, [mode, query, credentialId, revision]);
  async function issueCredential() {
    if (lock.current) return; lock.current = true; setBusy(true); setIssue(null);
    try {
      const e = state.data.eligibility;
      const detail = await request('credentials/issue', { method: 'POST', body: { competency_id: e.competency, demo: !e.eligible } });
      if (alive.current) router.push(`/credentials?claim=${e.competency}&id=${detail.id}`);
    } catch (error) { if (alive.current) setIssue(error); }
    finally { lock.current = false; if (alive.current) setBusy(false); }
  }
  const data = state.data;
  const p = new URLSearchParams(query); p.delete('exam'); p.delete('submission');
  const Wrapper = mode === 'verify' ? 'div' : WorkspaceLayout;
  return <Wrapper><section className="workspace-content study-content">
    <p className="eyebrow">05 / KEMAJUAN MENJADI BUKTI</p><h1>{mode === 'verify' ? 'Verifikasi credential' : mode === 'credentials' ? 'Credential dan evidence' : 'Assessment kompetensi'}</h1>
    <p className="intro">Kurikulum adalah standar penilaian. Diagnostic dan selesai membaca bukan kelulusan assessment; mock dan standar draft bukan bukti final.</p>
    {mode !== 'verify' && <nav className="profile-actions" aria-label="Navigasi evidence"><Link href="/catalog">Pilih target</Link><Link href="/credentials">Credential saya</Link>
      {mode === 'assessment' && <Link href={`/study?${p}`}>Kembali ke materi</Link>}</nav>}
    {state.loading && <p role="status">Memuat data server…</p>}
    {state.error && <><ErrorSummary issue={state.error} /><button className="button secondary" onClick={() => setRevision((n) => n + 1)}>Coba lagi</button></>}
    {mode === 'assessment' && data && <>
      <p>Skill: {data.skill.title} · Target: {data.target.title}</p>
      <ul>{(data.skill.learning_outcomes || []).map((outcome, i) => <li key={i}>{outcome}</li>)}</ul>
      <Link href={`/credentials?claim=${data.competency.id}`}>Lihat kebutuhan credential competency ini</Link>
      {!data.assessments.length && <p className="notice">Belum ada assessment untuk skill ini.</p>}
      <div className="profile-actions">{data.assessments.map((a) => { const params = new URLSearchParams(p); params.set('exam', a.id); return <Link key={a.id} className="button secondary" href={`/assessment?${params}`}>{a.title}</Link>; })}</div>
      {data.assessment && <>
        <section className="profile-card"><h2>{data.assessment.title}</h2><p>{data.assessment.instructions}</p><h3>Standar yang diukur</h3><p>{data.assessment.objective}</p><p>{data.assessment.mastery_criteria}</p>
          <ul>{data.assessment.expected_evidence.map((text, i) => <li key={i}>{text}</li>)}</ul>
          <ul>{(data.assessment.rubric || []).map((r, i) => <li key={i}>{r.criterion} · Bobot {r.weight}</li>)}</ul>
          <p>Ambang lulus: {data.assessment.passing_score} / {data.assessment.max_score}. Review: {data.assessment.review_status}. Mode: {data.assessment.evaluation_mode}.</p>
          <p className="hint">URL evidence tidak diunduh/dijalankan. Penilai AI hanya menerima isi teks/kode yang kamu kirim; hasil mock bukan evaluasi nyata.</p>
        </section>
        {data.result ? <Result result={data.result} /> : <AssessmentForm assessment={data.assessment} query={query} />}
        <section className="profile-card"><h2>Hasil tersimpan</h2>{!data.submissions.length && <p>Belum ada submission untuk assessment ini.</p>}
          <ul>{data.submissions.map((s) => { const params = new URLSearchParams(query); params.set('submission', s.id); return <li key={s.id}><Link href={`/assessment?${params}`}>Attempt #{s.id} · {s.status} · {s.score ?? 'belum dinilai'}</Link></li>; })}</ul>
          <button className="button secondary" onClick={() => setRevision((n) => n + 1)}>Perbarui riwayat</button>
          {data.result && <Link className="button secondary" href={`/assessment?${new URLSearchParams([...new URLSearchParams(query)].filter(([key]) => key !== 'submission'))}`}>Buat attempt baru</Link>}
        </section>
      </>}
    </>}
    {mode === 'credentials' && data && <>
      {data.eligibility && <section className="profile-card"><h2>Kelayakan dari evidence server</h2><p>{data.eligibility.reason}</p><p>Skor assessment competency: {data.eligibility.score} / 100. Versi: {data.eligibility.curriculum_version || 'belum dicatat'} · Standar: {data.eligibility.curriculum_status} · Proof provider: {data.eligibility.proof_provider}</p>
        <ul>{data.eligibility.missing_skills.map((s) => <li key={s.id}>Evidence lulus belum tersedia: {s.title}{data.eligibility.career_track && <p><Link href={proofHref(`track=${data.eligibility.career_track}`, s.id)}>Uji {s.title}</Link></p>}</li>)}</ul>
        <ErrorSummary issue={issue} />{issue && <p className="hint">Periksa daftar/detail sebelum mengirim ulang. Request yang sama mengembalikan credential yang sama selama evidence dan versi tidak berubah.</p>}
        <button className="button primary" disabled={busy || (!data.eligibility.eligible && !data.eligibility.demo_ready)} onClick={issueCredential}>{busy ? 'Memproses…' : data.eligibility.eligible ? 'Terbitkan credential final' : 'Buat draft demo — bukan credential valid'}</button>
      </section>}
      {data.detail && <CredentialView data={data.detail} />}
      <section className="profile-card"><h2>Credential akun ini</h2>{!data.list.results.length && <p>Belum ada credential.</p>}
        <ul>{data.list.results.map((c) => <li key={c.id}><Link href={`/credentials?id=${c.id}`}>{c.competency_title} · {c.status}</Link></li>)}</ul>
        <nav className="profile-actions" aria-label="Halaman credential">{data.page > 1 && <Link href={`/credentials?page=${data.page - 1}`}>Sebelumnya</Link>}{data.list.next && <Link href={`/credentials?page=${data.page + 1}`}>Berikutnya</Link>}</nav>
        <button className="button secondary" onClick={() => setRevision((n) => n + 1)}>Perbarui credential</button>
      </section>
    </>}
    {mode === 'verify' && data && <CredentialView data={data} publicView />}
  </section></Wrapper>;
}

function AssessmentForm({ assessment: a, query }) {
  const [answers, setAnswers] = useState({}); const [evidence, setEvidence] = useState({ text: '', github_url: '', demo_url: '' });
  const [busy, setBusy] = useState(false); const [issue, setIssue] = useState(null); const [pending, setPending] = useState(null); const [notice, setNotice] = useState('');
  const lock = useRef(false); const alive = useRef(true); const router = useRouter();
  useEffect(() => { alive.current = true; return () => { alive.current = false; }; }, []);
  function show(s) { const p = new URLSearchParams(query); p.set('submission', s.id); router.push(`/assessment?${p}`); }
  async function submit(event) {
    event.preventDefault(); if (lock.current) return; lock.current = true; setBusy(true); setIssue(null);
    let body;
    try {
      body = pending || assessmentPayload(a, answers, evidence, crypto.randomUUID());
      setPending(body); const s = await submitAssessment(a, body); if (alive.current) show(s);
    } catch (error) { if (alive.current) { setIssue(error); if (!body || [400, 401, 403].includes(error.status)) setPending(null); } }
    finally { lock.current = false; if (alive.current) setBusy(false); }
  }
  async function recover() {
    if (lock.current || !pending) return; lock.current = true; setBusy(true); setIssue(null);
    try { const s = await recoverSubmission(a, pending.request_id); if (alive.current) { if (s) show(s); else setNotice('Belum ditemukan. Kirim ulang payload yang sama dengan request ID yang sama; jangan ubah isian untuk recovery.'); } }
    catch (error) { if (alive.current) setIssue(error); }
    finally { lock.current = false; if (alive.current) setBusy(false); }
  }
  const links = Object.fromEntries(a.questions.map((q, i) => [q.id, `exam-question-${i}`]));
  for (const key of ['text', 'github_url', 'demo_url']) links[key] = `evidence-${key}`;
  return <form onSubmit={submit} noValidate aria-busy={busy} className="checkpoint-form">
    <h2>Kirim evidence</h2><ErrorSummary issue={issue} links={links} />
    <fieldset disabled={busy || Boolean(pending)}>
      {a.evaluation_mode === 'rules' ? a.questions.map((q, i) => <fieldset key={q.id} className="diagnostic-question profile-card"><legend>{i + 1}. {q.prompt}</legend>
        {q.options.map((o, n) => <label key={o.value} className="target-option"><input id={n === 0 ? links[q.id] : undefined} type="radio" name={`exam-${i}`} checked={answers[q.id] === o.value}
          aria-invalid={Boolean(issue?.fields?.[q.id])} aria-describedby={issue?.fields?.[q.id] ? `exam-error-${i}` : undefined} onChange={() => setAnswers({ ...answers, [q.id]: o.value })} />{o.label}</label>)}
        {issue?.fields?.[q.id] && <p className="field-error" id={`exam-error-${i}`}>{issue.fields[q.id]}</p>}
      </fieldset>) : ['text', 'github_url', 'demo_url'].map((key) => <div className="field" key={key}><label htmlFor={links[key]}>{key === 'text' ? 'Isi evidence / kode (wajib)' : `${key} (opsional)`}</label>
        {key === 'text' ? <textarea id={links[key]} rows="12" value={evidence[key]} maxLength={190000} aria-invalid={Boolean(issue?.fields?.[key])} aria-describedby={`${links[key]}-hint`} onChange={(e) => setEvidence({ ...evidence, [key]: e.target.value })} /> :
          <input id={links[key]} value={evidence[key]} maxLength={500} type="url" aria-invalid={Boolean(issue?.fields?.[key])} aria-describedby={`${links[key]}-hint`} onChange={(e) => setEvidence({ ...evidence, [key]: e.target.value })} />}
        <p id={`${links[key]}-hint`} className={issue?.fields?.[key] ? 'field-error' : 'hint'}>{issue?.fields?.[key] || (key === 'text' ? 'Maksimal 200 KB. Jangan kirim secret atau data pribadi. Tidak dijalankan sebagai kode.' : 'HTTP(S); hanya tautan pendukung.')}</p></div>)}
    </fieldset>
    {pending && <div className="notice" role="status"><p>Request ID: {pending.request_id}. Isian dikunci untuk mencegah perubahan payload saat recovery. Reload menghapus isian; hasil yang tersimpan tetap ada di riwayat.</p><button type="button" className="button secondary" disabled={busy} onClick={recover}>Periksa hasil request ini</button></div>}
    {notice && <p role="status">{notice}</p>}
    <button type="submit" className="button primary" disabled={busy || (a.evaluation_mode === 'rules' && !a.questions.length)}>{busy ? 'Menilai di server…' : pending ? 'Kirim ulang request yang sama' : 'Kirim untuk dinilai'}</button>
  </form>;
}

function Result({ result: s }) {
  const { heading, label } = resultLabel(s);
  return <section className="profile-card"><h2>Attempt #{s.id}: {heading}</h2>
    <p>Skor: {s.score ?? 'belum tersedia'} / {s.evaluation.max_score ?? 'tidak dicatat'}</p>{label && <p className="notice" role="status">{label}</p>}<p>{s.feedback}</p>
    <p>Penilai: {s.evaluation.provider || 'provenance lama tidak dicatat'} · Review: {s.evaluation.review_status || 'tidak dicatat'} · Versi: {s.evaluation.curriculum_version || 'tidak dicatat'}</p>
    <p className="hint">Skor dan kelulusan berasal dari server. Lulus mock/draft bukan evidence final. XP hanya untuk submission lulus; recovery request yang sama tidak memberikan reward baru.</p>
  </section>;
}

function CredentialView({ data: c, publicView = false }) {
  const standard = publicView ? c.standard : c.metadata; const credentialId = c.id || c.credential_id;
  const final = c.is_valid && c.status === 'issued' && standard.mode === 'final' && standard.proof_provider === 'http';
  return <section className="profile-card"><h2>{c.competency_title}</h2><p role="status">{final ? 'Credential final terverifikasi' : c.status === 'revoked' ? 'Credential dicabut' : 'Bukan credential final terverifikasi'}</p>
    <p>Pemilik: {c.student_name || c.user_username}. Status: {c.status} · Skor: {c.score}</p><p>Versi standar: {standard.curriculum_version || 'tidak dicatat'} · Mode: {standard.mode || 'provenance lama tidak dicatat'}</p>
    {publicView && <p>Integritas: {c.integrity_verified ? 'sesuai proof' : 'belum terverifikasi'} · {c.integrity_reason}</p>}
    <h3>Standar saat dibuat</h3><ul>{(standard.observable_behaviors || []).map((s, i) => <li key={i}>{s}</li>)}</ul>
    {(standard.skill_standards || []).map((s) => <div className="study-step" key={s.skill_id}><h4>{s.title}</h4><p>{s.evaluation.objective}</p><p>{s.evaluation.mastery_criteria}</p><p>Penilai: {s.evaluation.provider} · Review: {s.evaluation.review_status} · Skor: {s.score} / {s.evaluation.max_score}</p></div>)}
    <h3>Evidence terkait</h3><ul>{c.evidences.map((e) => <li key={e.id}>Submission #{e.submission || 'tidak tersedia'}{['github_url', 'demo_url', 'file_url'].map((k) => sourceHref(e[k]) && <p key={k}><a href={sourceHref(e[k])} target="_blank" rel="noopener noreferrer">{k} (tab baru)</a></p>)}</li>)}</ul>
    {!publicView && <Link className="button secondary" href={`/verify/${credentialId}`}>Buka verifikasi publik / tautan untuk dibagikan</Link>}
    <p className="hint">Draft demo tidak memiliki proof dan tidak valid. Integritas proof bukan verifikasi isi repository atau audit independen kemampuan.</p>
  </section>;
}
