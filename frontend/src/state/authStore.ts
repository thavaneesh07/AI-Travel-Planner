import { create } from "zustand";
import { register, login, getMe } from "../api/authApi";
import { User } from "../api/types";

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
  registerUser: (payload: any) => Promise<boolean>;
  loginUser: (payload: any) => Promise<boolean>;
  logout: () => void;
  loadUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem("token"),
  isAuthenticated: !!localStorage.getItem("token"),
  loading: false,
  error: null,

  registerUser: async (payload) => {
    set({ loading: true, error: null });
    try {
      const data = await register(payload);
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("refreshToken", data.refresh_token);
      set({ token: data.access_token, isAuthenticated: true, loading: false });
      const user = await getMe();
      set({ user });
      return true;
    } catch (err: any) {
      set({ error: err.response?.data?.detail || "Registration failed", loading: false });
      return false;
    }
  },

  loginUser: async (payload) => {
    set({ loading: true, error: null });
    try {
      const data = await login(payload);
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("refreshToken", data.refresh_token);
      set({ token: data.access_token, isAuthenticated: true, loading: false });
      const user = await getMe();
      set({ user });
      return true;
    } catch (err: any) {
      set({ error: err.response?.data?.detail || "Login failed", loading: false });
      return false;
    }
  },

  logout: () => {
    localStorage.removeItem("token");
    localStorage.removeItem("refreshToken");
    set({ user: null, token: null, isAuthenticated: false });
  },

  loadUser: async () => {
    const token = localStorage.getItem("token");
    if (!token) return;
    set({ loading: true });
    try {
      const user = await getMe();
      set({ user, isAuthenticated: true, loading: false });
    } catch (err) {
      localStorage.removeItem("token");
      localStorage.removeItem("refreshToken");
      set({ user: null, token: null, isAuthenticated: false, loading: false });
    }
  }
}));
