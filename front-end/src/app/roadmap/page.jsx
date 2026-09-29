import { Suspense } from 'react';
import Roadmap from '../../Roadmap.jsx';

export const metadata = { title: 'Roadmap target' };
export default function Page() {
  return <Suspense fallback={<p role="status">Memuat roadmap…</p>}><Roadmap /></Suspense>;
}
