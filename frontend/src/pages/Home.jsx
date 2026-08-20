import React from 'react';
import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div className="bg-slate-50/60 min-h-[calc(100vh-8rem)]">
      {/* Hero Section */}
      <section className="pt-10 pb-8 sm:pt-12 sm:pb-10 border-b border-slate-200/70 bg-white">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto">
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 tracking-tight leading-tight mb-3.5 font-sans">
              Peer-to-peer hub for study resources and campus essentials.
            </h1>
            <p className="text-base sm:text-lg text-slate-600 max-w-xl mx-auto mb-7 leading-relaxed">
              Upload and discover course material, ask questions scoped directly to your lecture notes, and exchange textbooks or equipment with fellow students on campus.
            </p>
            <div className="flex flex-col sm:flex-row justify-center items-center gap-3">
              <Link
                to="/vault"
                className="w-full sm:w-auto px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-lg shadow-sm transition-colors duration-150 text-center"
              >
                Explore Resource Vault
              </Link>
              <Link
                to="/market"
                className="w-full sm:w-auto px-6 py-2.5 bg-white border border-slate-300 hover:bg-slate-50 hover:border-slate-400 text-slate-700 text-sm font-semibold rounded-lg transition-colors duration-150 text-center shadow-xs"
              >
                Browse Marketplace
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Product Destinations Section */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Resource Vault Card */}
          <div className="bg-white p-6 sm:p-7 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between hover:border-slate-300 transition-colors duration-150">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 border border-indigo-100 flex items-center justify-center">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
                <div>
                  <span className="text-xs font-semibold uppercase tracking-wider text-indigo-600">The Library</span>
                  <h2 className="text-lg font-bold text-slate-900">Resource Vault</h2>
                </div>
              </div>
              <p className="text-sm text-slate-600 mb-5 leading-relaxed">
                Share and access lecture slides, past exams, and study guides. Search documents with page-level citations and ask targeted questions about your course materials.
              </p>
              <div className="flex flex-wrap gap-2 mb-6">
                <span className="px-2.5 py-1 bg-slate-100 text-slate-600 text-xs font-medium rounded-md">Course Tagged</span>
                <span className="px-2.5 py-1 bg-slate-100 text-slate-600 text-xs font-medium rounded-md">PDF Documents</span>
                <span className="px-2.5 py-1 bg-slate-100 text-slate-600 text-xs font-medium rounded-md">Document Q&amp;A</span>
              </div>
            </div>
            <div>
              <Link
                to="/vault"
                className="text-sm font-semibold text-indigo-600 hover:text-indigo-800 inline-flex items-center gap-1.5 transition-colors"
              >
                <span>Go to Resource Vault</span>
                <span aria-hidden="true">&rarr;</span>
              </Link>
            </div>
          </div>

          {/* Physical Marketplace Card */}
          <div className="bg-white p-6 sm:p-7 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between hover:border-slate-300 transition-colors duration-150">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-teal-50 text-teal-700 border border-teal-100 flex items-center justify-center">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                  </svg>
                </div>
                <div>
                  <span className="text-xs font-semibold uppercase tracking-wider text-teal-700">The Square</span>
                  <h2 className="text-lg font-bold text-slate-900">Physical Marketplace</h2>
                </div>
              </div>
              <p className="text-sm text-slate-600 mb-5 leading-relaxed">
                Find textbooks, lab coats, drafting supplies, and graphing calculators from students who took the course before. Request items and coordinate direct campus handoffs.
              </p>
              <div className="flex flex-wrap gap-2 mb-6">
                <span className="px-2.5 py-1 bg-slate-100 text-slate-600 text-xs font-medium rounded-md">Textbooks &amp; Gear</span>
                <span className="px-2.5 py-1 bg-slate-100 text-slate-600 text-xs font-medium rounded-md">Free &amp; Peer Trade</span>
                <span className="px-2.5 py-1 bg-slate-100 text-slate-600 text-xs font-medium rounded-md">Campus Handoff</span>
              </div>
            </div>
            <div>
              <Link
                to="/market"
                className="text-sm font-semibold text-teal-700 hover:text-teal-900 inline-flex items-center gap-1.5 transition-colors"
              >
                <span>Go to Marketplace</span>
                <span aria-hidden="true">&rarr;</span>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

