import { Suspense } from 'react';
import Proof from '../../Proof.jsx';
export const metadata = { title: 'Credential | Progressio' };
export default function Page() { return <Suspense fallback={<p role="status">Memuat credential…</p>}><Proof mode="credentials" /></Suspense>; }
