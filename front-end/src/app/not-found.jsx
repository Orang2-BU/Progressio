import Link from 'next/link';

export default function NotFound() {
  return <section className="not-found"><p className="eyebrow">404</p>
    <h1>Halaman belum tersedia.</h1><p>Kembali ke workspace untuk melanjutkan.</p>
    <Link className="button primary" href="/">Kembali</Link></section>;
}
