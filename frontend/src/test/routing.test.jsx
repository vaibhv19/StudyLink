import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import ProtectedRoute from '../components/ProtectedRoute';
import Home from '../pages/Home';
import Auth from '../pages/Auth';
import Dashboard from '../pages/Dashboard';

// Mock apiClient to avoid real network calls
vi.mock('../hooks/useApi', () => ({
  apiClient: {
    get: vi.fn().mockResolvedValue({ data: { my_listings: [], my_active_requests: [] } }),
    post: vi.fn().mockResolvedValue({ data: {} }),
    interceptors: {
      request: { use: vi.fn(), handlers: [] },
      response: { use: vi.fn(), handlers: [] },
    },
  },
  default: () => ({
    get: vi.fn().mockResolvedValue({ data: { my_listings: [], my_active_requests: [] } }),
    post: vi.fn().mockResolvedValue({ data: {} }),
  }),
}));

describe('React Router & ProtectedRoute Navigation', () => {
  beforeEach(() => {
    useAuthStore.getState().logout();
  });

  it('renders Home landing page on "/"', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText(/Peer-to-Peer Hub/i)).toBeInTheDocument();
    expect(screen.getByText(/Explore Resource Vault/i)).toBeInTheDocument();
  });

  it('renders Auth page on "/auth"', () => {
    render(
      <MemoryRouter initialEntries={['/auth']}>
        <Routes>
          <Route path="/auth" element={<Auth />} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Welcome Back')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Register/i })).toBeInTheDocument();
  });

  it('redirects unauthorized users from "/dashboard" to "/auth"', () => {
    useAuthStore.getState().logout();

    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Routes>
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route path="/auth" element={<div>Auth Redirect Target</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Auth Redirect Target')).toBeInTheDocument();
    expect(screen.queryByText(/Student Dashboard/i)).not.toBeInTheDocument();
  });

  it('renders protected dashboard when user is authenticated', async () => {
    useAuthStore.getState().login(
      { id: 'usr-1', email: 'student@example.edu', full_name: 'Alex Student' },
      'valid-token'
    );

    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/dashboard']}>
          <Routes>
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route path="/auth" element={<div>Auth Page</div>} />
          </Routes>
        </MemoryRouter>
      );
    });

    expect(screen.getByText(/Hello, Alex Student!/i)).toBeInTheDocument();
  });
});
