import React, { useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Button from '../components/Button';

export default function OAuthCallback() {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate('/auth', { replace: true });
    }, 2000);
    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center py-12 px-4 bg-slate-50/50">
      <div className="max-w-md w-full bg-white p-8 rounded-2xl border border-slate-200 shadow-xl text-center space-y-6">
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">
          Social Authentication Deferred
        </h2>
        <p className="text-sm text-slate-600 leading-relaxed">
          StudyLink v1 uses local email and password authentication. Redirecting you to sign in...
        </p>
        <Link to="/auth">
          <Button variant="primary" size="md" className="w-full">
            Go to Sign In
          </Button>
        </Link>
      </div>
    </div>
  );
}
