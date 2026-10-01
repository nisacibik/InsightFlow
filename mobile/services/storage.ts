import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';

const TOKEN_KEY = 'insightflow_auth_token';
const USER_KEY = 'insightflow_auth_user';


let inMemoryStorage: Record<string, string> = {};

export async function saveAuthToken(token: string): Promise<void> {
  try {
    if (Platform.OS === 'web') {
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem(TOKEN_KEY, token);
      } else {
        inMemoryStorage[TOKEN_KEY] = token;
      }
      return;
    }
    await SecureStore.setItemAsync(TOKEN_KEY, token);
  } catch (error) {
    console.warn('SecureStore save token error:', error);
    inMemoryStorage[TOKEN_KEY] = token;
  }
}

export async function getAuthToken(): Promise<string | null> {
  try {
    if (Platform.OS === 'web') {
      if (typeof localStorage !== 'undefined') {
        return localStorage.getItem(TOKEN_KEY);
      }
      return inMemoryStorage[TOKEN_KEY] || null;
    }
    return await SecureStore.getItemAsync(TOKEN_KEY);
  } catch (error) {
    console.warn('SecureStore get token error:', error);
    return inMemoryStorage[TOKEN_KEY] || null;
  }
}

export async function removeAuthToken(): Promise<void> {
  try {
    if (Platform.OS === 'web') {
      if (typeof localStorage !== 'undefined') {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
      }
      delete inMemoryStorage[TOKEN_KEY];
      delete inMemoryStorage[USER_KEY];
      return;
    }
    await SecureStore.deleteItemAsync(TOKEN_KEY);
    await SecureStore.deleteItemAsync(USER_KEY).catch(() => { });
  } catch (error) {
    console.warn('SecureStore remove token error:', error);
    delete inMemoryStorage[TOKEN_KEY];
  }
}

export async function saveStoredUser(user: any): Promise<void> {
  try {
    const raw = JSON.stringify(user);
    if (Platform.OS === 'web') {
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem(USER_KEY, raw);
      } else {
        inMemoryStorage[USER_KEY] = raw;
      }
      return;
    }
    await SecureStore.setItemAsync(USER_KEY, raw);
  } catch (error) {
    console.warn('SecureStore save user error:', error);
  }
}

export async function getStoredUser(): Promise<any | null> {
  try {
    let raw: string | null = null;
    if (Platform.OS === 'web') {
      raw = typeof localStorage !== 'undefined' ? localStorage.getItem(USER_KEY) : inMemoryStorage[USER_KEY];
    } else {
      raw = await SecureStore.getItemAsync(USER_KEY);
    }
    return raw ? JSON.parse(raw) : null;
  } catch (error) {
    console.warn('SecureStore get user error:', error);
    return null;
  }
}
