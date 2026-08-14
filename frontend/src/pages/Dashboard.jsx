import React from 'react';
import { useAuthStore } from '../store/authStore';

export default function Dashboard() {
  const { user } = useAuthStore();
  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-black text-slate-900">Student Dashboard</h1>
      <p className="text-slate-600">Logged in as {user?.email || 'Student'}</p>
    </div>
  );
}
