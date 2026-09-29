'use client';

import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { WorkspaceLayout } from './App.jsx';
import { loadTarget } from './catalog.js';
import { loadRoadmap } from './roadmap.js';

export default function Roadmap() {
  const query = useSearchParams().toString();
  const [revision, setRevision] = useState(0);
  const [state, setState] = useState({ loading: true });
  useEffect(() => {
    const controller = new AbortController();
    setState({ query, loading: true });
    (async () => {
      const target = await loadTarget(query, { signal: controller.signal });
      const data = await loadRoadmap(target, { signal: controller.signal });
      if (!controller.signal.aborted) setState({ query, target, data });
    })().catch((error) => {
      if (!controller.signal.aborted) setState({ query, error: error.message });
    });
    return () => controller.abort();
  }, [query, revision]);
  const current = state.query === query ? state : { loading: true };
  const data = current.data;
  const suffix = query ? `?${query}` : '';
  const titles = new Map([...(data?.steps || []), ...(data?.already_satisfied || [])].map((s) => [s.skill_slug, s.skill_title]));
  return <WorkspaceLayout><section className="workspace-content roadmap-content" aria-busy={Boolean(current.loading)}>
    <p className="eyebrow">03 / SUSUN LANGKAH</p><h1>Roadmap menuju targetmu.</h1>
    <p className="intro">Urutan skill disusun server dari target, mastery tersimpan dan prasyarat. Ini rencana pengembangan, bukan bukti lulus atau credential.</p>
    <nav className="profile-actions" aria-label="Navigasi target roadmap"><Link href={`/catalog${suffix}`}>Kembali ke target</Link>
      <Link href={`/diagnostic${suffix}`}>Ukur ulang titik awal</Link><Link href={`/diagnostic/result${suffix}`}>Hasil diagnostic terbaru</Link></nav>
    <p className="hint">Diagnostic tidak wajib untuk membuka roadmap. Tanpa progress, mastery dianggap 0. Mastery dapat berasal dari diagnostic, aktivitas belajar, atau assessment; roadmap tidak memakai skor attempt terakhir saja.</p>
    {current.loading && <p role="status">Memuat roadmap dari server…</p>}
    {current.error && <div className="error-summary" role="alert"><p>{current.error}</p><button className="button secondary" onClick={() => setRevision((n) => n + 1)}>Coba lagi</button></div>}
    {data && <>
      <section className="profile-card" aria-labelledby="roadmap-summary"><p className="eyebrow">TARGET / {data.target.type}</p><h2 id="roadmap-summary">{data.target.title}</h2>
        <p>Career track: {current.target.track.title}</p>
        <dl><div><dt>Langkah tersisa</dt><dd>{data.total_steps} skill</dd></div><div><dt>Estimasi belajar tersisa</dt><dd>{data.remaining_minutes} menit / sekitar {data.remaining_hours} jam</dd></div></dl>
        <p className="hint">Estimasi berasal dari katalog, bukan deadline atau jaminan menguasai skill. Ambang cukup untuk roadmap saat ini 70 mastery; label mastered pada learning-path memakai 85. Keduanya bukan bukti assessment lulus.</p>
        <button className="button secondary" onClick={() => setRevision((n) => n + 1)}>Perbarui roadmap</button>
      </section>
      <section aria-labelledby="remaining-title"><h2 id="remaining-title">Langkah yang masih diperlukan</h2>
        {data.steps.length === 0 ? <p className="notice" role="status">Tidak ada langkah tersisa menurut mastery server. Ini tidak berarti credential sudah memenuhi syarat; evidence assessment tetap diperlukan.</p> : <ol className="roadmap-steps">
          {data.steps.map((s) => <li key={s.skill_id} className="profile-card"><p className="eyebrow">LANGKAH {s.order} / {s.is_target ? 'BAGIAN TARGET' : 'PRASYARAT TARGET'}</p>
            <h3>{s.skill_title}</h3><p>{s.competency_title} · {s.difficulty}</p>
            <p>Mastery tersimpan: {s.mastery} / 100 · Estimasi: {s.estimated_minutes} menit</p>
            <details><summary>Prasyarat ({s.prerequisites.length})</summary>{s.prerequisites.length ? <ul>{s.prerequisites.map((slug) => <li key={slug}>{titles.get(slug) || slug}</li>)}</ul> : <p>Tidak ada prasyarat pada katalog.</p>}</details>
          </li>)}</ol>}
      </section>
      <section className="profile-card" aria-labelledby="satisfied-title"><h2 id="satisfied-title">Cukup untuk roadmap ini</h2>
        <p className="hint">Ditentukan server dari mastery tersimpan, bukan tanda selesai membaca. Prasyarat di bawah skill yang sudah cukup tidak ditelusuri ulang oleh backend.</p>
        {data.already_satisfied.length ? <ul className="diagnostic-scores">{data.already_satisfied.map((s) => <li key={s.skill_slug}><strong>{s.skill_title}</strong><span>Mastery {s.mastery} / 100</span></li>)}</ul> : <p>Belum ada skill pada jalur ini yang dinyatakan cukup.</p>}
      </section>
      <p className="session-note">Roadmap dihitung ulang, bukan rencana tersimpan. Membuka atau memperbaruinya tidak mengubah mastery/XP. Materi dan assessment akan disambungkan pada fase berikutnya.</p>
    </>}
  </section></WorkspaceLayout>;
}
