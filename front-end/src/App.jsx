'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useRef, useState, useSyncExternalStore } from 'react';
import { getSession, getServerSession, subscribe, login, register, logout, reloadProfile } from './api.js';
import { loginDestination } from './navigation.js';
import { Button, Icon, Notice, ProgressBar, StatusBadge } from './ui.jsx';

const useSession = () => useSyncExternalStore(subscribe, getSession, getServerSession);
const roleNames = { student: 'Student', recruiter: 'Recruiter', admin: 'Admin' };

function Brand() {
  return <Link className="brand" href="/" aria-label="Progressio, beranda"><span className="brand-mark" aria-hidden="true">p.</span>progressio<span className="brand-dot">.</span></Link>;
}

function AuthForm({ mode, notice, onRegistered }) {
  const router = useRouter();
  const isRegister = mode === 'register';
  const [values, setValues] = useState({ username: '', email: '', password: '', password_confirm: '', role: 'student' });
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const [visible, setVisible] = useState(false);
  const summary = useRef(null);
  const alive = useRef(true);
  useEffect(() => { alive.current = true; return () => { alive.current = false; }; }, []);
  useEffect(() => { if (message) summary.current?.focus(); }, [message, errors]);
  async function submit(event) {
    event.preventDefault();
    if (busy) return;
    setErrors({}); setMessage('');
    if (isRegister && values.password !== values.password_confirm) {
      setErrors({ password_confirm: 'Konfirmasi kata sandi belum sama.' });
      setMessage('Periksa kembali isianmu.'); return;
    }
    setBusy(true);
    try {
      if (isRegister) {
        await register(values);
        if (alive.current) onRegistered(values.username);
      } else {
        const destination = loginDestination(new URLSearchParams(window.location.search).get('next'));
        await login({ username: values.username, password: values.password });
        if (alive.current) router.replace(destination);
      }
    } catch (error) {
      if (alive.current) { setMessage(error.message); setErrors(error.fields || {}); }
    } finally { if (alive.current) setBusy(false); }
  }
  function field(name, label, type = 'text', hint) {
    const password = name.startsWith('password');
    return <div className="field" key={name}>
      <label htmlFor={name}>{label}</label>
      <div className={password ? 'password-field' : undefined}>
        <input id={name} name={name} type={password && visible ? 'text' : type}
          required value={values[name]} disabled={busy}
          maxLength={name === 'username' ? 150 : undefined}
          minLength={isRegister && name === 'password' ? 8 : undefined}
          autoComplete={name === 'password_confirm' || (name === 'password' && isRegister) ? 'new-password' : name === 'password' ? 'current-password' : name}
          aria-invalid={Boolean(errors[name])}
          aria-describedby={[hint && `${name}-hint`, errors[name] && `${name}-error`].filter(Boolean).join(' ') || undefined}
          onChange={(event) => setValues({ ...values, [name]: event.target.value })} />
        {password && name === 'password' && <button className="reveal" type="button" disabled={busy}
          aria-pressed={visible} onClick={() => setVisible(!visible)}>{visible ? 'Sembunyikan' : 'Lihat'}</button>}
      </div>
      {hint && <p className="hint" id={`${name}-hint`}>{hint}</p>}
      {errors[name] && <p className="field-error" id={`${name}-error`}>{errors[name]}</p>}
    </div>;
  }
  return <div className="auth-layout">
    <section className="auth-story" aria-label="Tentang Progressio">
      <span className="eyebrow">TURNING PROGRESS INTO PROOF</span>
      <h1>Kemampuanmu.<br /><span>Buktinya nyata.</span></h1>
      <p>Kenali kemampuanmu hari ini. Bangun langkah yang tepat untuk tujuan berikutnya.</p>
      <ol className="journey">
        <li><span>01</span><div><strong>Ukur titik awal</strong><p>Kenali kemampuan dan celah yang perlu kamu isi.</p></div></li>
        <li><span>02</span><div><strong>Ikuti arah yang jelas</strong><p>Roadmap disusun dari target dan prasyaratnya.</p></div></li>
        <li><span>03</span><div><strong>Tunjukkan bukti</strong><p>Assessment menghubungkan kemampuan dengan evidence.</p></div></li>
      </ol>
      <div className="story-foot">Belajar dengan arah. Berkembang dengan bukti.</div>
    </section>
    <section className="auth-panel" aria-labelledby="form-title">
      <p className="eyebrow">{isRegister ? 'MULAI PERJALANANMU' : 'SELAMAT DATANG KEMBALI'}</p>
      <h2 id="form-title">{isRegister ? 'Buat akun Progressio' : 'Masuk ke workspace'}</h2>
      <p className="intro">{isRegister ? 'Satu akun untuk mengukur dan membuktikan kemampuan.' : 'Gunakan username yang kamu pilih saat mendaftar.'}</p>
      {notice && <Notice tone="success">{notice}</Notice>}
      <form onSubmit={submit} aria-busy={busy}>
        {message && <div ref={summary} className="error-summary" role="alert" tabIndex="-1">
          <strong>{message}</strong>
          {Object.entries(errors).filter(([name]) => name in values).length > 0 && <ul>
            {Object.entries(errors).filter(([name]) => name in values).map(([name, text]) =>
              <li key={name}><a href={`#${name}`} onClick={(event) => { event.preventDefault(); document.getElementById(name)?.focus(); }}>{text}</a></li>)}
          </ul>}
        </div>}
        <fieldset disabled={busy}>
          {field('username', 'Username', 'text', isRegister ? 'Huruf, angka, dan karakter @ . + - _ diperbolehkan.' : undefined)}
          {isRegister && field('email', 'Email', 'email')}
          {field('password', 'Kata sandi', 'password', isRegister ? 'Minimal 8 karakter. Hindari kata sandi umum atau seluruhnya angka.' : undefined)}
          {isRegister && field('password_confirm', 'Konfirmasi kata sandi', 'password')}
          {isRegister && <div className="field"><label htmlFor="role">Saya bergabung sebagai</label>
            <select id="role" value={values.role} aria-invalid={Boolean(errors.role)} aria-describedby={errors.role ? 'role-error' : undefined} onChange={(event) => setValues({ ...values, role: event.target.value })}>
              <option value="student">Student — mengembangkan kemampuan</option>
              <option value="recruiter">Recruiter — menilai bukti kemampuan</option>
            </select>{errors.role && <p className="field-error" id="role-error">{errors.role}</p>}
          </div>}
          <Button className="full" type="submit" disabled={busy}>{busy ? 'Memproses…' : isRegister ? 'Buat akun' : 'Masuk'}<Icon name="arrow" size={18}/></Button>
        </fieldset>
      </form>
      <p className="auth-switch">{isRegister ? 'Sudah punya akun?' : 'Belum punya akun?'}{' '}
        <Link href={isRegister ? '/login' : '/register'}>{isRegister ? 'Masuk' : 'Daftar sekarang'}</Link></p>
      <p className="session-note">Sesi hanya tersimpan selama halaman ini terbuka. Muat ulang halaman untuk memulai sesi baru.</p>
    </section>
  </div>;
}

