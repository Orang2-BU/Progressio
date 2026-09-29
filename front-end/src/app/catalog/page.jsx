import { Suspense } from 'react';
import Catalog from '../../Catalog.jsx';

export const metadata = { title: 'Pilih target' };
export default function Page() {
  return <Suspense fallback={<p className="not-found" role="status">Memuat pilihan target…</p>}><Catalog /></Suspense>;
}
