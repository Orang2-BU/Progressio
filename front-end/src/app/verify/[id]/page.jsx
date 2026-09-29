import { Suspense } from 'react';
import Proof from '../../../Proof.jsx';
export const metadata = { title: 'Verifikasi publik | Progressio' };
export default async function Page({ params }) { const { id } = await params; return <Suspense fallback={<p role="status">Memuat verifikasi…</p>}><Proof mode="verify" credentialId={id} /></Suspense>; }
