import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { apiClient } from "@/lib/api-client"
import type { Caracteristica, CaracteristicaFormValues } from "@/types/api"

export function useCaracteristicasByEtapa(etapaId: number | undefined) {
  return useQuery({
    queryKey: ["etapas", etapaId, "caracteristicas"],
    queryFn: async () => {
      const { data } = await apiClient.get<Caracteristica[]>(`/etapas/${etapaId}/caracteristicas`)
      return data
    },
    enabled: !!etapaId,
  })
}

export function useCreateCaracteristica(etapaId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: CaracteristicaFormValues) => {
      const { data } = await apiClient.post<Caracteristica>(
        `/etapas/${etapaId}/caracteristicas`,
        payload
      )
      return data
    },
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["etapas", etapaId, "caracteristicas"] }),
  })
}

export function useUpdateCaracteristica(caracteristicaId: number, etapaId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: Partial<CaracteristicaFormValues>) => {
      const { data } = await apiClient.put<Caracteristica>(
        `/caracteristicas/${caracteristicaId}`,
        payload
      )
      return data
    },
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["etapas", etapaId, "caracteristicas"] }),
  })
}

export function useInativarCaracteristica(etapaId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (caracteristicaId: number) => {
      const { data } = await apiClient.patch<Caracteristica>(
        `/caracteristicas/${caracteristicaId}/inativar`
      )
      return data
    },
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["etapas", etapaId, "caracteristicas"] }),
  })
}
