import { useMutation, useQuery } from "@tanstack/react-query"

import { apiClient } from "@/lib/api-client"
import type { Usuario } from "@/types/api"

export interface LoginPayload {
  login: string
  senha: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  usuario: Usuario
}

export function useLogin() {
  return useMutation({
    mutationFn: async (payload: LoginPayload) => {
      const { data } = await apiClient.post<LoginResponse>("/auth/login", payload)
      return data
    },
  })
}

export function useMe(enabled: boolean) {
  return useQuery({
    queryKey: ["auth", "me"],
    queryFn: async () => {
      const { data } = await apiClient.get<Usuario>("/auth/me")
      return data
    },
    enabled,
    retry: false,
  })
}
