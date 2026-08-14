import React, { useEffect, useState, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useFilterStore } from '../store/filterStore';
import { apiClient } from '../hooks/useApi';
import Card from '../components/Card';
import Badge from '../components/Badge';
import Button from '../components/Button';

export default function Marketplace() {
  const { isAuthenticated } = useAuthStore();
  const {
    subject,
    condition,
    pickupArea,
    setSubject,
    setCondition,
    setPickupArea,
    resetMarketFilters,
  } = useFilterStore();
  const navigate = useNavigate();

  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [subjectsList, setSubjectsList] = useState([]);

  const fetchListings = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const params = {};
      if (subject) params.subject = subject;
      if (condition) params.condition = condition;
      if (pickupArea) params.pickup_area = pickupArea;

      const response = await apiClient.get('/market/', { params });
      const data = response.data;
      const list = Array.isArray(data) ? data : data.results || [];
      setListings(list);
    } catch (err) {
      console.error('Failed to load marketplace listings', err);
      setError('Unable to load listings. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [subject, condition, pickupArea]);

  useEffect(() => {
    fetchListings();
  }, [fetchListings]);

  useEffect(() => {
    async function loadSubjects() {
      try {
        const response = await apiClient.get('/core/subjects/');
        const data = Array.isArray(response.data)
          ? response.data
          : response.data.results || [];
        setSubjectsList(data);
      } catch (e) {
        console.error('Failed to load subjects', e);
      }
    }
    loadSubjects();
  }, []);

  const hasActiveFilters = !!subject || !!condition || !!pickupArea;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 font-sans">
      {/* Marketplace Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-accent/10 text-accent text-xs font-bold mb-2 uppercase tracking-wider">
            <span>🔄 Campus Square</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
            Giveaway Marketplace
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Claim free physical textbooks, calculators, and lab tools left by campus peers.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <Button
            variant="secondary"
            size="md"
            onClick={() => {
              if (!isAuthenticated) navigate('/auth');
              else navigate('/market/create');
            }}
          >
            <span className="mr-1.5">📦</span> Give Away Item
          </Button>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-sm mb-8 space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {/* Pickup Area Search */}
          <div>
            <label className="block text-xxs font-bold text-slate-400 uppercase tracking-wider mb-1.5">
              Pickup Area
            </label>
            <input
              type="text"
              placeholder="Search pickup location..."
              value={pickupArea}
              onChange={(e) => setPickupArea(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-accent"
            />
          </div>

          {/* Condition Filter */}
          <div>
            <label className="block text-xxs font-bold text-slate-400 uppercase tracking-wider mb-1.5">
              Condition
            </label>
            <select
              value={condition}
              onChange={(e) => setCondition(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-accent bg-white"
            >
              <option value="">All Conditions</option>
              <option value="New">New</option>
              <option value="Used - Like New">Used - Like New</option>
              <option value="Used - Good">Used - Good</option>
              <option value="Used - Fair">Used - Fair</option>
            </select>
          </div>

          {/* Subject Filter */}
          <div>
            <label className="block text-xxs font-bold text-slate-400 uppercase tracking-wider mb-1.5">
              Subject
            </label>
            <select
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-accent bg-white"
            >
              <option value="">All Subjects</option>
              {subjectsList.map((s) => (
                <option key={s.id} value={s.slug}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {hasActiveFilters && (
          <div className="flex justify-end pt-2 border-t border-slate-100">
            <button
              onClick={resetMarketFilters}
              className="text-xs text-accent hover:text-accent-dark font-semibold"
            >
              Clear Filters
            </button>
          </div>
        )}
      </div>

      {/* Loading / Error States */}
      {loading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="bg-white rounded-2xl border border-slate-200/80 overflow-hidden shadow-sm animate-pulse"
            >
              <div className="h-48 bg-slate-100"></div>
              <div className="p-6 space-y-3">
                <div className="h-5 bg-slate-100 rounded w-20"></div>
                <div className="h-6 bg-slate-100 rounded w-3/4"></div>
                <div className="h-4 bg-slate-100 rounded w-1/2"></div>
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && error && (
        <div className="bg-rose-50 border border-rose-200 rounded-2xl p-8 text-center text-rose-700">
          <p className="font-semibold text-sm mb-4">{error}</p>
          <Button variant="outline" size="sm" onClick={fetchListings}>
            Retry
          </Button>
        </div>
      )}

      {!loading && !error && listings.length === 0 && (
        <div className="bg-white border border-slate-200/80 rounded-2xl p-12 text-center shadow-sm">
          <div className="w-16 h-16 rounded-2xl bg-slate-100 text-slate-400 flex items-center justify-center text-2xl mx-auto mb-4">
            📦
          </div>
          <h3 className="text-lg font-bold text-slate-800 mb-1">
            No giveaway listings found
          </h3>
          <p className="text-slate-500 text-xs max-w-sm mx-auto mb-6">
            Clear your filter criteria or pass forward textbooks and supplies you no longer need.
          </p>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => {
              if (!isAuthenticated) navigate('/auth');
              else navigate('/market/create');
            }}
          >
            Create First Listing
          </Button>
        </div>
      )}

      {/* Image-Heavy Classifieds Grid */}
      {!loading && !error && listings.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {listings.map((item) => (
            <Card
              key={item.id}
              className="overflow-hidden flex flex-col justify-between group"
            >
              {/* Photo Area with status badge */}
              <div className="relative h-52 bg-slate-100 overflow-hidden">
                {item.photo_url ? (
                  <img
                    src={item.photo_url}
                    alt={item.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-slate-400 text-3xl">
                    📷
                  </div>
                )}

                {/* Status Badge Overlay */}
                <div className="absolute top-3 right-3">
                  <Badge status={item.status} size="sm" />
                </div>

                <div className="absolute bottom-3 left-3">
                  <span className="px-2 py-0.5 rounded-md bg-white/90 backdrop-blur-md text-slate-800 text-xxs font-bold shadow-xs">
                    Free / Giveaway
                  </span>
                </div>
              </div>

              {/* Body */}
              <div className="p-5 flex-grow flex flex-col justify-between">
                <div>
                  <div className="flex items-center space-x-2 text-xxs text-slate-400 font-bold uppercase tracking-wider mb-2">
                    <span className="text-slate-600">{item.condition}</span>
                    {item.subject?.name && (
                      <>
                        <span>•</span>
                        <span className="text-accent">{item.subject.name}</span>
                      </>
                    )}
                  </div>

                  <h3 className="font-bold text-slate-900 text-base leading-snug group-hover:text-accent transition-colors line-clamp-2 mb-3">
                    <Link to={`/market/${item.id}`}>{item.title}</Link>
                  </h3>

                  {/* Pickup Area Badge */}
                  <div className="flex items-center space-x-1.5 text-xs text-slate-500 bg-slate-50 p-2.5 rounded-xl border border-slate-100 mb-4">
                    <span className="text-slate-400">📍</span>
                    <span className="truncate font-medium">{item.pickup_area}</span>
                  </div>
                </div>

                {/* Footer Link */}
                <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-xxs text-slate-400">
                    By {item.owner?.full_name || 'Campus Student'}
                  </span>
                  <Link
                    to={`/market/${item.id}`}
                    className="text-xs font-bold text-accent hover:text-accent-dark transition-colors inline-flex items-center gap-1"
                  >
                    <span>View & Request</span>
                    <span>&rarr;</span>
                  </Link>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
