import Link from 'next/link';

const paths = {
  home: <><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/></>,
  target: <><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></>,
  chart: <><path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/></>,
  route: <><circle cx="6" cy="19" r="3"/><path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/><circle cx="18" cy="5" r="3"/></>,
  book: <><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></>,
  shield: <><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/></>,
  award: <><circle cx="12" cy="8" r="6"/><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"/></>,
  user: <><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></>,
  check: <path d="M20 6 9 17l-5-5"/>,
  info: <><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></>,
  warning: <><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/></>,
  x: <><path d="M18 6 6 18"/><path d="m6 6 12 12"/></>,
  lock: <><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></>,
  arrow: <><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></>,
  logout: <><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></>,
};

export function Icon({ name, size = 20, className = '', label }) {
  if (!paths[name]) return null;
  return <svg className={className} width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" role={label ? 'img' : undefined} aria-label={label} aria-hidden={label ? undefined : true}>{paths[name]}</svg>;
}

export function Button({ href, variant = 'primary', className = '', children, ...props }) {
  const classes = `button ${variant} ${className}`.trim();
  return href ? <Link className={classes} href={href} {...props}>{children}</Link> : <button className={classes} {...props}>{children}</button>;
}

const noticeIcons = { success: 'check', info: 'info', warning: 'warning', error: 'x' };
const noticeLabels = { success: 'Berhasil', info: 'Informasi', warning: 'Perhatian', error: 'Kesalahan' };
export function Notice({ tone = 'info', title, children, className = '', ...props }) {
  const kind = noticeIcons[tone] ? tone : 'info';
  return <div className={`ui-notice ui-notice-${kind} ${className}`.trim()} role={kind === 'error' ? 'alert' : 'status'} {...props}>
    <Icon name={noticeIcons[kind]} size={20}/><div><strong>{title || noticeLabels[kind]}</strong>{children && <div>{children}</div>}</div>
  </div>;
}

export function StatusBadge({ tone = 'info', children, className = '' }) {
  if (!children) return null;
  const kind = noticeIcons[tone] ? tone : 'info';
  return <span className={`ui-status ui-status-${kind} ${className}`.trim()}>{children}</span>;
}

export function ProgressBar({ value, max, label = 'Progres', className = '' }) {
  const hasTotal = Number.isFinite(max) && max > 0;
  const safeMax = hasTotal ? max : 1;
  const safeValue = Number.isFinite(value) ? Math.min(safeMax, Math.max(0, value)) : 0;
  return <div className={`ui-progress ${className}`.trim()} role="progressbar" aria-label={label} aria-valuemin={0} aria-valuemax={hasTotal ? safeMax : undefined} aria-valuenow={hasTotal ? safeValue : undefined} aria-valuetext={hasTotal ? undefined : 'Total belum tersedia'}>
    <span style={{ width: `${safeValue / safeMax * 100}%` }}/>
  </div>;
}

export function DifficultyTag({ level }) {
  const labels = { beginner: 'Pemula', intermediate: 'Menengah', advanced: 'Mahir', pemula: 'Pemula', menengah: 'Menengah', mahir: 'Mahir' };
  const key = String(level || '').toLowerCase();
  return labels[key] ? <span className={`ui-difficulty ui-difficulty-${key}`}>{labels[key]}</span> : null;
}

const journeySteps = [
  ['Target', 'target'], ['Diagnostic', 'chart'], ['Roadmap', 'route'], ['Study', 'book'], ['Bukti', 'shield'],
];
export function JourneyTracker({ statuses, className = '' }) {
  return <ol className={`ui-journey ${className}`.trim()} aria-label="Tahapan perjalanan">
    {journeySteps.map(([label, icon], index) => {
      const state = statuses?.[index] || 'upcoming';
      const statusLabel = state === 'complete' ? 'selesai' : state === 'current' ? 'langkah saat ini' : state === 'locked' ? 'terkunci' : 'belum dimulai';
      return <li className={`ui-journey-${state}`} key={label} aria-current={state === 'current' ? 'step' : undefined} aria-label={`${label}, ${statusLabel}`}>
        <span className="ui-journey-node"><Icon name={state === 'complete' ? 'check' : state === 'locked' ? 'lock' : icon} size={18}/></span>
        <span className="ui-journey-copy"><span className="ui-journey-label">{label}</span><span className="ui-journey-status">{statusLabel}</span></span>
      </li>;
    })}
  </ol>;
}

export function EmptyState({ icon = 'info', title, children, action }) {
  return <div className="ui-empty" role="status"><span className="ui-empty-icon"><Icon name={icon} size={32}/></span><h2>{title}</h2><p>{children}</p>{action}</div>;
}

export function LoadingState({ children = 'Memuat…' }) {
  return <p className="ui-loading" role="status"><span className="ui-loading-dot" aria-hidden="true"/>{children}</p>;
}
