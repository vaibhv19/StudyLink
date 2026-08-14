import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { apiClient } from '../hooks/useApi';
import AccountLinkModal from './AccountLinkModal';
import Button from '../components/Button';

export default function OAuthCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuthStore();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [conflictData, setConflictData] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const code = searchParams.get('code');
  const provider = searchParams.get('provider') || 'google';

  useEffect(() => {
    let isMounted = true;

    async function handleExchange() {
      if (!code) {
        if (isMounted) {
          setError('Authorization code is missing from callback URL.');
          setLoading(false);
        }
        return;
      }

      try {
        const response = await apiClient.post(`/auth/social/${provider}/`, {
          code,
        });

        if (isMounted) {
          login(response.data.user, response.data.access);
          navigate('/dashboard', { replace: true });
        }
      } catch (err) {
        if (!isMounted) return;

        if (err.response?.status === 409) {
          const data = err.response.data;
          setConflictData({
            email: data.email,
            provider: data.provider || provider,
            code,
            message: data.message,
          });
          setIsModalOpen(true);
        } else {
          const message =
            err.response?.data?.message ||
            'OAuth authentication failed. Please try signing in again.';
          setError(message);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    handleExchange();

    return () => {
      isMounted = false;
    };
  }, [code, provider, login, navigate]);

  return (
    <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center py-12 px-4 bg-surface-light">
      <div className="max-w-md w-full bg-white p-8 rounded-2xl border border-slate-200 shadow-xl text-center">
        {loading && (
          <div className="space-y-4 py-8">
            <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin mx-auto"></div>
            <h2 className="text-xl font-black text-slate-800 tracking-tight font-sans">
              Authenticating with {provider.charAt(0).toUpperCase() + provider.slice(1)}...
            </h2>
            <p className="text-sm text-slate-500">
              Verifying your academic identity and retrieving your session.
            </p>
          </div>
        )}

        {!loading && error && (
          <div className="space-y-6 py-4">
            <div className="w-12 h-12 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center font-bold text-xl mx-auto">
              ✕
            </div>
            <div>
              <h2 className="text-xl font-black text-slate-900 mb-2">Authentication Failed</h2>
              <p className="text-sm text-slate-600 leading-relaxed">{error}</p>
            </div>
            <Link to="/auth">
              <Button variant="primary" size="md" className="w-full">
                Return to Sign In
              </Button>
            </Link>
          </div>
        )}

        {/* Account Linking Modal Pop-up on 409 Conflict */}
        {conflictData && (
          <AccountLinkModal
            isOpen={isModalOpen}
            onClose={() => {
              setIsModalOpen(false);
              navigate('/auth', { replace: true });
            }}
            email={conflictData.email}
            provider={conflictData.provider}
            code={conflictData.code}
            message={conflictData.message}
          />
        )}
      </div>
    </div>
  );
}
