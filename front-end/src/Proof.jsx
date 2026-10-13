'use client';

import Link from 'next/link';
import { useSearchParams, useRouter } from 'next/navigation';
import { useEffect, useRef, useState } from 'react';
import { WorkspaceLayout } from './App.jsx';
import { request } from './api.js';
import { loadAssessments, assessmentPayload, submitAssessment, recoverSubmission, loadCredentials, loadVerification, proofHref, resultLabel, resultSnapshot } from './proof.js';
import { sourceHref } from './study.js';
import { Button, EmptyState, Icon, Notice, StatusBadge } from './ui.jsx';

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
    const controller = new AbortController(); setState({ loading: true }); setIssue(null);
    const options = { signal: controller.signal };
    (mode === 'verify' ? loadVerification(credentialId, options) : mode === 'credentials' ? loadCredentials(query, options) : loadAssessments(query, options))
      .then((data) => { if (!controller.signal.aborted) setState({ data }); })
      .catch((error) => { if (!controller.signal.aborted) setState({ error }); });
    return () => controller.abort();
  }, [mode, query, credentialId, revision]);
  async function issueCredential() {
    if (lock.current) return; lock.current = true; setBusy(true); setIssue(null);
    try {
      const eligibility = state.data.eligibility;
      const detail = await request('credentials/issue', { method: 'POST', body: { competency_id: eligibility.competency, demo: !eligibility.eligible } });
      if (alive.current) router.push(`/credentials?claim=${eligibility.competency}&id=${detail.id}`);
    } catch (error) { if (alive.current) setIssue(error); }
    finally { lock.current = false; if (alive.current) setBusy(false); }
  }
  const data = state.data;
  const params = new URLSearchParams(query); params.delete('exam'); params.delete('submission');
  const Wrapper = mode === 'verify' ? 'div' : WorkspaceLayout;
  return <Wrapper><section className={`workspace-content proof-page proof-${mode}`}>
    {mode === 'verify' ? <PublicHeader /> : <ProofHeader mode={mode} />}
    {state.loading && <p className="ui-loading" role="status">Memuat data server…</p>}
    {state.error && <div className="proof-load-error"><Notice tone={state.error.status === 404 && mode === 'verify' ? 'warning' : 'error'} title={state.error.status === 404 && mode === 'verify' ? 'Credential tidak ditemukan' : 'Data belum dapat dimuat'}>{state.error.status === 404 && mode === 'verify' ? 'ID verifikasi ini tidak ditemukan.' : state.error.message}</Notice>{!(state.error.status === 404 && mode === 'verify') && <Button variant="secondary" onClick={() => setRevision((n) => n + 1)}>Coba lagi</Button>}</div>}
    {mode === 'assessment' && data && <AssessmentPage data={data} query={query} params={params} onRefresh={() => setRevision((n) => n + 1)} />}
    {mode === 'credentials' && data && <CredentialsPage data={data} query={query} busy={busy} issue={issue} onIssue={issueCredential} />}
    {mode === 'verify' && data && <CredentialView data={data} publicView />}
    {mode === 'verify' && <PublicFooter />}
  </section></Wrapper>;
}

function ProofHeader({ mode }) {
  return <header className="proof-heading">
    <p className="eyebrow">05 / KEMAJUAN MENJADI BUKTI</p>
    <h1>{mode === 'assessment' ? 'Assessment dan evidence' : 'Credential-mu'}</h1>
    <p className="intro">{mode === 'assessment' ? 'Tunjukkan pemahaman melalui soal atau evidence yang ditentukan. Skor dan hasil berasal dari penilaian server.' : 'Lihat kelayakan, riwayat credential, dan detail snapshot standar dari server.'}</p>
    <nav className="proof-nav" aria-label="Navigasi bukti"><Link href="/catalog">Pilih target</Link><Link href="/credentials">Credential</Link>{mode === 'assessment' && <Link href="/">Ringkasan</Link>}</nav>
  </header>;
}

