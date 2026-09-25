import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { apiClient } from "@/lib/api-client"
import type {
  BloqueioDeposito,
  CriarBloqueioPayload,
  LiberarBloqueioPayload,
  PecaComBloqueios,
  StatusBloqueioDeposito,
} from "@/types/api"

export function useBuscarBloqueiosPorCodigoPeca(codigoPeca: string | undefined) {
  return useQuery({
    queryKey: ["deposito-qualidade", "buscar", codigoPeca],
    queryFn: async () => {
      const { data } = await apiClient.get<PecaComBloqueios>("/deposito-qualidade/buscar", {
        params: { codigo_peca: codigoPeca },
      })
      return data
    },
    enabled: !!codigoPeca,
    retry: false,
  })
}

export function useBloqueios(params: { status?: StatusBloqueioDeposito; busca?: string } = {}) {
  return useQuery({
    queryKey: ["deposito-qualidade", params],
    queryFn: async () => {
      const { data } = await apiClient.get<BloqueioDeposito[]>("/deposito-qualidade", { params })
      return data
    },
  })
}

export function useCriarBloqueio() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: CriarBloqueioPayload) => {
      const { data } = await apiClient.post<BloqueioDeposito>("/deposito-qualidade", payload)
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["deposito-qualidade"] }),
  })
}

export function useLiberarBloqueio() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ bloqueioId, ...payload }: { bloqueioId: number } & LiberarBloqueioPayload) => {
      const { data } = await apiClient.patch<BloqueioDeposito>(
        `/deposito-qualidade/${bloqueioId}/liberar`,
        payload
      )
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["deposito-qualidade"] }),
  })
}

export function useUploadFotoBloqueio() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ bloqueioId, arquivo }: { bloqueioId: number; arquivo: File }) => {
      const formData = new FormData()
      formData.append("arquivo", arquivo)
      const { data } = await apiClient.post<BloqueioDeposito>(
        `/deposito-qualidade/${bloqueioId}/foto`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      )
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["deposito-qualidade"] }),
  })
}
