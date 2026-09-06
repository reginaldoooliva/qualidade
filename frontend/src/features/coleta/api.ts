import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { apiClient } from "@/lib/api-client"
import type {
  FinalizarColetaPayload,
  FinalizarColetaResponse,
  IniciarColetaPayload,
  Medicao,
  OrdemProducao,
  RodadaColetaDetalhe,
} from "@/types/api"

export function useOrdemPorNumero(pecaId: number | undefined, numeroOrdem: string) {
  return useQuery({
    queryKey: ["pecas", pecaId, "ordens", numeroOrdem],
    queryFn: async () => {
      const { data } = await apiClient.get<OrdemProducao | null>(
        `/pecas/${pecaId}/ordens/${encodeURIComponent(numeroOrdem)}`
      )
      return data
    },
    enabled: !!pecaId && numeroOrdem.trim().length > 0,
  })
}

export function useIniciarColeta() {
  return useMutation({
    mutationFn: async (payload: IniciarColetaPayload) => {
      const { data } = await apiClient.post<RodadaColetaDetalhe>("/coletas/iniciar", payload)
      return data
    },
  })
}

export function useRodada(rodadaId: number | undefined) {
  return useQuery({
    queryKey: ["coletas", rodadaId],
    queryFn: async () => {
      const { data } = await apiClient.get<RodadaColetaDetalhe>(`/coletas/${rodadaId}`)
      return data
    },
    enabled: !!rodadaId,
  })
}

export function useSalvarMedicao(rodadaId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({
      caracteristicaId,
      amostraNumero,
      valor,
    }: {
      caracteristicaId: number
      amostraNumero: number
      valor: number
    }) => {
      const { data } = await apiClient.put<Medicao>(
        `/coletas/${rodadaId}/medicoes/${caracteristicaId}/${amostraNumero}`,
        { valor }
      )
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["coletas", rodadaId] }),
  })
}

export function useExcluirMedicao(rodadaId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({
      caracteristicaId,
      amostraNumero,
    }: {
      caracteristicaId: number
      amostraNumero: number
    }) => {
      await apiClient.delete(`/coletas/${rodadaId}/medicoes/${caracteristicaId}/${amostraNumero}`)
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["coletas", rodadaId] }),
  })
}

export function useFinalizarColeta(rodadaId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: FinalizarColetaPayload) => {
      const { data } = await apiClient.post<FinalizarColetaResponse>(`/coletas/${rodadaId}/finalizar`, payload)
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["coletas", rodadaId] }),
  })
}

export function useReabrirColeta() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (rodadaId: number) => {
      const { data } = await apiClient.post<RodadaColetaDetalhe>(`/coletas/${rodadaId}/reabrir`)
      return data
    },
    onSuccess: (_data, rodadaId) => queryClient.invalidateQueries({ queryKey: ["coletas", rodadaId] }),
  })
}