export function WorkspaceLayout({ children }) {
  const path = usePathname()?.replace(/\/$/, '') || '/';
  const items = [['/', 'Ringkasan', 'home'], ['/catalog', 'Pilih target', 'target'], ['/credentials', 'Credential', 'award'], ['/profile', 'Profil akun', 'user']];
  return <div className="workspace">
    <aside className="sidebar"><p className="eyebrow">WORKSPACE</p>
      <nav aria-label="Navigasi workspace">{items.map(([href, label, icon]) =>
        <Link key={href} href={href} aria-current={path === href ? 'page' : undefined}><Icon name={icon}/><span>{label}</span></Link>)}</nav>
      <div className="sidebar-note"><span className="eyebrow">TARGET → BUKTI</span><p>Kurikulum adalah standar penilaian kemampuan, bukan daftar materi yang wajib dibaca.</p><small>Pilih target, ukur titik awal, ikuti roadmap, lalu kirim evidence assessment. Draft demo bukan credential final.</small></div>
    </aside>{children}
  </div>;
}

export function FocusLayout({ children, exitHref, completed = 0, total = 0 }) {
  return <div className="focus-layout">
    <header className="focus-header">
      <Link className="icon-button" href={exitHref} aria-label="Tutup diagnostic dan kembali ke target"><Icon name="x"/></Link>
      <ProgressBar value={completed} max={total} label="Soal diagnostic dijawab"/>
      <span className="focus-count">{total ? `${completed} / ${total} dijawab` : 'Memuat soal'}</span>
    </header>
    {children}
  </div>;
}

