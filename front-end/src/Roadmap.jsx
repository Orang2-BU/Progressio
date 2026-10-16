'use client';

import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { WorkspaceLayout } from './App.jsx';
import { loadTarget, formatMinutes } from './catalog.js';
import { loadRoadmap, roadmapCoveragePercent } from './roadmap.js';
import { studyHref } from './study.js';
import { DifficultyTag, EmptyState, Icon, LoadingState } from './ui.jsx';

export default function Roadmap() {
  const query = useSearchParams().toString();
  const [revision, setRevision] = useState(0);
  const [state, setState] = useState({ loading: true });
  const [selectedId, setSelectedId] = useState(null);
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
  useEffect(() => { setSelectedId(data?.steps?.[0]?.skill_id ?? null); }, [data]);
  const suffix = query ? `?${query}` : '';
  const titles = new Map([...(data?.steps || []), ...(data?.already_satisfied || [])].map((s) => [s.skill_slug, s.skill_title]));
  const satisfiedSlugs = new Set((data?.already_satisfied || []).map((s) => s.skill_slug));
  const stepOrderBySlug = new Map((data?.steps || []).map((s) => [s.skill_slug, s.order]));
  const selectedStep = (data && (data.steps.find((s) => s.skill_id === selectedId) || data.steps[0])) || null;
  const coveragePercent = roadmapCoveragePercent(data);
  function prereqNote(slug) {
    if (satisfiedSlugs.has(slug)) return 'Cukup untuk roadmap ini';
    if (stepOrderBySlug.has(slug)) return `Akan dipelajari di langkah ${stepOrderBySlug.get(slug)}`;
    return 'Belum tercakup pada roadmap ini';
  }
  return <WorkspaceLayout><section className="workspace-content roadmap-content" aria-busy={Boolean(current.loading)}>
    <p className="eyebrow">03 / SUSUN LANGKAH</p><h1>Roadmap menuju targetmu.</h1>
    <p className="intro">Urutan skill disusun server dari target, mastery tersimpan dan prasyarat. Ini rencana pengembangan, bukan bukti lulus atau credential.</p>
    <nav className="profile-actions" aria-label="Navigasi target roadmap"><Link href={`/catalog${suffix}`}>Kembali ke target</Link>
      <Link href={`/diagnostic${suffix}`}>Ukur ulang titik awal</Link><Link href={`/diagnostic/result${suffix}`}>Hasil diagnostic terbaru</Link></nav>
    <p className="hint">Diagnostic tidak wajib untuk membuka roadmap. Tanpa progress, mastery dianggap 0. Mastery dapat berasal dari diagnostic, aktivitas belajar, atau assessment; roadmap tidak memakai skor attempt terakhir saja.</p>
    {current.loading && <LoadingState>Memuat roadmap dari server…</LoadingState>}
    {current.error && <div className="error-summary" role="alert"><p>{current.error}</p><button className="button secondary" onClick={() => setRevision((n) => n + 1)}>Coba lagi</button></div>}
    {data && <>
      <section className="profile-card roadmap-summary" aria-labelledby="roadmap-summary"><p className="eyebrow">TARGET / {data.target.type}</p><h2 id="roadmap-summary">{data.target.title}</h2>
        <p>Career track: {current.target.track.title}</p>
        <dl><div><dt>Langkah tersisa</dt><dd>{data.total_steps} skill</dd></div><div><dt>Estimasi belajar tersisa</dt><dd>{data.remaining_minutes} menit / sekitar {data.remaining_hours} jam</dd></div>
          {coveragePercent !== null && <div><dt>Cakupan skill cukup</dt><dd>{coveragePercent}% dari skill unik roadmap ini</dd></div>}</dl>
        <p className="hint">Estimasi berasal dari katalog, bukan deadline atau jaminan menguasai skill. Ambang cukup untuk roadmap saat ini 70 mastery; label mastered pada learning-path memakai 85. Keduanya bukan bukti assessment lulus. Cakupan skill cukup bukan kelayakan credential; evidence assessment tetap diperlukan.</p>
        <button className="button secondary" onClick={() => setRevision((n) => n + 1)}>Perbarui roadmap</button>
      </section>
      <section aria-labelledby="remaining-title" className="roadmap-path-section"><h2 id="remaining-title">Langkah yang masih diperlukan</h2>
        {data.steps.length === 0 ? <EmptyState icon="check" title="Tidak ada langkah tersisa menurut mastery server">Ini tidak berarti credential sudah memenuhi syarat; evidence assessment tetap diperlukan.</EmptyState> : <div className="roadmap-path-layout">
          <ol className="roadmap-path" aria-label="Jalur skill berurutan">{data.steps.map((s, index) => <li key={s.skill_id} className={`roadmap-node-row${index % 2 ? ' is-alt' : ''}`}>
            <button type="button" className={`roadmap-node${selectedStep?.skill_id === s.skill_id ? ' is-selected' : ''}`} aria-pressed={selectedStep?.skill_id === s.skill_id}
              aria-label={`Lihat detail langkah ${s.order}: ${s.skill_title}`} onClick={() => setSelectedId(s.skill_id)}><span aria-hidden="true">{s.order}</span></button>
            <span className="roadmap-node-copy"><strong>{s.skill_title}</strong><span className="hint">{s.competency_title} · {formatMinutes(s.estimated_minutes)} · {s.is_target ? 'Bagian target' : 'Prasyarat target'}</span></span>
          </li>)}</ol>
          {selectedStep && <aside className="roadmap-detail profile-card" aria-labelledby="roadmap-detail-title">
            <p className="eyebrow">LANGKAH {selectedStep.order} / {data.total_steps}</p><h3 id="roadmap-detail-title">{selectedStep.skill_title}</h3>
            <p className="hint">{selectedStep.competency_title} · {selectedStep.is_target ? 'Bagian target' : 'Prasyarat target'}</p>
            <div className="roadmap-detail-tags"><DifficultyTag level={selectedStep.difficulty} /><span className="ui-status ui-status-info">{formatMinutes(selectedStep.estimated_minutes)}</span><span className="ui-status ui-status-info">Mastery tersimpan {selectedStep.mastery} / 100</span></div>
            <h4>Prasyarat ({selectedStep.prerequisites.length})</h4>{selectedStep.prerequisites.length ? <ul className="roadmap-prereq-list">{selectedStep.prerequisites.map((slug) => <li key={slug}><strong>{titles.get(slug) || slug}</strong><span className="hint">{prereqNote(slug)}</span></li>)}</ul> : <p className="hint">Tidak ada prasyarat pada katalog.</p>}
            <Link className="button primary full" href={studyHref(query, selectedStep.skill_id)}>Mulai belajar {selectedStep.skill_title} <Icon name="arrow" size={18} /></Link>
          </aside>}
        </div>}
      </section>
      <section className="profile-card roadmap-satisfied" aria-labelledby="satisfied-title"><h2 id="satisfied-title">Cukup untuk roadmap ini</h2>
        <p className="hint">Ditentukan server dari mastery tersimpan, bukan tanda selesai membaca. Prasyarat di bawah skill yang sudah cukup tidak ditelusuri ulang oleh backend.</p>
        {data.already_satisfied.length ? <ul className="diagnostic-scores">{data.already_satisfied.map((s) => <li key={s.skill_slug}><strong>{s.skill_title}</strong><span>Mastery {s.mastery} / 100</span></li>)}</ul> : <p>Belum ada skill pada jalur ini yang dinyatakan cukup.</p>}
      </section>
      <p className="session-note">Roadmap dihitung ulang, bukan rencana tersimpan. Membuka atau memperbaruinya tidak mengubah mastery/XP. Skill yang sudah cukup tetap dapat dipelajari dan diuji kembali melalui katalog. Buka assessment dari materi; kelayakan credential memerlukan evidence tiap skill.</p>
    </>}
  </section></WorkspaceLayout>;
}
