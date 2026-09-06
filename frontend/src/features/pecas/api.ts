import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { apiClient } from "@/lib/api-client"
import type { Peca, PecaFormValues, PecaListItem } from "@/types/api"

export function usePecas(params: { busca?: string; cliente?: string } = {}) {
  return useQuery({
    queryKey: ["pecas", params],
    queryFn: async () => {
      const { data } = await apiClient.get<PecaListItem[]>("/pecas", { params })
      return data
    },
  })
}

export function usePeca(pecaId: number | undefined) {
  return useQuery({
    queryKey: ["pecas", pecaId],
    queryFn: async () => {
      const { data } = await apiClient.get<Peca>(`/pecas/${pecaId}`)
      return data
    },
    enabled: !!pecaId,
  })
}

export function useCreatePeca() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: PecaFormValues) => {
      const { data } = await apiClient.post<Peca>("/pecas", payload)
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["pecas"] }),
  })
}

export function useUpdatePeca(pecaId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: Partial<PecaFormValues>) => {
      const { data } = await apiClient.put<Peca>(`/pecas/${pecaId}`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pecas"] })
      queryClient.invalidateQueries({ queryKey: ["pecas", pecaId] })
    },
  })
}

export function useToggleStatusPeca() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ pecaId, ativar }: { pecaId: number; ativar: boolean }) => {
      const { data } = await apiClient.patch<Peca>(`/pecas/${pecaId}/${ativar ? "ativar" : "inativar"}`)
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["pecas"] }),
  })
}
