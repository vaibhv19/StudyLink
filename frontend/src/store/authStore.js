import { create } from 'zustand';

export const useAuthStore = create((set, get) => ({
  user: null,
  accessToken: null,
  isAuthenticated: false,

  login: (userData, accessToken) => {
    set({
      user: userData,
      accessToken: accessToken,
      isAuthenticated: true,
    });
  },

  logout: () => {
    set({
      user: null,
      accessToken: null,
      isAuthenticated: false,
    });
  },

  setAccessToken: (accessToken) => {
    set({
      accessToken: accessToken,
      isAuthenticated: !!accessToken,
    });
  },

  setUser: (userData) => {
    set({
      user: userData,
    });
  },

  updateProfile: (profileData) => {
    const currentUser = get().user;
    set({
      user: currentUser ? { ...currentUser, ...profileData } : null,
    });
  },
}));
