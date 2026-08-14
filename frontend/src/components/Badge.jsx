import React from 'react';

export default function Badge({
  status,
  variant, // optional manual override
  size = 'md', // 'sm' | 'md'
  className = '',
  children,
}) {
  const sizeStyles = {
    sm: 'px-2 py-0.5 text-xxs font-bold',
    md: 'px-2.5 py-1 text-xs font-semibold',
  };

  const statusMap = {
    // Vault statuses
    READY: 'bg-emerald-50 text-emerald-700 border border-emerald-200',
    PROCESSING: 'bg-amber-50 text-amber-700 border border-amber-200 animate-pulse',
    FAILED: 'bg-rose-50 text-rose-700 border border-rose-200',
    UNSEARCHABLE: 'bg-slate-100 text-slate-700 border border-slate-200',

    // Marketplace statuses
    AVAILABLE: 'border border-emerald-500 text-emerald-700 bg-emerald-50/50 font-bold',
    REQUESTED: 'bg-amber-500 text-white font-bold shadow-xs',
    GIVEN_AWAY: 'bg-slate-200 text-slate-500 line-through font-medium',
    'GIVEN AWAY': 'bg-slate-200 text-slate-500 line-through font-medium',

    // Generic variants
    primary: 'bg-primary/10 text-primary border border-primary/20',
    accent: 'bg-accent/10 text-accent border border-accent/20',
    neutral: 'bg-slate-100 text-slate-600 border border-slate-200',
  };

  const badgeStyle =
    variant ? statusMap[variant] : (statusMap[status] || statusMap.neutral);

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full leading-none tracking-wide ${sizeStyles[size] || sizeStyles.md} ${badgeStyle} ${className}`}
    >
      {status === 'PROCESSING' && (
        <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-ping"></span>
      )}
      {children || status}
    </span>
  );
}
