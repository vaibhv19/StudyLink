import { describe, it, expect, beforeEach } from 'vitest';
import { useAuthStore } from '../store/authStore';

describe('Zustand authStore', () => {
  beforeEach(() => {
    useAuthStore.getState().logout();
  });

  it('should initialize with unauthenticated null state', () => {
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.accessToken).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });

  it('should login and set user and access token in memory', () => {
    const mockUser = {
      id: 'usr-123',
      email: 'student@example.edu',
      full_name: 'Jane Doe',
    };
    const mockToken = 'mock-jwt-access-token';

    useAuthStore.getState().login(mockUser, mockToken);

    const state = useAuthStore.getState();
    expect(state.user).toEqual(mockUser);
    expect(state.accessToken).toBe(mockToken);
    expect(state.isAuthenticated).toBe(true);
  });

  it('should clear authentication state on logout', () => {
    useAuthStore.getState().login({ email: 'test@example.com' }, 'token-abc');
    expect(useAuthStore.getState().isAuthenticated).toBe(true);

    useAuthStore.getState().logout();

    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.accessToken).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });

  it('should update access token when setAccessToken is called', () => {
    useAuthStore.getState().setAccessToken('new-refreshed-token');
    const state = useAuthStore.getState();
    expect(state.accessToken).toBe('new-refreshed-token');
    expect(state.isAuthenticated).toBe(true);
  });

  it('should update profile fields without overwriting user id', () => {
    useAuthStore.getState().login(
      { id: 'usr-1', email: 'test@example.com', full_name: 'Original Name' },
      'tok-1'
    );

    useAuthStore.getState().updateProfile({ full_name: 'Updated Name' });

    const state = useAuthStore.getState();
    expect(state.user.id).toBe('usr-1');
    expect(state.user.full_name).toBe('Updated Name');
    expect(state.user.email).toBe('test@example.com');
  });
});
