import React, { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { apiClient } from '../hooks/useApi';
import Badge from '../components/Badge';
import Button from '../components/Button';

export default function OwnerDashboard() {
  const { user } = useAuthStore();
  const [dashboardData, setDashboardData] = useState({
    my_listings: [],
    my_active_requests: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState({});

  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const response = await apiClient.get('/dashboard/owner/');
      setDashboardData(response.data);
    } catch (err) {
      console.error('Failed to load owner dashboard', err);
      setError('Unable to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  const handleAcceptRequest = async (requestId, listingId) => {
    setActionLoading((prev) => ({ ...prev, [`accept-${requestId}`]: true }));
    try {
      await apiClient.post(`/market/requests/${requestId}/accept/`);
      // Refresh full dashboard state to synchronize listing and request transitions
      await fetchDashboardData();
    } catch (err) {
      console.error('Accept request failed', err);
      const msg = err.response?.data?.message || 'Failed to accept request.';
      alert(msg);
    } finally {
      setActionLoading((prev) => ({ ...prev, [`accept-${requestId}`]: false }));
    }
  };

  const handleDeclineRequest = async (requestId) => {
    setActionLoading((prev) => ({ ...prev, [`decline-${requestId}`]: true }));
    try {
      await apiClient.post(`/market/requests/${requestId}/cancel/`);
      await fetchDashboardData();
    } catch (err) {
      console.error('Decline request failed', err);
      const msg = err.response?.data?.message || 'Failed to decline request.';
      alert(msg);
    } finally {
      setActionLoading((prev) => ({ ...prev, [`decline-${requestId}`]: false }));
    }
  };

  const handleConfirmHandoff = async (listingId) => {
    setActionLoading((prev) => ({ ...prev, [`handoff-${listingId}`]: true }));
    try {
      await apiClient.post(`/market/${listingId}/complete/`);
      await fetchDashboardData();
    } catch (err) {
      console.error('Complete handoff failed', err);
      const msg = err.response?.data?.message || 'Failed to confirm handoff.';
      alert(msg);
    } finally {
      setActionLoading((prev) => ({ ...prev, [`handoff-${listingId}`]: false }));
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center font-sans">
        <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-sm font-semibold text-slate-500">
          Loading Owner Dashboard...
        </p>
      </div>
    );
  }

  const myListings = dashboardData.my_listings || [];
  const myActiveRequests = dashboardData.my_active_requests || [];

  // Group pending requests across listings
  const pendingListingRequests = [];
  myListings.forEach((listing) => {
    if (listing.recent_requests && listing.recent_requests.length > 0) {
      listing.recent_requests.forEach((req) => {
        pendingListingRequests.push({
          ...req,
          listing_id: listing.id,
          listing_title: listing.title,
          listing_status: listing.status,
        });
      });
    }
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 font-sans space-y-10">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-primary/10 via-accent/5 to-white border border-primary/20 rounded-3xl p-8 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-primary text-white text-xs font-bold mb-2 uppercase tracking-wider">
            <span>👑 Marketplace Owner Console</span>
          </div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">
            Exchange Management Hub
          </h1>
          <p className="text-slate-600 text-sm mt-1">
            Coordinate campus giveaways, respond to student requests, and confirm physical handoffs.
          </p>
        </div>

        <Link to="/market/create">
          <Button variant="secondary" size="md">
            <span>➕ Create New Listing</span>
          </Button>
        </Link>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl text-xs font-semibold text-rose-700">
          {error}
        </div>
      )}

      {/* TOP SECTION: "Your Listings" Carousel / Grid */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-primary font-bold text-lg">📦</span>
            <h2 className="text-xl font-bold text-slate-900 tracking-tight">
              Your Listings ({myListings.length})
            </h2>
          </div>
          <span className="text-xxs uppercase tracking-wider text-slate-400 font-bold">
            Horizontal Carousel
          </span>
        </div>

        {myListings.length === 0 ? (
          <div className="bg-white p-8 rounded-2xl border border-slate-200 text-center text-slate-500 text-xs">
            You have not posted any physical items for giveaway yet.{' '}
            <Link to="/market/create" className="text-accent font-bold hover:underline">
              Create your first listing
            </Link>
          </div>
        ) : (
          <div className="flex space-x-4 overflow-x-auto pb-4 pt-1 snap-x">
            {myListings.map((item) => (
              <div
                key={item.id}
                className="flex-shrink-0 w-80 sm:w-96 bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm flex flex-col justify-between space-y-4 snap-start hover:border-slate-300 transition-all"
              >
                <div>
                  <div className="flex justify-between items-start mb-3">
                    <Badge status={item.status} size="sm" />
                    <span className="text-xxs font-mono text-slate-400 font-semibold">
                      {item.request_count} {item.request_count === 1 ? 'request' : 'requests'}
                    </span>
                  </div>

                  <h3 className="font-bold text-slate-900 text-base leading-snug line-clamp-2 mb-2">
                    <Link
                      to={`/market/${item.id}`}
                      className="hover:text-primary transition-colors"
                    >
                      {item.title}
                    </Link>
                  </h3>
                </div>

                {/* If REQUESTED, show handoff confirmation action */}
                {item.status === 'REQUESTED' ? (
                  <div className="p-3.5 bg-amber-50 rounded-xl border border-amber-200 space-y-2">
                    <div className="flex items-center justify-between text-xs text-amber-800 font-bold">
                      <span>⏳ Handoff in Progress</span>
                      <span className="text-xxs font-normal">Accepted Request</span>
                    </div>
                    {item.recent_requests && item.recent_requests.length > 0 && (
                      <p className="text-xxs text-amber-700">
                        Recipient: <strong className="font-semibold">{item.recent_requests[0].user_name}</strong>
                      </p>
                    )}
                    <Button
                      variant="primary"
                      size="sm"
                      loading={actionLoading[`handoff-${item.id}`]}
                      onClick={() => handleConfirmHandoff(item.id)}
                      className="w-full text-xs"
                    >
                      ✓ Confirm Item Handoff
                    </Button>
                  </div>
                ) : item.status === 'GIVEN_AWAY' || item.status === 'GIVEN AWAY' ? (
                  <div className="p-2.5 bg-slate-100 rounded-xl border border-slate-200 text-center text-xxs font-bold text-slate-500">
                    ✓ Handoff Completed & Item Given Away
                  </div>
                ) : (
                  <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xxs text-slate-400">
                    <span>Awaiting student requests</span>
                    <Link
                      to={`/market/${item.id}`}
                      className="font-bold text-primary hover:underline"
                    >
                      View &rarr;
                    </Link>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      {/* BOTTOM SECTION: "Pending Requests" List */}
      <section className="space-y-4">
        <div className="flex items-center space-x-2">
          <span className="text-amber-500 font-bold text-lg">📩</span>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">
            Incoming Listing Requests ({pendingListingRequests.length})
          </h2>
        </div>

        {pendingListingRequests.length === 0 ? (
          <div className="bg-white p-8 rounded-2xl border border-slate-200 text-center text-slate-400 text-xs">
            No incoming requests pending response.
          </div>
        ) : (
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden divide-y divide-slate-100">
            {pendingListingRequests.map((req) => (
              <div
                key={req.id}
                className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50/50 transition-colors"
              >
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-sm text-slate-900">
                      {req.user_name || 'Anonymous Student'}
                    </span>
                    <span className="text-xxs text-slate-400">
                      • {new Date(req.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600">
                    Requested item:{' '}
                    <strong className="font-semibold text-slate-800">
                      {req.listing_title}
                    </strong>
                  </p>
                </div>

                <div className="flex items-center space-x-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    loading={actionLoading[`decline-${req.id}`]}
                    onClick={() => handleDeclineRequest(req.id)}
                    className="text-rose-600 hover:bg-rose-50 border-rose-200"
                  >
                    Decline
                  </Button>
                  <Button
                    type="button"
                    variant="primary"
                    size="sm"
                    loading={actionLoading[`accept-${req.id}`]}
                    onClick={() => handleAcceptRequest(req.id, req.listing_id)}
                  >
                    Accept Request
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* OUTGOING REQUESTS SECTION */}
      <section className="space-y-4">
        <div className="flex items-center space-x-2">
          <span className="text-slate-400 font-bold text-lg">🚀</span>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">
            Your Outgoing Requests ({myActiveRequests.length})
          </h2>
        </div>

        {myActiveRequests.length === 0 ? (
          <div className="bg-white p-6 rounded-2xl border border-slate-200 text-center text-slate-400 text-xs">
            You have not requested any marketplace items.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {myActiveRequests.map((ar, idx) => (
              <div
                key={idx}
                className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between"
              >
                <div>
                  <h4 className="font-bold text-xs text-slate-800 line-clamp-1 mb-1">
                    {ar.listing_title}
                  </h4>
                  <span className="text-xxs text-slate-400">
                    Status: <strong className="text-slate-600">{ar.status}</strong>
                  </span>
                </div>
                <Link
                  to={`/market/${ar.listing_id}`}
                  className="text-xs font-bold text-accent hover:underline ml-3 flex-shrink-0"
                >
                  View &rarr;
                </Link>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
