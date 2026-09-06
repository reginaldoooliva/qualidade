import axios, { type AxiosError } from "axios"

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1"
const TOKEN_KEY = "sq_token"

export const apiClient = axios.create({ baseURL: BASE_URL })

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string | null): void {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else localStorage.removeItem(TOKEN_KEY)
}

apiClient.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export interface ApiErrorBody {
  detail: string
  code: string
}

export function getApiError(error: unknown): ApiErrorBody {
  const axiosError = error as AxiosError<ApiErrorBody>
  if (axiosError.response?.data?.detail) {
    return axiosError.response.data
  }
  return { detail: "Erro inesperado. Tente novamente.", code: "ERRO_DESCONHECIDO" }
}

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401 && !error.config?.url?.includes("/auth/login")) {
      setToken(null)
      window.location.href = "/login"
    }
    return Promise.reject(error)
  }
)
