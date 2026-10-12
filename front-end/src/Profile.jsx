'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { WorkspaceLayout, useSession } from './App.jsx';
import { logout, reloadProfile } from './api.js';
import { profileEmail, progressSummary } from './dashboard.js';
import { loadProgress } from './study.js';
import { Button, EmptyState, Icon, LoadingState, Notice } from './ui.jsx';

const roleNames = { student: 'Student', recruiter: 'Recruiter', admin: 'Admin' };
const upcomingSettings = [
  ['Edit profil', 'Perbarui informasi akunmu'],
  ['Ganti kata sandi', 'Perbarui kata sandi akunmu'],
  ['Pengingat belajar', 'Notifikasi belajar harian'],
  ['Privasi profil', 'Kelola visibilitas profil'],
];

function joinedDate(value) {
  if (!value) return 'Belum tersedia';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? 'Belum tersedia' : new Intl.DateTimeFormat('id-ID', { dateStyle: 'long' }).format(date);
}

export default function Profile() {
  const { user } = useSession();
  const router = useRouter();
  const [progressState, setProgressState] = useState({ loading: true });
  const [profileError, setProfileError] = useState('');
  const [revision, setRevision] = useState(0);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    setProgressState({ loading: true });
    loadProgress({ signal: controller.signal }).then(
      (progress) => { if (!controller.signal.aborted) setProgressState({ progress }); },
      (error) => { if (!controller.signal.aborted) setProgressState({ error: error.message }); },
    );
    return () => controller.abort();
  }, [revision]);

  async function refresh() {
    setBusy(true);
    setProfileError('');
    setRevision((current) => current + 1);
    try { await reloadProfile(); } catch (error) { setProfileError(error.message); }
    finally { setBusy(false); }
  }

  function signOut() {
    logout();
    router.replace('/login?logged_out=1');
  }

  const summary = progressState.progress ? progressSummary(progressState.progress) : null;
  return <WorkspaceLayout><section className="workspace-content profile-v3" aria-busy={progressState.loading}>
    <p className="eyebrow">AKUN PROGRESSIO</p>
    <h1>Profil akun</h1>
    <p className="intro">Informasi identitas dan kemajuan yang tercatat pada akunmu.</p>
    {profileError && <Notice tone="error" title="Profil belum dapat diperbarui">{profileError}</Notice>}

    <section className="profile-v3-card" aria-labelledby="identity-title">
      <div className="profile-v3-heading"><div className="profile-avatar" aria-hidden="true">{user?.username?.trim()?.[0]?.toUpperCase() || '?'}</div>
        <div><p className="eyebrow">IDENTITAS AKUN</p><h2 id="identity-title">{user?.username || 'Pengguna'}</h2></div>
      </div>
      <dl className="profile-v3-identity">
        <div><dt>Username</dt><dd>{user?.username || 'Belum tersedia'}</dd></div>
        <div><dt>Email</dt><dd>{profileEmail(user?.email)}</dd></div>
        <div><dt>Peran</dt><dd>{roleNames[user?.role] || user?.role || 'Belum tersedia'}</dd></div>
        <div><dt>Bergabung</dt><dd>{joinedDate(user?.date_joined)}</dd></div>
      </dl>
    </section>

    <section className="profile-v3-section" aria-labelledby="profile-progress-title">
      <div className="profile-v3-section-heading"><div><p className="eyebrow">DARI SERVER</p><h2 id="profile-progress-title">Kemajuan belajar</h2></div>
        <Button variant="secondary" disabled={busy || progressState.loading} onClick={refresh}>{busy ? 'Memuat…' : 'Muat ulang'}</Button></div>
      {progressState.loading && <LoadingState>Memuat kemajuan akun…</LoadingState>}
      {progressState.error && <Notice tone="error" title="Kemajuan belum tersedia">{progressState.error}</Notice>}
      {summary && <div className="profile-v3-stats">
        <article><span><Icon name="chart"/>Total XP</span><strong>{summary.totalXp.toLocaleString('id-ID')}</strong><small>Dicatat oleh server</small></article>
        <article><span><Icon name="book"/>Materi selesai</span><strong>{summary.completedLessons}</strong><small>Completion tersimpan</small></article>
      </div>}
      {summary && summary.totalXp === 0 && summary.completedLessons === 0 && <EmptyState icon="book" title="Perjalananmu baru dimulai">XP dan materi selesai akan tercatat saat kamu belajar.</EmptyState>}
    </section>

    <section className="profile-v3-section" aria-labelledby="profile-journey-title"><div className="profile-v3-section-heading"><div><p className="eyebrow">BELUM TERSEDIA</p><h2 id="profile-journey-title">Aktivitas dan pencapaian</h2></div></div>
      <div className="profile-v3-unavailable">
        <p>Streak, level, lencana, dan peta aktivitas belum tersedia dari server.</p>
        <Button href="/credentials" variant="secondary">Lihat credential <Icon name="arrow" size={18}/></Button>
      </div>
    </section>

    <section className="profile-v3-section" aria-labelledby="profile-settings-title"><p className="eyebrow">PENGATURAN</p><h2 id="profile-settings-title">Pengaturan akun</h2>
      <ul className="profile-v3-settings">{upcomingSettings.map(([title, description]) => <li key={title}>
        <span><strong>{title}</strong><small>{description}</small></span><button type="button" disabled aria-label={`${title}, segera`}>SEGERA</button>
      </li>)}</ul>
      <Button className="profile-v3-logout" variant="secondary" onClick={signOut}><Icon name="logout"/>Keluar</Button>
    </section>
  </section></WorkspaceLayout>;
}
