import React from 'react';

export default function UpvoteButton({
  count = 0,
  hasUpvoted = false,
  onToggle,
  disabled = false,
  loading = false,
  className = '',
}) {
  return (
    <button
      type="button"
      disabled={disabled || loading}
      onClick={(e) => {
        e.preventDefault();
        e.stopPropagation();
        if (onToggle) onToggle();
      }}
      className={`inline-flex items-center rounded-full text-xs transition-all duration-200 border select-none focus:outline-none focus:ring-2 focus:ring-accent/40 ${
        hasUpvoted
          ? 'bg-accent/15 border-accent/40 text-accent font-bold shadow-xs shadow-accent/10'
          : 'bg-white hover:bg-slate-50 border-slate-200 text-slate-600 font-semibold'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:scale-105 active:scale-95'} ${className}`}
      title={hasUpvoted ? 'Remove upvote' : 'Upvote resource'}
    >
      <span className="px-2 py-1 flex items-center justify-center">
        <svg
          className={`w-3.5 h-3.5 transition-transform ${hasUpvoted ? 'text-accent fill-current scale-110' : 'text-slate-400'}`}
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fillRule="evenodd"
            d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z"
            clipRule="evenodd"
          />
        </svg>
      </span>
      <span className="h-3.5 w-px bg-slate-200" />
      <span className="px-2 py-1 font-mono text-xs">
        {loading ? '...' : count}
      </span>
    </button>
  );
}
