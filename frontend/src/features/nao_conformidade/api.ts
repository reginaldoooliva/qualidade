import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { apiClient } from "@/lib/api-client"
import type {
  AbrirNCPayload,
  IndicadoresNC,
  NaoConformidadeDetalhe,
  NaoConformidadeListItem,
  StatusNC,
  TratarNCPayload,
} from "@/types/api"

export interface FiltrosNC {
  status?: StatusNC
  pecaId?: number
  classificacao?: string
  origem?: string
  responsavelAnaliseId?: number
  comPlano?: boolean
  dataInicio?: string
  dataFim?: string
}

export function useNaoConformidades(filtros: FiltrosNC) {
  return useQuery({
    queryKey: ["nao-conformidades", filtros],
    queryFn: async () => {
      const { data } = await apiClient.get<NaoConformidadeListItem[]>("/nao-conformidades", {
        params: {
          status: filtros.status,
          peca_id: filtros.pecaId,
          classificacao: filtros.classificacao,
          origem: filtros.origem,
          responsavel_analise_id: filtros.responsavelAnaliseId,
          com_plano: filtros.comPlano,
          data_inicio: filtros.dataInicio,
          data_fim: filtros.dataFim,
        },
      })
      return data
    },
  })
}

export function useIndicadoresNC() {
  return useQuery({
    queryKey: ["nao-conformidades", "indicadores"],
    queryFn: async () => {
      const { data } = await apiClient.get<IndicadoresNC>("/nao-conformidades/indicadores")
      return data
    },
  })
}

export function useNaoConformidade(ncId: number | undefined) {
  return useQuery({
    queryKey: ["nao-conformidades", ncId],
    queryFn: async () => {
      const { data } = await apiClient.get<NaoConformidadeDetalhe>(`/nao-conformidades/${ncId}`)
      return data
    },
    enabled: !!ncId,
  })
}

export function useAbrirNC() {
  return useMutation({
    mutationFn: async (payload: AbrirNCPayload) => {
      const { data } = await apiClient.post<NaoConformidadeDetalhe>("/nao-conformidades", payload)
      return data
    },
  })
}

export function useTratarNC(ncId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: TratarNCPayload) => {
      const { data } = await apiClient.patch<NaoConformidadeDetalhe>(`/nao-conformidades/${ncId}/tratamento`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["nao-conformidades", ncId] })
      queryClient.invalidateQueries({ queryKey: ["nao-conformidades", "indicadores"] })
    },
  })
}

export function useEncerrarNC(ncId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.post<NaoConformidadeDetalhe>(`/nao-conformidades/${ncId}/encerrar`)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["nao-conformidades", ncId] })
      queryClient.invalidateQueries({ queryKey: ["nao-conformidades", "indicadores"] })
    },
  })
}
