import React from 'react';
import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div className="bg-surface-light min-h-[calc(100vh-8rem)]">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-20 pb-16 sm:pb-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center max-w-3xl mx-auto">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-bold mb-6 uppercase tracking-wider">
              <span>🎓 Digital Campus Ecosystem</span>
            </div>
            <h1 className="text-4xl sm:text-6xl font-black text-slate-900 tracking-tight leading-tight mb-6 font-sans">
              Peer-to-Peer Hub for{' '}
              <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                Study Notes & Campus Gear
              </span>
            </h1>
            <p className="text-lg sm:text-xl text-slate-600 mb-8 leading-relaxed">
              Upload study resources, search lecture summaries with single-document scoped AI, and trade campus textbooks or calculators. Built for students, powered by the community.
            </p>
            <div className="flex flex-col sm:flex-row justify-center items-center gap-4">
              <Link
                to="/vault"
                className="w-full sm:w-auto px-8 py-3.5 bg-primary hover:bg-primary-dark text-white text-base font-semibold rounded-xl shadow-lg shadow-primary/25 transition-all duration-200 text-center"
              >
                Explore Resource Vault
              </Link>
              <Link
                to="/market"
                className="w-full sm:w-auto px-8 py-3.5 bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 text-base font-semibold rounded-xl transition-all duration-200 text-center shadow-sm"
              >
                Browse Marketplace
              </Link>
            </div>
          </div>
        </div>
        
        {/* Decorative background gradients */}
        <div className="absolute top-1/2 left-1/4 -translate-y-1/2 -translate-x-1/2 w-96 h-96 bg-primary/10 rounded-full blur-3xl -z-10 pointer-events-none"></div>
        <div className="absolute top-1/3 right-1/4 -translate-y-1/2 translate-x-1/2 w-96 h-96 bg-accent/10 rounded-full blur-3xl -z-10 pointer-events-none"></div>
      </section>

      {/* Grid Highlights */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white p-8 rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition-all duration-300">
            <div className="w-12 h-12 bg-primary/10 text-primary rounded-xl flex items-center justify-center mb-6 font-bold text-xl">
              📚
            </div>
            <h2 className="text-2xl font-bold text-slate-800 mb-2">Resource Vault (The Library)</h2>
            <p className="text-slate-600 mb-6 leading-relaxed">
              Instantly share and discover lecture materials, homework solutions, and exam preparation sheets. Search documents with interactive RAG and page-level citations.
            </p>
            <Link
              to="/vault"
              className="text-primary hover:text-primary-dark font-semibold inline-flex items-center space-x-1"
            >
              <span>Explore Vault</span>
              <span>&rarr;</span>
            </Link>
          </div>

          <div className="bg-white p-8 rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition-all duration-300">
            <div className="w-12 h-12 bg-accent/10 text-accent rounded-xl flex items-center justify-center mb-6 font-bold text-xl">
              🔄
            </div>
            <h2 className="text-2xl font-bold text-slate-800 mb-2">Physical Marketplace (The Square)</h2>
            <p className="text-slate-600 mb-6 leading-relaxed">
              Declutter your dorm or find affordable equipment. Trade textbooks, graphing calculators, lab coats, and draft tools directly with fellow campus students.
            </p>
            <Link
              to="/market"
              className="text-accent hover:text-accent-dark font-semibold inline-flex items-center space-x-1"
            >
              <span>Browse Marketplace</span>
              <span>&rarr;</span>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
