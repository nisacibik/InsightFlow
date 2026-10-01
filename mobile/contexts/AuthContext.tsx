import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import api, { AuthUser, turkishApiError } from '../services/api';
import {
  getAuthToken,
  saveAuthToken,
  removeAuthToken,
  getStoredUser,
  saveStoredUser,
} from '../services/storage';

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);


  useEffect(() => {
    let isMounted = true;
    async function restoreSession() {
      try {
        const token = await getAuthToken();
        const cachedUser = await getStoredUser();

        if (token && isMounted) {
          api.setToken(token);
          if (cachedUser) {
            setUser(cachedUser);
          }

          try {
            const meRes = await api.getMe();
            if (isMounted && meRes?.user) {
              setUser(meRes.user);
              await saveStoredUser(meRes.user);
            }
          } catch (err) {

            console.warn('Stored token validation failed:', err);
            api.setToken(null);
            await removeAuthToken();
            if (isMounted) setUser(null);
          }
        }
      } catch (err) {
        console.warn('Session restore error:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    restoreSession();
    return () => {
      isMounted = false;
    };
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      error,
      login: async (email, password) => {
        setLoading(true);
        setError(null);
        try {
          const result = await api.login(email.trim(), password);
          await saveAuthToken(result.token);
          await saveStoredUser(result.user);
          setUser(result.user);
          return true;
        } catch (err) {
          setError(turkishApiError(err, 'Giriş yapılamadı. Bilgilerinizi kontrol edin.'));
          return false;
        } finally {
          setLoading(false);
        }
      },
      register: async (email, password) => {
        setLoading(true);
        setError(null);
        try {
          const result = await api.register(email.trim(), password);
          await saveAuthToken(result.token);
          await saveStoredUser(result.user);
          setUser(result.user);
          return true;
        } catch (err) {
          setError(turkishApiError(err, 'Kayıt tamamlanamadı. Lütfen tekrar deneyin.'));
          return false;
        } finally {
          setLoading(false);
        }
      },
      logout: async () => {
        try {
          await api.logout();
        } catch (err) {
          console.error(err);
        } finally {
          await removeAuthToken();
          api.setToken(null);
          setUser(null);
        }
      },
    }),
    [user, loading, error]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return ctx;
}
