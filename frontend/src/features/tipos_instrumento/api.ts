import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { apiClient } from "@/lib/api-client"
import type { StatusCadastro, TipoInstrumento, TipoInstrumentoFormValues } from "@/types/api"

export function useTiposInstrumento(params: { busca?: string; status?: StatusCadastro } = {}) {
  return useQuery({
    queryKey: ["tipos-instrumento", params],
    queryFn: async () => {
      const { data } = await apiClient.get<TipoInstrumento[]>("/tipos-instrumento", { params })
      return data
    },
  })
}

export function useTipoInstrumento(tipoId: number | undefined) {
  return useQuery({
    queryKey: ["tipos-instrumento", tipoId],
    queryFn: async () => {
      const { data } = await apiClient.get<TipoInstrumento>(`/tipos-instrumento/${tipoId}`)
      return data
    },
    enabled: !!tipoId,
  })
}

export function useCreateTipoInstrumento() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: TipoInstrumentoFormValues) => {
      const { data } = await apiClient.post<TipoInstrumento>("/tipos-instrumento", payload)
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tipos-instrumento"] }),
  })
}

export function useUpdateTipoInstrumento(tipoId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: Partial<TipoInstrumentoFormValues>) => {
      const { data } = await apiClient.put<TipoInstrumento>(`/tipos-instrumento/${tipoId}`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tipos-instrumento"] })
      queryClient.invalidateQueries({ queryKey: ["tipos-instrumento", tipoId] })
    },
  })
}

export function useToggleStatusTipoInstrumento() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ tipoId, ativar }: { tipoId: number; ativar: boolean }) => {
      const { data } = await apiClient.patch<TipoInstrumento>(
        `/tipos-instrumento/${tipoId}/${ativar ? "ativar" : "inativar"}`
      )
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tipos-instrumento"] }),
  })
}

export function useUploadImagemTipoInstrumento() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ tipoId, arquivo }: { tipoId: number; arquivo: File }) => {
      const formData = new FormData()
      formData.append("arquivo", arquivo)
      const { data } = await apiClient.post<TipoInstrumento>(
        `/tipos-instrumento/${tipoId}/imagem`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      )
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tipos-instrumento"] }),
  })
}
