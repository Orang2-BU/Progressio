import { Suspense } from 'react';
import Study from '../../Study.jsx';

export const metadata = { title: 'Materi dan study plan' };
export default function Page() {
  return <Suspense fallback={<p role="status">Memuat materi…</p>}><Study /></Suspense>;
}