function PublicHeader() {
  return <header className="proof-public-header"><p className="eyebrow">VERIFIKASI PUBLIK</p><h1>Verifikasi credential</h1><p>mock dan standar draft bukan bukti final. Draft demo juga bukan credential final; status serta integritas mengikuti respons server.</p></header>;
}

function PublicFooter() { return <footer className="proof-public-footer"><strong>progressio.</strong><span>Turning Progress Into Proof</span></footer>; }

function AssessmentPage({ data, query, params, onRefresh }) {
  return <>
    <div className="proof-context">
      <div><p className="eyebrow">TARGET AKTIF</p><p><strong>{data.target.title}</strong><span>{data.skill.title}</span></p></div>
      <Link href={`/study?${params}`}>Kembali ke materi</Link>
    </div>
      <JourneyTracker />
    {!data.assessments.length && <EmptyState icon="shield" title="Assessment belum tersedia">Belum ada assessment untuk skill ini.</EmptyState>}
    {!data.assessment && !!data.assessments.length && <section className="proof-section proof-assessment-picker"><div className="proof-section-title"><div><p className="eyebrow">ASSESSMENT</p><h2>{data.assessments.length > 1 ? 'Pilih assessment' : 'Assessment tersedia'}</h2></div></div><div className="proof-assessment-list">{data.assessments.map((assessment) => { const next = new URLSearchParams(params); next.set('exam', assessment.id); return <Link key={assessment.id} className="proof-assessment-choice" href={`/assessment?${next}`}><span>{assessment.title}</span><Icon name="arrow" size={18}/></Link>; })}</div></section>}
    {data.assessment && <>
      <AssessmentWorkspace assessment={data.assessment} data={data} query={query} />
      {data.result && <Result result={data.result} />}
      <SubmissionHistory data={data} query={query} onRefresh={onRefresh} />
    </>}
  </>;
}

function JourneyTracker() {
  return <ol className="proof-journey" aria-label="Tahapan perjalanan"><li aria-current="step">05 / Assessment dan credential</li></ol>;
}

function AssessmentWorkspace({ assessment: a, data, query }) {
  return <div className="proof-assessment-grid">
    <article className="proof-panel proof-standard">
      <div className="proof-panel-heading"><p className="eyebrow">STANDAR · {data.competency.title}</p><h2>{a.title}</h2><Difficulty level={data.skill.difficulty}/></div>
      <div className="proof-panel-body"><h3>Standar yang diukur</h3><p>{a.objective}</p><p>{a.mastery_criteria}</p>
        {a.instructions && <div className="proof-instructions"><h3>Panduan pengerjaan</h3><p>{a.instructions}</p></div>}
        {!!a.expected_evidence.length && <><h3>Evidence yang diharapkan</h3><ul>{a.expected_evidence.map((item, index) => <li key={index}>{item}</li>)}</ul></>}
        <div className="proof-rubric"><div className="proof-section-title"><h3>Rubrik penilaian</h3><span>Bobot dari server</span></div>
          {a.rubric?.length ? <div className="proof-table-wrap"><table><thead><tr><th>Kriteria</th><th className="numeric">Bobot</th></tr></thead><tbody>{a.rubric.map((row, index) => <tr key={`${row.criterion}-${index}`}><td>{row.criterion}</td><td className="numeric">{row.weight}</td></tr>)}</tbody></table></div> : <p className="proof-muted">Rubrik per kriteria tidak tersedia. Penilaian mengikuti standar server.</p>}
        </div>
        <Notice tone="info" title="Cara penilaian">Mode: {a.evaluation_mode === 'rules' ? 'soal dengan aturan server' : 'evidence dinilai server'}. Skor maksimum {a.max_score}; ambang lulus {a.passing_score}. Review standar: {a.review_status}.</Notice>
      </div>
    </article>
    <div className="proof-assessment-submit"><AssessmentForm assessment={a} query={query}/></div>
  </div>;
}

function Difficulty({ level }) {
  const labels = { beginner: 'Pemula', intermediate: 'Menengah', advanced: 'Mahir' };
  return labels[level] ? <StatusBadge tone="info">{labels[level]}</StatusBadge> : null;
}

