import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ProtectedRoute from './components/ProtectedRoute';

import Home from './pages/Home';
import Auth from './pages/Auth';
import OAuthCallback from './pages/OAuthCallback';
import ResourceVault from './pages/ResourceVault';
import ResourceDetail from './pages/ResourceDetail';
import Marketplace from './pages/Marketplace';
import ListingDetail from './pages/ListingDetail';
import CreateListing from './pages/CreateListing';
import Dashboard from './pages/Dashboard';
import OwnerDashboard from './pages/OwnerDashboard';

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50/50 flex flex-col font-sans text-slate-800 antialiased selection:bg-primary/20 selection:text-primary">
      <Navbar />
      <main className="flex-grow">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/auth" element={<Auth />} />
          <Route path="/oauth-callback" element={<OAuthCallback />} />
          <Route path="/vault" element={<ResourceVault />} />
          <Route path="/vault/:id" element={<ResourceDetail />} />
          <Route path="/market" element={<Marketplace />} />
          <Route path="/market/create" element={
            <ProtectedRoute>
              <CreateListing />
            </ProtectedRoute>
          } />
          <Route path="/market/:id" element={<ListingDetail />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/owner"
            element={
              <ProtectedRoute>
                <OwnerDashboard />
              </ProtectedRoute>
            }
          />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}
