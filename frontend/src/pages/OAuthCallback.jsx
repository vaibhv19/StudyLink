import React from 'react';

export default function OAuthCallback() {
  return (
    <div className="max-w-md mx-auto my-12 p-8 bg-white rounded-2xl border border-slate-200 shadow-sm text-center">
      <h1 className="text-2xl font-bold text-slate-800 mb-2">Authenticating with Provider</h1>
      <p className="text-slate-600">Processing OAuth response...</p>
    </div>
  );
}