function AssessmentForm({ assessment: a, query }) {
  const [answers, setAnswers] = useState({}); const [evidence, setEvidence] = useState({ text: '', github_url: '', demo_url: '' });
  const [busy, setBusy] = useState(false); const [issue, setIssue] = useState(null); const [pending, setPending] = useState(null); const [notice, setNotice] = useState('');
  const lock = useRef(false); const alive = useRef(true); const router = useRouter();
  useEffect(() => { alive.current = true; return () => { alive.current = false; }; }, []);
  function show(s) { const p = new URLSearchParams(query); p.set('submission', s.id); router.push(`/assessment?${p}`); }
  async function submit(event) {
    event.preventDefault(); if (lock.current) return; lock.current = true; setBusy(true); setIssue(null); setNotice('');
    let body;
    try { body = pending || assessmentPayload(a, answers, evidence, crypto.randomUUID()); setPending(body); const result = await submitAssessment(a, body); if (alive.current) show(result); }
    catch (error) { if (alive.current) { setIssue(error); if (!body || [400, 401, 403].includes(error.status)) setPending(null); } }
    finally { lock.current = false; if (alive.current) setBusy(false); }
  }
  async function recover() {
    if (lock.current || !pending) return; lock.current = true; setBusy(true); setIssue(null); setNotice('');
    try { const result = await recoverSubmission(a, pending.request_id); if (alive.current) { if (result) show(result); else setNotice('Hasil belum ditemukan. Isian tetap terkunci; coba periksa kembali atau kirim ulang payload yang sama dengan request ID ini.'); } }
    catch (error) { if (alive.current) setIssue(error); }
    finally { lock.current = false; if (alive.current) setBusy(false); }
  }
  const links = Object.fromEntries(a.questions.map((q, index) => [q.id, `exam-question-${index}`]));
  for (const key of ['text', 'github_url', 'demo_url']) links[key] = `evidence-${key}`;
  return <form onSubmit={submit} noValidate aria-busy={busy} className="proof-editor">
    <div className="proof-editor-bar"><span><i aria-hidden="true"/> evidence.md</span><span>{a.evaluation_mode === 'rules' ? 'KUIS · JAWABAN DARI STANDAR' : 'EVIDENCE · INPUT TEKS DAN URL'}</span></div>
    <div className="proof-editor-content"><div className="proof-editor-intro"><p className="eyebrow">KIRIM BUKTI</p><h2>{a.evaluation_mode === 'rules' ? 'Jawab setiap soal' : 'Jelaskan evidence-mu'}</h2><p>Isian dikirim ke server untuk dinilai. Jangan sertakan secret atau data pribadi.</p></div>
      <ErrorSummary issue={issue} links={links}/>
      <fieldset disabled={busy || Boolean(pending)} className="proof-fields">
        {a.evaluation_mode === 'rules' ? a.questions.map((q, index) => <fieldset key={q.id} className="proof-question"><legend><span>{String(index + 1).padStart(2, '0')}</span>{q.prompt}</legend><div className="proof-options">{q.options.map((option, optionIndex) => <label key={option.value} className="proof-option"><input id={optionIndex === 0 ? links[q.id] : undefined} type="radio" name={`exam-${index}`} checked={answers[q.id] === option.value} aria-invalid={Boolean(issue?.fields?.[q.id])} aria-describedby={issue?.fields?.[q.id] ? `exam-error-${index}` : undefined} onChange={() => setAnswers({ ...answers, [q.id]: option.value })}/><span>{option.label}</span></label>)}</div>{issue?.fields?.[q.id] && <p className="field-error" id={`exam-error-${index}`}>{issue.fields[q.id]}</p>}</fieldset>) : ['text', 'github_url', 'demo_url'].map((key) => <div className="proof-field" key={key}><label htmlFor={links[key]}>{key === 'text' ? 'Isi evidence atau kode (wajib)' : key === 'github_url' ? 'URL repositori GitHub (opsional)' : 'URL demo (opsional)'}</label>{key === 'text' ? <textarea id={links[key]} rows="12" value={evidence[key]} maxLength={190000} aria-invalid={Boolean(issue?.fields?.[key])} aria-describedby={`${links[key]}-hint`} onChange={(event) => setEvidence({ ...evidence, [key]: event.target.value })}/> : <input id={links[key]} value={evidence[key]} maxLength={500} type="url" aria-invalid={Boolean(issue?.fields?.[key])} aria-describedby={`${links[key]}-hint`} onChange={(event) => setEvidence({ ...evidence, [key]: event.target.value })}/>}<p id={`${links[key]}-hint`} className={issue?.fields?.[key] ? 'field-error' : 'hint'}>{issue?.fields?.[key] || (key === 'text' ? 'Maksimal 200 KB. URL saja tidak cukup; teks tidak dijalankan sebagai kode.' : 'Gunakan URL HTTP(S) tanpa kredensial.')}</p></div>)}
      </fieldset>
      {pending && <Notice tone="warning" title="Request terkunci untuk recovery"><p>Request ID: <code>{pending.request_id}</code>. Payload dipertahankan agar retry memakai request yang sama. Reload menghapus isian; hasil tersimpan tetap ada di riwayat.</p><Button type="button" variant="secondary" disabled={busy} onClick={recover}>Periksa hasil request ini</Button></Notice>}
      {notice && <Notice tone="info" title="Status recovery">{notice}</Notice>}
      <div className="proof-submit-row"><button type="submit" className="button primary" disabled={busy || (a.evaluation_mode === 'rules' && !a.questions.length)}>{busy ? 'Menilai di server…' : pending ? 'Kirim ulang request yang sama' : 'Kirim untuk dinilai'}<Icon name="arrow" size={18}/></button><span>Skor dan kelulusan ditentukan server.</span></div>
      <p className="proof-simulation-note"><strong>Draft demo bukan credential final.</strong> Hasil provider mock atau standar draft tidak menjadi bukti kompetensi final.</p>
    </div>
  </form>;
}