function Workspace({ user, profile }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  async function refresh() {
    setBusy(true); setError('');
    try { await reloadProfile(); } catch (issue) { setError(issue.message); }
    finally { setBusy(false); }
  }
  return <WorkspaceLayout>
    <section className="workspace-content">
      <p className="eyebrow">{profile ? 'AKUN PROGRESSIO' : 'TITIK AWAL YANG BAIK'}</p>
      <h1>{profile ? 'Profil akun' : <>Halo, <span>{user.username}.</span></>}</h1>
      <p className="intro">{profile ? 'Informasi akunmu diambil langsung dari server.' : 'Akunmu siap. Perjalanan berikutnya dimulai dari tujuan yang kamu pilih.'}</p>
      {!profile && <div className="welcome-card"><div><span className="eyebrow">FONDASI PERJALANANMU</span>
        <h2>Kenali dirimu.<br />Tentukan arahmu.</h2><p>Progressio menghubungkan target keahlian, hasil penilaian, dan bukti kemampuan dalam satu perjalanan.</p>
        <Button href="/catalog">Pilih target keahlian <Icon name="arrow" size={18}/></Button></div>
        <div className="path-graphic" aria-hidden="true"><span>Target</span><i /><span>Assessment</span><i /><span>Proof</span></div>
      </div>}
      <div className="profile-card"><div className="section-heading"><h2>Identitas akun</h2><StatusBadge tone="success">Terhubung</StatusBadge></div>
        <dl><div><dt>Username</dt><dd>{user.username}</dd></div><div><dt>Email</dt><dd>{user.email || 'Belum diisi'}</dd></div>
          <div><dt>Peran</dt><dd>{roleNames[user.role] || user.role}</dd></div>
          <div><dt>Bergabung</dt><dd>{new Intl.DateTimeFormat('id-ID', { dateStyle: 'long' }).format(new Date(user.date_joined))}</dd></div></dl>
        {error && <p className="error-summary" role="alert">{error}</p>}
        <div className="profile-actions"><button className="button secondary" disabled={busy} onClick={refresh}>{busy ? 'Memuat profil…' : 'Muat ulang profil'}</button>
          <span className="hint">Profil ditampilkan sebagai informasi baca saja.</span></div>
      </div>
    </section>
  </WorkspaceLayout>;
}

export function AuthPage({ mode }) {
  const { reason } = useSession();
  const router = useRouter();
  return <AuthForm mode={mode} notice={mode === 'login' ? reason : ''}
    onRegistered={(username) => {
      logout(`Akun ${username} berhasil dibuat. Masuk dengan username dan kata sandimu.`);
      router.replace('/login');
    }} />;
}

export function WorkspacePage({ profile = false }) {
  const { user } = useSession();
  return user ? <Workspace user={user} profile={profile} /> : null;
}

export default function App({ children }) {
  const { user } = useSession();
  const route = usePathname()?.replace(/\/$/, '') || '/';
  const router = useRouter();
  const main = useRef(null);
  const publicRoute = ['/login', '/register'].includes(route);
  const privateRoute = ['/', '/profile', '/catalog', '/diagnostic', '/diagnostic/result', '/roadmap', '/study', '/assessment', '/credentials'].includes(route);
  const focusRoute = route === '/diagnostic';
  useEffect(() => {
    if (!user && privateRoute) router.replace('/login?next=' + encodeURIComponent(window.location.pathname + window.location.search));
    if (user && publicRoute) router.replace(loginDestination(new URLSearchParams(window.location.search).get('next')));
    main.current?.focus();
  }, [route, user, publicRoute, privateRoute, router]);
  const redirecting = (!user && privateRoute) || (user && publicRoute);
  return <><a className="skip-link" href="#main" onClick={(event) => { event.preventDefault(); main.current?.focus(); }}>Lewati ke konten utama</a>
    {!focusRoute && <header className="topbar"><div className="topbar-inner"><Brand /><div className="header-right">
      {user ? <><Link className="account-link" href="/profile" aria-label={`Profil ${user.username}`}><span className="account-avatar" aria-hidden="true">{user.username?.slice(0, 1).toUpperCase()}</span><span className="account-label">{roleNames[user.role] || user.role}</span></Link><Button variant="secondary" className="compact" onClick={() => { logout('Kamu sudah keluar dari akun.'); router.replace('/login'); }}><Icon name="logout" size={16}/><span>Keluar</span></Button></> : <span className="brand-tagline">Turning Progress Into Proof</span>}
    </div></div></header>}
    <main id="main" ref={main} tabIndex="-1">
      {redirecting ? <p className="not-found" role="status">Mengalihkan halaman…</p> : children}
    </main>{!focusRoute && <footer className="footer"><span>progressio<span className="brand-dot">.</span> — Setiap kemajuan punya arah.</span><span>TURNING PROGRESS INTO PROOF</span></footer>}
  </>;
}
