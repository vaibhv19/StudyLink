import { create } from 'zustand';

export const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: false,
  token: null,
  
  login: (userData, token) => set({
    user: userData,
    isAuthenticated: true,
    token: token
  }),
  
  logout: () => set({
    user: null,
    isAuthenticated: false,
    token: null
  }),
  
  updateProfile: (profileData) => set((state) => ({
    user: state.user ? { ...state.user, ...profileData } : null
  }))
}));