export function Result({ result }) {
  const { heading, label } = resultLabel(result);
  const snapshot = resultSnapshot(result);
  return <section className="proof-section proof-result"><div className="proof-section-title"><div><p className="eyebrow">HASIL PENILAIAN SERVER</p><h2>{heading}</h2></div><StatusBadge tone={result.is_passed ? 'success' : 'warning'}>{result.status}</StatusBadge></div>
    <div className="proof-result-score"><strong>{result.score ?? '—'}</strong><span>/ {snapshot.maxScore ?? 'maksimum tidak dicatat'}</span></div>
    {snapshot.passingScore !== null && <p className="proof-muted">Ambang lulus saat dinilai: <strong>{snapshot.passingScore} / {snapshot.maxScore ?? 'maksimum tidak dicatat'}</strong> · status lulus mengikuti keputusan server.</p>}
    {label && <Notice tone="warning" title="Batas status evidence">{label}</Notice>}
    <p className="proof-feedback">{result.feedback || 'Feedback belum tersedia.'}</p>
    {snapshot.rubric.length > 0 && <div className="proof-rubric proof-result-rubric"><div className="proof-section-title"><h3>Rubrik pada snapshot penilaian</h3><span>Kriteria dan bobot dari server; skor per kriteria tidak tersedia.</span></div><div className="proof-table-wrap"><table><caption className="sr-only">Rubrik yang tersimpan saat submission dinilai</caption><thead><tr><th>Kriteria</th><th className="numeric">Bobot</th></tr></thead><tbody>{snapshot.rubric.map((row, index) => <tr key={`${row.criterion}-${index}`}><td>{row.criterion}</td><td className="numeric">{row.weight}</td></tr>)}</tbody></table></div></div>}
    <dl className="proof-provenance"><div><dt>Penilai</dt><dd>{result.evaluation.provider || 'tidak dicatat'}</dd></div><div><dt>Review</dt><dd>{result.evaluation.review_status || 'tidak dicatat'}</dd></div><div><dt>Versi kurikulum</dt><dd>{result.evaluation.curriculum_version || 'tidak dicatat'}</dd></div></dl>
  </section>;
}

