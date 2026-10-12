'use client';

import { useSession } from '../App.jsx';
import Dashboard from '../Dashboard.jsx';

export default function DashboardRoute() {
  const { user } = useSession();
  return user ? <Dashboard user={user} /> : null;
}
