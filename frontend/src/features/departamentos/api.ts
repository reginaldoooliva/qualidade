import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { apiClient } from "@/lib/api-client"
import type { Departamento, DepartamentoFormValues } from "@/types/api"

export function useDepartamentos(params: { busca?: string } = {}) {
  return useQuery({
    queryKey: ["departamentos", params],
    queryFn: async () => {
      const { data } = await apiClient.get<Departamento[]>("/departamentos", { params })
      return data
    },
  })
}

export function useDepartamento(departamentoId: number | undefined) {
  return useQuery({
    queryKey: ["departamentos", departamentoId],
    queryFn: async () => {
      const { data } = await apiClient.get<Departamento>(`/departamentos/${departamentoId}`)
      return data
    },
    enabled: !!departamentoId,
  })
}

export function useCreateDepartamento() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: DepartamentoFormValues) => {
      const { data } = await apiClient.post<Departamento>("/departamentos", payload)
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["departamentos"] }),
  })
}

export function useUpdateDepartamento(departamentoId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: Partial<DepartamentoFormValues>) => {
      const { data } = await apiClient.put<Departamento>(`/departamentos/${departamentoId}`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["departamentos"] })
      queryClient.invalidateQueries({ queryKey: ["departamentos", departamentoId] })
    },
  })
}

export function useToggleStatusDepartamento() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ departamentoId, ativar }: { departamentoId: number; ativar: boolean }) => {
      const { data } = await apiClient.patch<Departamento>(
        `/departamentos/${departamentoId}/${ativar ? "ativar" : "inativar"}`
      )
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["departamentos"] }),
  })
}
