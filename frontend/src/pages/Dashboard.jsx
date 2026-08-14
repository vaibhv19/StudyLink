import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { apiClient } from '../hooks/useApi';
import Card from '../components/Card';
import Badge from '../components/Badge';
import Button from '../components/Button';

export default function Dashboard() {
  const { user } = useAuthStore();
  const [dashboardData, setDashboardData] = useState({
    my_listings: [],
    my_active_requests: [],
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const response = await apiClient.get('/dashboard/owner/');
        setDashboardData(response.data);
      } catch (e) {
        console.error('Error loading dashboard overview', e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 font-sans space-y-8">
      {/* Student Welcome Banner */}
      <div className="bg-gradient-to-r from-primary/10 via-primary/5 to-accent/10 border border-primary/20 p-8 rounded-3xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 shadow-sm">
        <div className="flex items-center space-x-5">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-primary to-accent text-white font-black text-2xl flex items-center justify-center shadow-lg shadow-primary/20">
            {user?.full_name?.charAt(0) || user?.email?.charAt(0) || 'S'}
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
              Hello, {user?.full_name || 'Student'}!
            </h1>
            <p className="text-xs text-slate-500 mt-1">
              Logged in as <strong className="text-slate-700">{user?.email}</strong> • Verified Student Session
            </p>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          <Link to="/vault">
            <Button variant="primary" size="sm">
              📚 Browse Vault
            </Button>
          </Link>
          <Link to="/dashboard/owner">
            <Button variant="secondary" size="sm">
              👑 Owner Console
            </Button>
          </Link>
        </div>
      </div>

      {/* Quick Navigation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6 space-y-4">
          <div className="w-10 h-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center font-bold text-lg">
            📄
          </div>
          <div>
            <h3 className="font-bold text-slate-900 text-lg">Digital Resource Vault</h3>
            <p className="text-xs text-slate-500 mt-1">
              Access indexed exam study guides and single-doc AI tutoring.
            </p>
          </div>
          <Link
            to="/vault"
            className="text-xs font-bold text-primary hover:underline inline-flex items-center gap-1"
          >
            <span>Open Vault</span>
            <span>&rarr;</span>
          </Link>
        </Card>

        <Card className="p-6 space-y-4">
          <div className="w-10 h-10 rounded-xl bg-accent/10 text-accent flex items-center justify-center font-bold text-lg">
            🔄
          </div>
          <div>
            <h3 className="font-bold text-slate-900 text-lg">Giveaway Marketplace</h3>
            <p className="text-xs text-slate-500 mt-1">
              Find free textbooks, lab coats, and campus graphing calculators.
            </p>
          </div>
          <Link
            to="/market"
            className="text-xs font-bold text-accent hover:underline inline-flex items-center gap-1"
          >
            <span>Browse Exchange</span>
            <span>&rarr;</span>
          </Link>
        </Card>

        <Card className="p-6 space-y-4">
          <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-lg">
            📦
          </div>
          <div>
            <h3 className="font-bold text-slate-900 text-lg">Your Listings & Requests</h3>
            <p className="text-xs text-slate-500 mt-1">
              {dashboardData.my_listings?.length || 0} active listings •{' '}
              {dashboardData.my_active_requests?.length || 0} outgoing requests
            </p>
          </div>
          <Link
            to="/dashboard/owner"
            className="text-xs font-bold text-emerald-700 hover:underline inline-flex items-center gap-1"
          >
            <span>Manage Activity</span>
            <span>&rarr;</span>
          </Link>
        </Card>
      </div>
    </div>
  );
}
