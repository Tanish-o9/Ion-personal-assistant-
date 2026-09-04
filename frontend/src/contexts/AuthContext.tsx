import { createContext, ReactNode, useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';

export interface UserState {
  id: string;
  username: string;
  created_at: string;
}

interface AuthContextType {
  user: UserState | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
  login: async () => {},
  register: async () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('ion_token') || localStorage.getItem('jarvis_token'));
  const [user, setUser] = useState<UserState | null>(() => {
    const saved = localStorage.getItem('ion_user') || localStorage.getItem('jarvis_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      api.get('/auth/me')
        .then((res) => {
          setUser(res.data.user);
          localStorage.setItem('ion_user', JSON.stringify(res.data.user));
        })
        .catch(() => {
          logout();
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, [token]);

  const login = useCallback(async (username: string, password: string) => {
    setError(null);
    try {
      const res = await api.post('/auth/login', { username, password });
      const newToken = res.data.token;
      const newUser = res.data.user;

      setToken(newToken);
      setUser(newUser);
      localStorage.setItem('ion_token', newToken);
      localStorage.setItem('ion_user', JSON.stringify(newUser));
      api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Login failed';
      setError(msg);
      throw new Error(msg);
    }
  }, []);

  const register = useCallback(async (username: string, password: string) => {
    setError(null);
    try {
      const res = await api.post('/auth/register', { username, password });
      const newToken = res.data.token;
      const newUser = res.data.user;

      setToken(newToken);
      setUser(newUser);
      localStorage.setItem('ion_token', newToken);
      localStorage.setItem('ion_user', JSON.stringify(newUser));
      api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Registration failed';
      setError(msg);
      throw new Error(msg);
    }
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('ion_token');
    localStorage.removeItem('ion_user');
    localStorage.removeItem('jarvis_token');
    localStorage.removeItem('jarvis_user');
    delete api.defaults.headers.common['Authorization'];
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        error,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
