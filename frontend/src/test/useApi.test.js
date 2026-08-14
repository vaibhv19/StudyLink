import { describe, it, expect, beforeEach, vi } from 'vitest';
import axios from 'axios';
import { apiClient } from '../hooks/useApi';
import { useAuthStore } from '../store/authStore';

describe('useApi Axios Client Interceptor', () => {
  beforeEach(() => {
    useAuthStore.getState().logout();
    vi.restoreAllMocks();
  });

  it('should attach Authorization header when accessToken exists in authStore', async () => {
    useAuthStore.getState().login({ email: 'test@example.com' }, 'my-test-access-token');

    // Spy on the internal request handler
    const requestConfig = { headers: {} };
    const onFulfilled = apiClient.interceptors.request.handlers[0].fulfilled;

    const modifiedConfig = onFulfilled(requestConfig);

    expect(modifiedConfig.headers.Authorization).toBe('Bearer my-test-access-token');
  });

  it('should not attach Authorization header if accessToken is null', () => {
    useAuthStore.getState().logout();

    const requestConfig = { headers: {} };
    const onFulfilled = apiClient.interceptors.request.handlers[0].fulfilled;

    const modifiedConfig = onFulfilled(requestConfig);

    expect(modifiedConfig.headers.Authorization).toBeUndefined();
  });

  it('should attempt refresh and retry on 401 response', async () => {
    useAuthStore.getState().login({ email: 'test@example.com' }, 'expired-token');

    const refreshSpy = vi.spyOn(axios, 'post').mockResolvedValueOnce({
      data: { access: 'new-refreshed-jwt-token' },
    });

    const mockRetryResponse = { data: { success: true }, status: 200 };
    // Mock the apiClient itself for the retried call
    const originalAdapter = apiClient.defaults.adapter;
    apiClient.defaults.adapter = vi.fn().mockResolvedValueOnce(mockRetryResponse);

    const onRejected = apiClient.interceptors.response.handlers[0].rejected;

    const error401 = {
      config: { url: '/vault/', headers: {} },
      response: { status: 401 },
    };

    const result = await onRejected(error401);

    expect(refreshSpy).toHaveBeenCalledWith(
      expect.stringContaining('/auth/token/refresh/'),
      {},
      expect.objectContaining({ withCredentials: true })
    );
    expect(useAuthStore.getState().accessToken).toBe('new-refreshed-jwt-token');
    expect(result.data.success).toBe(true);

    apiClient.defaults.adapter = originalAdapter;
  });
});
