import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { apiClient } from '../hooks/useApi';
import Badge from '../components/Badge';
import Button from '../components/Button';

export default function ListingDetail() {
  const { id } = useParams();
  const { user, isAuthenticated } = useAuthStore();
  const navigate = useNavigate();

  const [listing, setListing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [requestLoading, setRequestLoading] = useState(false);
  const [requestSuccessMessage, setRequestSuccessMessage] = useState('');

  useEffect(() => {
    let isMounted = true;

    async function loadListing() {
      setLoading(true);
      setError('');
      try {
        const response = await apiClient.get(`/market/${id}/`);
        if (isMounted) {
          setListing(response.data);
        }
      } catch (err) {
        console.error('Failed to fetch listing', err);
        if (isMounted) {
          setError('Listing not found or failed to load.');
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    loadListing();

    return () => {
      isMounted = false;
    };
  }, [id]);

  const handleRequestItem = async () => {
    if (!isAuthenticated) {
      navigate('/auth');
      return;
    }

    setRequestLoading(true);
    setRequestSuccessMessage('');
    try {
      await apiClient.post(`/market/${id}/request/`);
      setListing((prev) => ({
        ...prev,
        has_requested: true,
      }));
      setRequestSuccessMessage(
        'Request submitted successfully! The owner has been notified.'
      );
    } catch (err) {
      console.error('Request item error:', err);
      const msg =
        err.response?.data?.message ||
        (Array.isArray(err.response?.data) && err.response.data[0]) ||
        'Unable to request item. You may have already requested it or the item is no longer available.';
      alert(msg);
    } finally {
      setRequestLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <div className="w-12 h-12 border-4 border-accent/20 border-t-accent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-sm font-semibold text-slate-500">Loading giveaway details...</p>
      </div>
    );
  }

  if (error || !listing) {
    return (
      <div className="max-w-md mx-auto my-16 p-8 bg-white rounded-2xl border border-slate-200 text-center shadow-sm">
        <div className="w-12 h-12 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center text-xl font-bold mx-auto mb-4">
          ✕
        </div>
        <h2 className="text-xl font-bold text-slate-900 mb-2">Item Unavailable</h2>
        <p className="text-xs text-slate-500 mb-6">{error || 'Could not find this listing.'}</p>
        <Link to="/market">
          <Button variant="secondary" size="md" className="w-full">
            Back to Marketplace
          </Button>
        </Link>
      </div>
    );
  }

  const isOwner = user && listing.owner && String(user.id) === String(listing.owner.id);
  const isAvailable = listing.status === 'AVAILABLE';

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 font-sans">
      <div className="mb-6 flex items-center space-x-2 text-xs text-slate-400">
        <Link to="/market" className="hover:text-accent transition-colors">
          &larr; Back to Marketplace
        </Link>
        <span>/</span>
        <span className="text-slate-600 font-medium">Listing Details</span>
      </div>

      <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden grid grid-cols-1 md:grid-cols-2">
        {/* Large Hero Image */}
        <div className="relative bg-slate-100 min-h-[350px] md:min-h-[480px] flex items-center justify-center overflow-hidden">
          {listing.photo_url ? (
            <img
              src={listing.photo_url}
              alt={listing.title}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="text-slate-400 text-6xl">📦</div>
          )}

          <div className="absolute top-4 right-4">
            <Badge status={listing.status} size="md" />
          </div>

          <div className="absolute bottom-4 left-4">
            <span className="px-3 py-1 bg-white/90 backdrop-blur-md text-slate-900 rounded-lg text-xs font-black shadow-sm">
              FREE GIVEAWAY
            </span>
          </div>
        </div>

        {/* Listing Info & Action Panel */}
        <div className="p-8 flex flex-col justify-between space-y-6">
          <div>
            <div className="flex items-center space-x-2 text-xxs font-bold text-slate-400 uppercase tracking-wider mb-2">
              <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                {listing.condition}
              </span>
              {listing.subject?.name && (
                <span className="px-2 py-0.5 rounded bg-accent/10 text-accent font-semibold">
                  {listing.subject.name}
                </span>
              )}
            </div>

            <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight mb-4">
              {listing.title}
            </h1>

            {/* Pickup Location Details */}
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100 space-y-2 mb-6">
              <div className="flex items-center space-x-2 text-xs font-bold text-slate-700">
                <span className="text-accent">📍</span>
                <span>Designated Pickup Location:</span>
              </div>
              <p className="text-xs text-slate-600 pl-5 font-medium">
                {listing.pickup_area}
              </p>
            </div>

            {/* Owner Profile */}
            <div className="flex items-center space-x-3 p-3.5 rounded-xl border border-slate-100 bg-white">
              <div className="w-10 h-10 rounded-full bg-accent/10 text-accent font-black text-sm flex items-center justify-center">
                {listing.owner?.full_name?.charAt(0) || 'U'}
              </div>
              <div>
                <p className="text-xs font-bold text-slate-900">
                  {listing.owner?.full_name || 'Campus Student'}
                </p>
                <p className="text-xxs text-slate-400">
                  Listed on StudyLink Giveaway Exchange
                </p>
              </div>
            </div>
          </div>

          {/* Action Area */}
          <div className="space-y-3 pt-6 border-t border-slate-100">
            {requestSuccessMessage && (
              <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl text-xs font-semibold text-emerald-800 flex items-center gap-2">
                <span>✓</span>
                <span>{requestSuccessMessage}</span>
              </div>
            )}

            {isOwner ? (
              <div className="space-y-3">
                <div className="p-3 bg-accent/10 border border-accent/20 rounded-xl text-xs text-accent-dark font-medium text-center">
                  You are the owner of this giveaway listing.
                </div>
                <Link to="/dashboard/owner" className="block w-full">
                  <Button variant="secondary" size="lg" className="w-full">
                    Manage in Owner Dashboard &rarr;
                  </Button>
                </Link>
              </div>
            ) : isAvailable ? (
              listing.has_requested ? (
                <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-center space-y-1">
                  <span className="text-xs font-bold text-amber-800">
                    ⏳ Request Pending
                  </span>
                  <p className="text-xxs text-amber-600">
                    You have requested this item. Check your active requests in dashboard.
                  </p>
                </div>
              ) : (
                <Button
                  variant="secondary"
                  size="lg"
                  loading={requestLoading}
                  onClick={handleRequestItem}
                  className="w-full shadow-lg shadow-accent/20"
                >
                  Request Item for Pickup
                </Button>
              )
            ) : (
              <div className="p-4 rounded-xl bg-slate-100 border border-slate-200 text-center">
                <span className="text-xs font-bold text-slate-500 uppercase">
                  Item {listing.status.replace('_', ' ')}
                </span>
                <p className="text-xxs text-slate-400 mt-0.5">
                  This item is no longer open for new requests.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
