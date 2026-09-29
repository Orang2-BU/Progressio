import { Suspense } from 'react';
import Diagnostic from '../../../Diagnostic.jsx';

export const metadata = { title: 'Hasil diagnostic' };
export default function Page() {
  return <Suspense fallback={<p role="status">Memuat hasil…</p>}><Diagnostic result /></Suspense>;
}
