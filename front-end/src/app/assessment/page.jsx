import { Suspense } from 'react';
import Proof from '../../Proof.jsx';
export const metadata = { title: 'Assessment | Progressio' };
export default function Page() { return <Suspense fallback={<p role="status">Memuat assessment…</p>}><Proof /></Suspense>; }
