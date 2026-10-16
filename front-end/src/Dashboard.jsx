'use client';

import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { WorkspaceLayout } from './App.jsx';
import { loadTarget } from './catalog.js';
import { progressSummary, nextStudyStep, loadDashboardData, journeyStatuses, displayUsername } from './dashboard.js';
import { loadRoadmap } from './roadmap.js';
import { loadProgress, studyHref } from './study.js';
import { Button, EmptyState, Icon, JourneyTracker, LoadingState, Notice } from './ui.jsx';

export default function Dashboard({ user }) {
  const query = useSearchParams().toString();
  const [revision, setRevision] = useState(0);
  const [state, setState] = useState({ loading: true });
  useEffect(() => {
    const controller = new AbortController();
    const options = { signal: controller.signal };
    setState({ query, loading: true });
    loadDashboardData(query, options, loadProgress, loadTarget, loadRoadmap).then((data) => {
      if (data) setState({ query, ...data });
    });
    return () => controller.abort();
  }, [query, revision]);
  const current = state.query === query ? state : { loading: true };
  const username = displayUsername(user, 'teman');
  const summary = current.progress ? progressSummary(current.progress) : null;
  const nextStep = nextStudyStep(current.roadmap);
  const targetQuery = query ? `?${query}` : '';
  const statuses = journeyStatuses(current.target, current.roadmap);
  return <WorkspaceLayout><section className="workspace-content dashboard-content" aria-busy={Boolean(current.loading)}>
    <p className="eyebrow">RINGKASAN</p>
    <h1>Halo, {username}.</h1>
    <p className="intro">Lihat kemajuan belajarmu dan tentukan langkah berikutnya.</p>
    {current.loading && <LoadingState>Memuat ringkasan akun dan progres belajar…</LoadingState>}
    {current.progressError && <Notice tone="error" title="Progres belum tersedia">{current.progressError}</Notice>}
    {current.targetError && <Notice tone="error" title="Target belum dapat dimuat">{current.targetError}</Notice>}
    {current.roadmapError && <Notice tone="error" title="Roadmap belum dapat dimuat">{current.roadmapError} Gunakan tombol Perbarui untuk mencoba lagi.</Notice>}
    <div className="dashboard-grid">
    <div className="dashboard-hero">
      {current.target ? <>
        <div className="dashboard-hero-copy"><p className="eyebrow">TARGET DARI TAUTAN INI</p><h2>{current.target.title}</h2>
          <p>Target ini dibaca dari URL. Pilihan target belum disimpan sebagai preferensi akun.</p>
          <Button href={`/roadmap${targetQuery}`}>Lihat roadmap <Icon name="arrow" size={18}/></Button>
        </div>
        <div className="dashboard-next">
          <span className="dashboard-step-label">LANGKAH BELAJAR BERIKUT</span>
          {nextStep ? <><h3>{nextStep.skill_title}</h3><p>{nextStep.competency_title} · {nextStep.difficulty} · {nextStep.estimated_minutes} menit</p>
            <Link className="dashboard-text-link" href={studyHref(query, nextStep.skill_id)}>Buka materi <Icon name="arrow" size={16}/></Link></>
            : current.roadmap ? <p>Tidak ada langkah tersisa pada roadmap ini. Periksa roadmap untuk melihat skill yang sudah cukup menurut mastery server.</p>
              : <p>Langkah berikut belum dapat dimuat. Perbarui ringkasan untuk mencoba lagi.</p>}
        </div>
      </> : <div className="dashboard-empty-target"><p className="eyebrow">MULAI DENGAN ARAH YANG JELAS</p><h2>Pilih target belajar pertamamu.</h2>
        <p>Target tidak tersimpan di profil. Pilih target untuk melihat roadmap dan langkah belajar yang sesuai.</p>
        <Button href="/catalog">Pilih target <Icon name="arrow" size={18}/></Button>
      </div>}
    </div>
    <aside className="dashboard-rail" aria-label="Ringkasan progres akun">
    <section className="dashboard-section" aria-labelledby="progress-title">
      <div className="dashboard-section-heading"><div><p className="eyebrow">DATA AKUN AKTIF</p><h2 id="progress-title">Ringkasan progres</h2></div>
        <button className="button secondary" type="button" disabled={current.loading} onClick={() => setRevision((value) => value + 1)}>Perbarui</button>
      </div>
      {summary ? <div className="dashboard-stats">
        <article className="dashboard-stat dashboard-stat-xp"><span><Icon name="chart"/>Total XP</span><strong>{summary.totalXp.toLocaleString('id-ID')}</strong><small>Diberikan oleh server</small></article>
        <article className="dashboard-stat dashboard-stat-study"><span><Icon name="book"/>Materi selesai</span><strong>{summary.completedLessons}</strong><small>Materi dengan ID selesai tersimpan</small></article>
        <article className="dashboard-stat dashboard-stat-skills"><span><Icon name="target"/>Skill dengan mastery</span><strong>{summary.skillsWithMastery}</strong><small>Dari data progres akun</small></article>
      </div> : !current.loading && !current.progressError && <EmptyState icon="chart" title="Belum ada progres">Selesaikan materi untuk mulai mencatat XP dan progres.</EmptyState>}
    </section>
    </aside>
    </div>
    <section className="dashboard-section" aria-labelledby="journey-title"><p className="eyebrow">TAHAPAN BELAJAR</p><h2 id="journey-title">Perjalananmu</h2>
      <JourneyTracker statuses={statuses} className="dashboard-journey" />
      {!current.target && <p className="hint">Pilih target untuk menghubungkan tahapan belajar dengan roadmap yang tervalidasi.</p>}
    </section>
    {current.roadmap && <section className="dashboard-section" aria-labelledby="steps-title"><div className="dashboard-section-heading"><div><p className="eyebrow">DARI ROADMAP SERVER</p><h2 id="steps-title">Langkah berikutnya</h2></div>
      <Link href={`/roadmap${targetQuery}`}>Semua langkah</Link></div>
      {!current.roadmap.steps.length ? <p className="dashboard-no-steps">Semua skill pada roadmap ini sudah cukup berdasarkan mastery yang tersimpan. Ini bukan bukti kelulusan assessment.</p>
        : <ol className="dashboard-steps">{current.roadmap.steps.slice(0, 3).map((step) => <li key={step.skill_id}>
          <span className="dashboard-step-number">{step.order.toString().padStart(2, '0')}</span><div><h3>{step.skill_title}</h3><p>{step.competency_title} · {step.difficulty} · {step.estimated_minutes} menit</p></div>
          <Link className="dashboard-step-action" href={studyHref(query, step.skill_id)} aria-label={`Pelajari ${step.skill_title}`}>Belajar <Icon name="arrow" size={17}/></Link>
        </li>)}</ol>}
    </section>}
    {current.loading && <div className="sr-only" role="status">Sedang memuat data ringkasan.</div>}
    <Link className="dashboard-profile-link" href="/profile"><Icon name="user" size={18}/> Lihat profil akun</Link>
  </section></WorkspaceLayout>;
}
