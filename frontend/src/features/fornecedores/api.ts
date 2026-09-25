import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { apiClient } from "@/lib/api-client"
import type { Fornecedor, FornecedorFormValues } from "@/types/api"

export function useFornecedores(params: { busca?: string } = {}) {
  return useQuery({
    queryKey: ["fornecedores", params],
    queryFn: async () => {
      const { data } = await apiClient.get<Fornecedor[]>("/fornecedores", { params })
      return data
    },
  })
}

export function useFornecedor(fornecedorId: number | undefined) {
  return useQuery({
    queryKey: ["fornecedores", fornecedorId],
    queryFn: async () => {
      const { data } = await apiClient.get<Fornecedor>(`/fornecedores/${fornecedorId}`)
      return data
    },
    enabled: !!fornecedorId,
  })
}

export function useCreateFornecedor() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: FornecedorFormValues) => {
      const { data } = await apiClient.post<Fornecedor>("/fornecedores", payload)
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["fornecedores"] }),
  })
}

export function useUpdateFornecedor(fornecedorId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: Partial<FornecedorFormValues>) => {
      const { data } = await apiClient.put<Fornecedor>(`/fornecedores/${fornecedorId}`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["fornecedores"] })
      queryClient.invalidateQueries({ queryKey: ["fornecedores", fornecedorId] })
    },
  })
}

export function useToggleStatusFornecedor() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ fornecedorId, ativar }: { fornecedorId: number; ativar: boolean }) => {
      const { data } = await apiClient.patch<Fornecedor>(
        `/fornecedores/${fornecedorId}/${ativar ? "ativar" : "inativar"}`
      )
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["fornecedores"] }),
  })
}
