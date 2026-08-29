import { create } from 'zustand';

export const useFilterStore = create((set) => ({
  subject: '',
  course: '',
  search: '',
  condition: '',
  pickupArea: '',

  setSubject: (subject) => set({ subject }),
  setCourse: (course) => set({ course }),
  setSearch: (search) => set({ search }),
  setCondition: (condition) => set({ condition }),
  setPickupArea: (pickupArea) => set({ pickupArea }),

  resetVaultFilters: () => set({ subject: '', course: '', search: '' }),
  resetMarketFilters: () => set({ subject: '', condition: '', pickupArea: '' }),
}));
