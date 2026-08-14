import React, { useState } from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { useAuthStore } from './store/authStore';

// Navbar Component
function Navbar() {
  const { user, isAuthenticated, logout } = useAuthStore();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-white/75 border-b border-slate-200/80 transition-all duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex items-center space-x-8">
            <Link to="/" className="flex items-center">
              <span className="text-2xl font-extrabold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent tracking-tight font-sans">
                StudyLink
              </span>
            </Link>
            <nav className="hidden md:flex space-x-1">
              <Link
                to="/vault"
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive('/vault')
                    ? 'bg-primary/10 text-primary'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                }`}
              >
                Resource Vault
              </Link>
              <Link
                to="/marketplace"
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive('/marketplace')
                    ? 'bg-primary/10 text-primary'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                }`}
              >
                Marketplace
              </Link>
              {isAuthenticated && (
                <Link
                  to="/dashboard"
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive('/dashboard')
                      ? 'bg-primary/10 text-primary'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                  }`}
                >
                  Dashboard
                </Link>
              )}
            </nav>
          </div>
          <div className="flex items-center space-x-3">
            {isAuthenticated ? (
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <img
                    src={user.avatarUrl || 'https://via.placeholder.com/32'}
                    alt={user.name}
                    className="w-8 h-8 rounded-full border border-primary/20"
                  />
                  <span className="hidden sm:inline text-sm font-medium text-slate-700">
                    {user.name}
                  </span>
                </div>
                <button
                  onClick={logout}
                  className="px-3 py-1.5 border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-lg text-sm font-medium transition-all duration-200"
                >
                  Logout
                </button>
              </div>
            ) : (
              <Link
                to="/login"
                className="px-4 py-2 bg-primary hover:bg-primary-dark text-white rounded-lg text-sm font-medium transition-all duration-200 shadow-sm shadow-primary/10"
              >
                Sign In
              </Link>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

// Landing Page View
function Home() {
  const { isAuthenticated } = useAuthStore();
  return (
    <div className="bg-surface-light min-h-[calc(100vh-4rem)]">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-20 pb-16 sm:pb-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-4xl sm:text-6xl font-extrabold text-slate-900 tracking-tight leading-none mb-6">
              The Peer-to-Peer Hub for{' '}
              <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                Digital Notes & Physical Gear
              </span>
            </h1>
            <p className="text-lg sm:text-xl text-slate-600 mb-8 leading-relaxed">
              Upload study resources, search lecture summaries with scoped RAG, and trade campus textbooks or calculators. Built for students, powered by the community.
            </p>
            <div className="flex flex-col sm:flex-row justify-center items-center gap-4">
              <Link
                to="/vault"
                className="w-full sm:w-auto px-8 py-3 bg-primary hover:bg-primary-dark text-white text-base font-semibold rounded-xl shadow-md shadow-primary/20 transition-all duration-200 text-center"
              >
                Explore Digital Vault
              </Link>
              <Link
                to="/marketplace"
                className="w-full sm:w-auto px-8 py-3 bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 text-base font-semibold rounded-xl transition-all duration-200 text-center shadow-sm"
              >
                Browse Marketplace
              </Link>
            </div>
          </div>
        </div>
        
        {/* Decorative subtle background blobs */}
        <div className="absolute top-1/2 left-1/4 -translate-y-1/2 -translate-x-1/2 w-96 h-96 bg-primary/10 rounded-full blur-3xl -z-10"></div>
        <div className="absolute top-1/3 right-1/4 -translate-y-1/2 translate-x-1/2 w-96 h-96 bg-accent/10 rounded-full blur-3xl -z-10"></div>
      </section>

      {/* Grid Highlights */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Card 1: Resource Vault */}
          <div className="bg-white p-8 rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition-all duration-300">
            <div className="w-12 h-12 bg-primary/10 text-primary rounded-xl flex items-center justify-center mb-6">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-slate-800 mb-2">Resource Vault</h2>
            <p className="text-slate-600 mb-6">
              Instantly share and discover lecture materials, homework solutions, and exam preparation sheets. Once uploaded, documents are indexed for AI-driven questioning.
            </p>
            <Link
              to="/vault"
              className="text-primary hover:text-primary-dark font-medium inline-flex items-center space-x-1"
            >
              <span>Explore Vault</span>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          </div>

          {/* Card 2: Marketplace */}
          <div className="bg-white p-8 rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition-all duration-300">
            <div className="w-12 h-12 bg-accent/10 text-accent rounded-xl flex items-center justify-center mb-6">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-slate-800 mb-2">Physical Marketplace</h2>
            <p className="text-slate-600 mb-6">
              Declutter your dorm or find affordable equipment. Trade textbooks, graphing calculators, lab coats, and draft tools directly with fellow campus students.
            </p>
            <Link
              to="/marketplace"
              className="text-accent hover:text-accent-dark font-medium inline-flex items-center space-x-1"
            >
              <span>Browse Marketplace</span>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          </div>
        </div>
      </section>

      {/* Backend / Infra Health check panel */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 border-t border-slate-200">
        <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">System Status (Phase 01 setup)</h3>
            <p className="text-sm text-slate-600">Local developer monorepo infrastructure validation panel.</p>
          </div>
          <div className="flex flex-wrap gap-4 text-xs font-semibold">
            <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
              <span className="w-2 h-2 mr-1.5 bg-emerald-500 rounded-full"></span>
              Django API: http://localhost:8000
            </span>
            <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
              <span className="w-2 h-2 mr-1.5 bg-emerald-500 rounded-full"></span>
              Supabase Postgres config: OK
            </span>
            <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
              <span className="w-2 h-2 mr-1.5 bg-emerald-500 rounded-full"></span>
              Tailwind CSS: READY
            </span>
          </div>
        </div>
      </section>
    </div>
  );
}

// Resource Vault Page
function ResourceVault() {
  const [searchTerm, setSearchTerm] = useState('');
  
  const mockResources = [
    { id: 1, title: 'CS101 Intro to Programming Lecture Notes', subject: 'CS101', code: 'CS', upvotes: 14, status: 'READY' },
    { id: 2, title: 'MATH201 Calculus II Cheat Sheet', subject: 'MATH201', code: 'MATH', upvotes: 28, status: 'READY' },
    { id: 3, title: 'PHYS103 Classical Mechanics Exam Solutions', subject: 'PHYS103', code: 'PHYS', upvotes: 9, status: 'PROCESSING' },
    { id: 4, title: 'CHEM110 Organic Chemistry Ingestion Notes', subject: 'CHEM110', code: 'CHEM', upvotes: 2, status: 'FAILED' }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Resource Vault</h1>
          <p className="text-slate-600">Discover and search shared course files.</p>
        </div>
        <button className="px-4 py-2 bg-primary text-white rounded-lg text-sm font-semibold hover:bg-primary-dark transition-all duration-200 self-start shadow-sm shadow-primary/20">
          Upload PDF
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar Filters */}
        <aside className="lg:col-span-1 space-y-6">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h3 className="font-bold text-slate-800 mb-4">Filters</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Subject Tag</label>
                <div className="space-y-2">
                  {['CS101', 'MATH201', 'PHYS103', 'CHEM110'].map(tag => (
                    <label key={tag} className="flex items-center space-x-2 text-sm text-slate-600 cursor-pointer">
                      <input type="checkbox" className="rounded text-primary focus:ring-primary w-4 h-4" />
                      <span>{tag}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </aside>

        {/* Content Area */}
        <main className="lg:col-span-3 space-y-6">
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <input
              type="text"
              placeholder="Search resource titles..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-slate-700"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {mockResources.map(res => (
              <div key={res.id} className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-all duration-200 flex flex-col justify-between">
                <div>
                  <div className="flex justify-between items-start gap-2 mb-3">
                    <span className="px-2 py-1 bg-slate-100 text-slate-600 rounded text-xs font-semibold">{res.subject}</span>
                    <span className={`px-2 py-0.5 rounded text-xxs font-bold ${
                      res.status === 'READY' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                      res.status === 'PROCESSING' ? 'bg-amber-50 text-amber-700 border border-amber-200' :
                      'bg-rose-50 text-rose-700 border border-rose-200'
                    }`}>{res.status}</span>
                  </div>
                  <h3 className="font-bold text-slate-800 text-lg mb-4 line-clamp-2">{res.title}</h3>
                </div>
                <div className="flex justify-between items-center border-t border-slate-100 pt-4 mt-2">
                  <span className="text-sm font-semibold text-slate-500 inline-flex items-center gap-1">
                    <svg className="w-4 h-4 text-amber-500" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a2 2 0 00-.8 2.4z" />
                    </svg>
                    {res.upvotes} Upvotes
                  </span>
                  <button className="text-primary hover:text-primary-dark text-sm font-bold inline-flex items-center gap-0.5">
                    <span>View Note</span>
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </main>
      </div>
    </div>
  );
}

// Marketplace Page
function Marketplace() {
  const mockItems = [
    { id: 1, title: 'Calculus Early Transcendentals 8th Edition', condition: 'Used - Good', pickup: 'Main Library Lobby', status: 'AVAILABLE', price: 'Free' },
    { id: 2, title: 'TI-84 Plus Graphing Calculator', condition: 'Used - Fair', pickup: 'Campus Student Center', status: 'REQUESTED', price: 'Free' },
    { id: 3, title: 'Organic Chemistry Model Kit', condition: 'New', pickup: 'Science Building Room 204', status: 'AVAILABLE', price: 'Free' }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Marketplace</h1>
          <p className="text-slate-600">Claim free physical books and tools left by graduates.</p>
        </div>
        <button className="px-4 py-2 bg-accent text-white rounded-lg text-sm font-semibold hover:bg-accent-dark transition-all duration-200 shadow-sm shadow-accent/20">
          Create Listing
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {mockItems.map(item => (
          <div key={item.id} className="bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-all duration-200 overflow-hidden flex flex-col justify-between">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <span className={`px-2 py-0.5 rounded text-xxs font-bold ${
                  item.status === 'AVAILABLE' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                  'bg-amber-50 text-amber-700 border border-amber-200'
                }`}>{item.status}</span>
                <span className="text-sm font-bold text-slate-500">{item.price}</span>
              </div>
              <h3 className="font-bold text-slate-800 text-lg mb-2">{item.title}</h3>
              <p className="text-sm text-slate-500 mb-4">Condition: <span className="font-medium text-slate-700">{item.condition}</span></p>
              <div className="flex items-center space-x-1.5 text-xs text-slate-500 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                <svg className="w-4 h-4 text-slate-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span className="truncate">{item.pickup}</span>
              </div>
            </div>
            <div className="p-4 bg-slate-50/50 border-t border-slate-100 flex justify-end">
              <button
                disabled={item.status !== 'AVAILABLE'}
                className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 ${
                  item.status === 'AVAILABLE'
                    ? 'bg-accent text-white hover:bg-accent-dark shadow-sm'
                    : 'bg-slate-100 text-slate-400 cursor-not-allowed'
                }`}
              >
                {item.status === 'AVAILABLE' ? 'Request Item' : 'Requested'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Login Stub Page
function Login() {
  const { login } = useAuthStore();

  const handleSocialLogin = (provider) => {
    login({
      name: `Mock ${provider} User`,
      email: 'mockstudent@example.edu',
      avatarUrl: `https://api.dicebear.com/7.x/bottts/svg?seed=${provider}`
    }, 'mock-jwt-token-abcdef');
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-slate-50/50 px-4">
      <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-xl max-w-md w-full text-center">
        <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight mb-2">Welcome to StudyLink</h2>
        <p className="text-slate-600 mb-8">Sign in to share notes and request tools.</p>
        <div className="space-y-4">
          <button
            onClick={() => handleSocialLogin('Google')}
            className="w-full flex items-center justify-center space-x-3 px-4 py-3 border border-slate-200 rounded-xl hover:bg-slate-50 text-slate-700 font-semibold transition-all duration-200 shadow-sm"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path fill="#EA4335" d="M12.24 10.285V14.4h6.887c-.275 1.565-1.88 4.604-6.887 4.604-4.33 0-7.859-3.579-7.859-8s3.529-8 7.859-8c2.46 0 4.105 1.025 5.047 1.926l3.227-3.107C18.29 1.638 15.473 1 12.24 1 6.059 1 1.05 6.009 1.05 12.2s5.009 11.2 11.19 11.2c6.457 0 10.748-4.532 10.748-10.932 0-.737-.08-1.302-.177-1.883H12.24z"/>
            </svg>
            <span>Continue with Google</span>
          </button>
          <button
            onClick={() => handleSocialLogin('GitHub')}
            className="w-full flex items-center justify-center space-x-3 px-4 py-3 bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-semibold transition-all duration-200 shadow-md shadow-slate-900/10"
          >
            <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
              <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.462-1.11-1.462-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.579.688.481C19.137 20.162 22 16.418 22 12c0-5.523-4.477-10-10-10z" />
            </svg>
            <span>Continue with GitHub</span>
          </button>
        </div>
      </div>
    </div>
  );
}

// Dashboard View
function Dashboard() {
  const { user } = useAuthStore();
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="bg-gradient-to-r from-primary/10 to-accent/10 border border-primary/20 p-8 rounded-2xl mb-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center space-x-4">
          <img
            src={user?.avatarUrl || 'https://via.placeholder.com/64'}
            alt={user?.name}
            className="w-16 h-16 rounded-full border-2 border-primary"
          />
          <div>
            <h1 className="text-2xl font-bold text-slate-800">Student Dashboard</h1>
            <p className="text-slate-600">Logged in as {user?.email}</p>
          </div>
        </div>
        <span className="px-3 py-1 bg-primary text-primary-dark font-semibold text-xs border border-primary/20 rounded-full">
          Verification: Session Active
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h2 className="text-xl font-bold text-slate-800 mb-4 pb-2 border-b border-slate-100">My Uploaded Resources</h2>
          <p className="text-sm text-slate-500 italic">No notes uploaded yet. Start sharing to see them here.</p>
        </div>
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h2 className="text-xl font-bold text-slate-800 mb-4 pb-2 border-b border-slate-100">My Marketplace Listings</h2>
          <p className="text-sm text-slate-500 italic">No items listed yet. Share physical resources with peers.</p>
        </div>
      </div>
    </div>
  );
}

// App Shell
function App() {
  return (
    <div className="min-h-screen bg-slate-50/50 flex flex-col">
      <Navbar />
      <main className="flex-grow">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/vault" element={<ResourceVault />} />
          <Route path="/marketplace" element={<Marketplace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/login" element={<Login />} />
        </Routes>
      </main>
      <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-400 font-medium">
        &copy; {new Date().getFullYear()} StudyLink Monorepo. All rights reserved.
      </footer>
    </div>
  );
}

export default App;
