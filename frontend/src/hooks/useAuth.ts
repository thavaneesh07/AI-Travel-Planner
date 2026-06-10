import { useAuthStore } from "../state/authStore";

export const useAuth = () => {
  const store = useAuthStore();
  return {
    user: store.user,
    token: store.token,
    isAuthenticated: store.isAuthenticated,
    loading: store.loading,
    error: store.error,
    register: store.registerUser,
    login: store.loginUser,
    logout: store.logout,
    loadUser: store.loadUser
  };
};
