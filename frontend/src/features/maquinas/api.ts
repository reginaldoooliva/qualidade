import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { apiClient } from "@/lib/api-client"
import type { Maquina, MaquinaFormValues } from "@/types/api"

export function useMaquinas(params: { busca?: string } = {}) {
  return useQuery({
    queryKey: ["maquinas", params],
    queryFn: async () => {
      const { data } = await apiClient.get<Maquina[]>("/maquinas", { params })
      return data
    },
  })
}

export function useMaquina(maquinaId: number | undefined) {
  return useQuery({
    queryKey: ["maquinas", maquinaId],
    queryFn: async () => {
      const { data } = await apiClient.get<Maquina>(`/maquinas/${maquinaId}`)
      return data
    },
    enabled: !!maquinaId,
  })
}

export function useCreateMaquina() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: MaquinaFormValues) => {
      const { data } = await apiClient.post<Maquina>("/maquinas", payload)
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["maquinas"] }),
  })
}

export function useUpdateMaquina(maquinaId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: Partial<MaquinaFormValues>) => {
      const { data } = await apiClient.put<Maquina>(`/maquinas/${maquinaId}`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["maquinas"] })
      queryClient.invalidateQueries({ queryKey: ["maquinas", maquinaId] })
    },
  })
}

export function useToggleStatusMaquina() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ maquinaId, ativar }: { maquinaId: number; ativar: boolean }) => {
      const { data } = await apiClient.patch<Maquina>(`/maquinas/${maquinaId}/${ativar ? "ativar" : "inativar"}`)
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["maquinas"] }),
  })
}
