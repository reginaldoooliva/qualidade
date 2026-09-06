import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { apiClient } from "@/lib/api-client"
import type { Etapa, EtapaFormValues } from "@/types/api"

export function useEtapasByPeca(pecaId: number | undefined) {
  return useQuery({
    queryKey: ["pecas", pecaId, "etapas"],
    queryFn: async () => {
      const { data } = await apiClient.get<Etapa[]>(`/pecas/${pecaId}/etapas`)
      return data
    },
    enabled: !!pecaId,
  })
}

export function useEtapa(etapaId: number | undefined) {
  return useQuery({
    queryKey: ["etapas", etapaId],
    queryFn: async () => {
      const { data } = await apiClient.get<Etapa>(`/etapas/${etapaId}`)
      return data
    },
    enabled: !!etapaId,
  })
}

export function useCreateEtapa(pecaId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: EtapaFormValues) => {
      const { data } = await apiClient.post<Etapa>(`/pecas/${pecaId}/etapas`, payload)
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["pecas", pecaId, "etapas"] }),
  })
}

export function useUpdateEtapa(etapaId: number, pecaId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: Partial<EtapaFormValues>) => {
      const { data } = await apiClient.put<Etapa>(`/etapas/${etapaId}`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pecas", pecaId, "etapas"] })
      queryClient.invalidateQueries({ queryKey: ["etapas", etapaId] })
    },
  })
}

export function useInativarEtapa(pecaId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (etapaId: number) => {
      const { data } = await apiClient.patch<Etapa>(`/etapas/${etapaId}/inativar`)
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["pecas", pecaId, "etapas"] }),
  })
}