function SubmissionHistory({ data, query, onRefresh }) {
  const params = new URLSearchParams(query);
  return <section className="proof-section proof-history"><div className="proof-section-title"><div><p className="eyebrow">RIWAYAT</p><h2>Submission assessment</h2></div><button className="button secondary" onClick={onRefresh}>Perbarui riwayat</button></div>
    {!data.submissions.length ? <p className="proof-muted">Belum ada submission untuk assessment ini.</p> : <div className="proof-table-wrap"><table><thead><tr><th>Submission</th><th>Status</th><th className="numeric">Skor</th><th>Hasil</th></tr></thead><tbody>{data.submissions.map((submission) => { const href = new URLSearchParams(params); href.set('submission', submission.id); return <tr key={submission.id}><td><Link href={`/assessment?${href}`}>#{submission.id}</Link></td><td>{submission.status}</td><td className="numeric">{submission.score ?? '—'}</td><td>{submission.status === 'completed' ? resultLabel(submission).heading : 'Belum selesai dinilai'}</td></tr>; })}</tbody></table></div>}
  </section>;
}

function CredentialsPage({ data, query, busy, issue, onIssue }) {
  const params = new URLSearchParams(query);
  const eligibility = data.eligibility;
  return <>
    {eligibility && <section className="proof-eligibility"><div className="proof-eligibility-copy"><p className="eyebrow">KELAYAKAN BERDASARKAN EVIDENCE</p><h2>{eligibility.eligible ? 'Memenuhi syarat credential final' : eligibility.demo_ready ? 'Tersedia draft demo' : 'Belum memenuhi syarat'}</h2><p>{eligibility.reason}</p><StatusBadge tone={eligibility.eligible ? 'success' : 'warning'}>{eligibility.eligible ? 'eligible' : eligibility.demo_ready ? 'demo_ready' : 'belum eligible'}</StatusBadge><dl className="proof-provenance">{eligibility.score !== undefined && <Fact label="Skor server">{eligibility.score}</Fact>}{eligibility.curriculum_version && <Fact label="Versi kurikulum">{eligibility.curriculum_version}</Fact>}{eligibility.curriculum_status && <Fact label="Review standar">{eligibility.curriculum_status}</Fact>}{eligibility.proof_provider && <Fact label="Provider proof">{eligibility.proof_provider}</Fact>}</dl></div><div className="proof-eligibility-action"><ErrorSummary issue={issue}/><button className="button primary" onClick={onIssue} disabled={busy || (!eligibility.eligible && !eligibility.demo_ready)}>{busy ? 'Memproses…' : eligibility.eligible ? 'Terbitkan credential' : 'Buat draft demo'}</button>{!eligibility.eligible && !eligibility.demo_ready && <p className="proof-muted">Penerbitan dinonaktifkan sampai syarat server terpenuhi.</p>}</div>
      {!!eligibility.missing_skills.length && <div className="proof-missing"><h3>Evidence skill yang belum tersedia</h3><ul>{eligibility.missing_skills.map((skill) => <li key={skill.id}><span>{skill.title}</span>{eligibility.career_track && <Link href={proofHref(`track=${eligibility.career_track}`, skill.id)}>Buka assessment</Link>}</li>)}</ul></div>}
      <p className="proof-simulation-note"><strong>Draft demo bukan credential final.</strong> Kelayakan dihitung dari submission dan provenance server, bukan progress diagnostic atau roadmap.</p>
    </section>}
    {data.detail && <CredentialView data={data.detail} />}
    <section className="proof-section proof-credential-list"><div className="proof-section-title"><div><p className="eyebrow">CATATAN SERVER</p><h2>Credential akun</h2></div></div>
      <form method="get" action="/credentials" className="proof-filters"><label>Status<select name="status" defaultValue={params.get('status') || ''}><option value="">Semua status</option><option value="issued">Final</option><option value="draft">Draft</option><option value="revoked">Dicabut</option></select></label><label>ID competency<input name="competency" inputMode="numeric" pattern="[0-9]+" defaultValue={params.get('competency') || ''}/></label><button className="button secondary" type="submit">Terapkan filter</button>{params.has('claim') && <input type="hidden" name="claim" value={params.get('claim')}/>}</form>
      {!data.list.results.length ? <EmptyState icon="award" title="Belum ada credential">Credential yang diterbitkan akan muncul di sini.</EmptyState> : <div className="proof-credential-cards">{data.list.results.map((credential) => <article className="proof-credential-card" key={credential.id}><div className="proof-credential-card-icon"><Icon name="award" size={26}/></div><div className="proof-credential-card-copy"><p className="eyebrow">{credential.id}</p><h3>{credential.competency_title}</h3><p>Skor {credential.score ?? 'tidak tersedia'}{credential.issued_at && <> · {formatDate(credential.issued_at)}</>}</p></div><StatusBadge tone={credential.status === 'issued' ? 'success' : credential.status === 'revoked' ? 'error' : 'warning'}>{credential.status === 'issued' ? 'Diterbitkan' : credential.status === 'revoked' ? 'Dicabut' : 'Draft'}</StatusBadge><Link className="button secondary" href={`/credentials?id=${credential.id}`}>Detail</Link></article>)}</div>}
      <nav className="proof-pagination" aria-label="Halaman credential">{data.page > 1 && <Link href={credentialPageHref(params, data.page - 1)}>Sebelumnya</Link>}<span>Halaman {data.page}</span>{data.list.next && <Link href={credentialPageHref(params, data.page + 1)}>Berikutnya</Link>}</nav>
    </section>
  </>;
}

function credentialPageHref(params, page) { const next = new URLSearchParams(params); next.set('page', page); return `/credentials?${next}`; }
function formatDate(value) { const date = new Date(value); return Number.isNaN(date.getTime()) ? value : new Intl.DateTimeFormat('id-ID', { dateStyle: 'medium' }).format(date); }

export function CredentialView({ data: credential, publicView = false }) {
  const standard = publicView ? credential.standard : credential.metadata;
  const credentialId = credential.id || credential.credential_id;
  const isFinal = credential.is_valid === true && credential.integrity_verified === true && credential.status === 'issued' && standard?.mode === 'final' && standard?.proof_provider === 'http';
  const isIssuedUnverified = credential.status === 'issued' && !isFinal;
  const statusLabel = credential.status === 'revoked' ? 'Dicabut' : isFinal ? 'Final' : isIssuedUnverified ? 'Terbit · belum terverifikasi' : credential.status === 'draft' ? 'Draft' : credential.status || 'Status tidak diketahui';
  const verificationUrl = `${typeof window !== 'undefined' ? window.location.origin : ''}/verify/${credentialId}`;
  const [copyState, setCopyState] = useState('');
  async function copyVerificationUrl() {
    const value = verificationUrl;
    try {
      if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(value);
      else { const field = document.createElement('textarea'); field.value = value; field.setAttribute('readonly', ''); field.style.position = 'fixed'; field.style.opacity = '0'; document.body.append(field); field.select(); const success = document.execCommand('copy'); field.remove(); if (!success) throw new Error('copy unavailable'); }
      setCopyState('Tautan verifikasi disalin.');
    } catch { setCopyState(`Salin tautan ini: ${value}`); }
  }
  const standardLabel = standard?.mode === 'demo' ? 'Demo' : standard?.mode === 'final' ? 'Final' : 'Mode tidak dicatat';
  return <article className={`proof-section proof-credential-detail ${publicView ? 'is-public' : ''}`}>
    <div className="proof-credential-hero"><div className="proof-credential-emblem"><Icon name="award" size={42}/></div><div><p className="eyebrow">CREDENTIAL · {credentialId}</p><h2>{credential.competency_title || 'Credential'}</h2><p>{credential.student_name || credential.user_username || 'Pemilik tidak dicatat'}</p></div><StatusBadge tone={credential.status === 'revoked' ? 'error' : isFinal ? 'success' : 'warning'}>{statusLabel}</StatusBadge></div>
    <div className="proof-status-banner" role="status"><Icon name={isFinal ? 'check' : credential.status === 'revoked' ? 'warning' : 'info'} size={20}/><div><strong>{credential.status === 'revoked' ? 'Credential dicabut' : isFinal ? 'Credential final · integritas server terkonfirmasi' : isIssuedUnverified ? 'Credential diterbitkan, tetapi belum valid/terverifikasi' : 'Bukan credential final terverifikasi'}</strong><p>{credential.status === 'revoked' ? 'Credential ini tidak boleh digunakan sebagai bukti aktif.' : isFinal ? 'Status final ditentukan oleh provenance dan pemeriksaan server.' : isIssuedUnverified ? (credential.integrity_reason || 'Validitas atau integritas credential belum dapat dikonfirmasi oleh server.') : 'Draft demo bukan credential final. Tampilan ini tidak mengubah status penerbitan.'}</p></div></div>
    <dl className="proof-credential-facts"><Fact label="Status">{credential.status || 'tidak dicatat'}</Fact><Fact label="Skor">{credential.score ?? 'tidak dicatat'}</Fact><Fact label="Tanggal terbit">{credential.issued_at ? formatDate(credential.issued_at) : 'belum diterbitkan'}</Fact><Fact label="Versi standar">{standard?.curriculum_version || 'tidak dicatat'}</Fact><Fact label="Mode standar">{standardLabel}</Fact><Fact label="Provider proof">{standard?.proof_provider || 'tidak dicatat'}</Fact>{publicView && <><Fact label="Integritas">{credential.integrity_verified ? 'Sesuai proof' : 'Belum terkonfirmasi'}</Fact><Fact label="Alasan integritas">{credential.integrity_reason || 'tidak dicatat'}</Fact></>}</dl>
    <section className="proof-snapshot"><h3>Standar saat credential dibuat</h3>{standard?.observable_behaviors?.length ? <ul>{standard.observable_behaviors.map((behavior, index) => <li key={index}>{behavior}</li>)}</ul> : <p className="proof-muted">Snapshot perilaku standar tidak tersedia.</p>}{standard?.skill_standards?.map((skill) => <article className="proof-skill-snapshot" key={skill.skill_id}><p className="eyebrow">SKILL · {skill.skill_id}</p><h4>{skill.title}</h4><p>{skill.evaluation?.objective}</p><p>{skill.evaluation?.mastery_criteria}</p><p>Penilai: {skill.evaluation?.provider || 'tidak dicatat'} · Review: {skill.evaluation?.review_status || 'tidak dicatat'} · Skor: {skill.score ?? '—'} / {skill.evaluation?.max_score ?? '—'}</p></article>)}</section>
    <section className="proof-evidence"><h3>Evidence terkait</h3>{credential.evidences?.length ? <ul>{credential.evidences.map((evidence) => <li key={evidence.id}><strong>Submission #{evidence.submission || 'tidak tersedia'}</strong>{['github_url', 'demo_url', 'file_url'].map((key) => { const href = sourceHref(evidence[key]); return href ? <a key={key} href={href} target="_blank" rel="noopener noreferrer">{key} <span className="sr-only">(tab baru)</span><Icon name="arrow" size={14}/></a> : null; })}</li>)}</ul> : <p className="proof-muted">Evidence tidak tersedia pada respons ini.</p>}</section>
    {publicView ? <p className="proof-integrity-limit">Pemeriksaan integritas mencakup credential dan hash evidence yang tercatat. Ini bukan audit independen atas repository atau kompetensi.</p> : <div className="proof-share"><Notice tone="warning" title="Status demo tetap terlihat">Draft demo bukan credential final.</Notice><div className="proof-share-actions"><Link className="button secondary" href={`/verify/${credentialId}`} target="_blank" rel="noopener noreferrer">Buka verifikasi publik</Link><button className="button secondary" type="button" onClick={copyVerificationUrl}>Salin tautan</button><span role="status" aria-live="polite">{copyState}</span></div><p className="proof-muted">Unduh PDF belum tersedia.</p></div>}
  </article>;
}

function Fact({ label, children }) { return <div><dt>{label}</dt><dd>{children}</dd></div>; }
