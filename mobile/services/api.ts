import { API_BASE_URL, ENDPOINTS } from '../constants/config';

export type AuthUser = { id: number; email: string };

export function turkishApiError(error: unknown, fallback = 'Veriler yüklenemedi. Lütfen tekrar deneyin.'): string {
  const raw = error instanceof Error ? error.message : String(error || '');
  console.error('API Error:', error);

  if (/network request failed|failed to fetch|timed out|timeout/i.test(raw)) {
    return 'Bağlantı kurulamadı. İnterneti ve backend sunucusunu kontrol edin.';
  }
  if (/401/.test(raw)) return 'Oturumunuz sona erdi. Lütfen tekrar giriş yapın.';
  if (/403/.test(raw)) return 'Bu işlem için yetkiniz yok.';
  if (/404/.test(raw)) return 'İstenen veri bulunamadı.';
  if (/500/.test(raw)) return 'Sunucu hatası. Lütfen tekrar deneyin.';
  if (raw && !raw.startsWith('HTTP')) return raw;
  return fallback;
}

class ApiService {
  private baseUrl: string;
  private token: string | null = null;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  setToken(token: string | null) {
    this.token = token;
  }

  getToken() {
    return this.token;
  }

  private async request<T>(
    endpoint: string,
    options?: {
      params?: Record<string, string | number | undefined>;
      method?: string;
      body?: unknown;
      auth?: boolean;
    }
  ): Promise<T> {
    let url = `${this.baseUrl}${endpoint}`;

    if (options?.params) {
      const searchParams = new URLSearchParams();
      Object.entries(options.params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          searchParams.append(key, String(value));
        }
      });
      const queryString = searchParams.toString();
      if (queryString) url += `?${queryString}`;
    }

    const headers: Record<string, string> = {
      Accept: 'application/json',
    };
    if (options?.body !== undefined) {
      headers['Content-Type'] = 'application/json';
    }
    if (options?.auth !== false && this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 20000);

    try {
      const response = await fetch(url, {
        method: options?.method || 'GET',
        headers,
        body: options?.body !== undefined ? JSON.stringify(options.body) : undefined,
        signal: controller.signal,
      });

      let payload: any = null;
      const text = await response.text();
      if (text) {
        try {
          payload = JSON.parse(text);
        } catch {
          payload = text;
        }
      }

      if (!response.ok) {
        const message =
          payload?.error || payload?.message || `HTTP ${response.status}: ${response.statusText}`;
        throw new Error(message);
      }

      return payload as T;
    } catch (error: any) {
      if (error?.name === 'AbortError') {
        throw new Error('İstek zaman aşımına uğradı. Lütfen tekrar deneyin.');
      }
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    } finally {
      clearTimeout(timeout);
    }
  }

  async getHealth() {
    return this.request<{ status: string; database: string; timestamp: string }>(ENDPOINTS.health, {
      auth: false,
    });
  }

  async login(email: string, password: string) {
    const result = await this.request<{ token: string; user: AuthUser }>(ENDPOINTS.login, {
      method: 'POST',
      body: { email, password },
      auth: false,
    });
    this.setToken(result.token);
    return result;
  }

  async register(email: string, password: string) {
    const result = await this.request<{ token: string; user: AuthUser }>(ENDPOINTS.register, {
      method: 'POST',
      body: { email, password },
      auth: false,
    });
    this.setToken(result.token);
    return result;
  }

  async logout() {
    try {
      await this.request(ENDPOINTS.logout, { method: 'POST' });
    } finally {
      this.setToken(null);
    }
  }

  async getMe() {
    return this.request<{ user: AuthUser }>(ENDPOINTS.me);
  }

  async getDashboard() {
    return this.request<any>(ENDPOINTS.dashboard);
  }

  async getDatasets() {
    const result = await this.request<any>(ENDPOINTS.datasets);
    return Array.isArray(result) ? result : [];
  }

  async getDataset(id: number) {
    return this.request<any>(`${ENDPOINTS.datasets}/${id}`);
  }

  async getDatasetStats(id: number) {
    return this.request<any>(`${ENDPOINTS.datasets}/${id}/stats`);
  }

  async getReviews(params?: Record<string, string | number | undefined>) {
    const result = await this.request<any>(ENDPOINTS.reviews, { params });
    if (Array.isArray(result)) {
      return {
        data: result,
        pagination: {
          total: result.length,
          limit: result.length,
          offset: 0,
          has_more: false,
        },
      };
    }
    return {
      data: Array.isArray(result?.data) ? result.data : [],
      pagination: result?.pagination || {
        total: 0,
        limit: 20,
        offset: 0,
        has_more: false,
      },
    };
  }

  async getReview(id: number) {
    return this.request<any>(`${ENDPOINTS.reviews}/${id}`);
  }

  async getTopics(datasetId?: number) {
    const result = await this.request<any>(ENDPOINTS.topics, {
      params: datasetId ? { dataset_id: datasetId } : undefined,
    });
    return Array.isArray(result) ? result : [];
  }

  async getSentimentDistribution(datasetId?: number) {
    const result = await this.request<any>(ENDPOINTS.sentimentDistribution, {
      params: datasetId ? { dataset_id: datasetId } : undefined,
    });
    return Array.isArray(result) ? result : [];
  }

  async getRatingDistribution(datasetId?: number) {
    const result = await this.request<any>(ENDPOINTS.ratingDistribution, {
      params: datasetId ? { dataset_id: datasetId } : undefined,
    });
    return Array.isArray(result) ? result : [];
  }

  async getTopPainPoints(datasetId?: number, limit = 10) {
    const result = await this.request<any>(ENDPOINTS.topPainPoints, {
      params: { limit, ...(datasetId ? { dataset_id: datasetId } : {}) },
    });
    return Array.isArray(result) ? result : [];
  }

  async getTopFeatureRequests(datasetId?: number, limit = 10) {
    const result = await this.request<any>(ENDPOINTS.topFeatureRequests, {
      params: { limit, ...(datasetId ? { dataset_id: datasetId } : {}) },
    });
    return Array.isArray(result) ? result : [];
  }

  async getMyCompany() {
    return this.request<{ company: any }>(ENDPOINTS.companyMe);
  }

  async createCompany(data: Record<string, string | null>) {
    return this.request<any>(ENDPOINTS.companyCreate, {
      method: 'POST',
      body: data,
    });
  }

  async updateCompany(data: Record<string, string | null>) {
    return this.request<any>(ENDPOINTS.companyMe, {
      method: 'PUT',
      body: data,
    });
  }
}

export const api = new ApiService();
export default api;
