import { Suspense } from 'react';
import Diagnostic from '../../Diagnostic.jsx';

export const metadata = { title: 'Diagnostic' };
export default function Page() {
  return <Suspense fallback={<p role="status">Memuat diagnostic…</p>}><Diagnostic /></Suspense>;
}
