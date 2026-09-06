import { useQuery } from "@tanstack/react-query"

import { apiClient } from "@/lib/api-client"
import type { AnaliseCapabilidadeResponse, CartaControleResponse, RodadaResumo } from "@/types/api"

export interface FiltrosAnalise {
  rodadaId?: number
  dataInicio?: string
  dataFim?: string
  operadorId?: number
}

export function useRodadasParaAnalise(pecaId: number | undefined, etapaId: number | undefined) {
  return useQuery({
    queryKey: ["pecas", pecaId, "etapas", etapaId, "rodadas"],
    queryFn: async () => {
      const { data } = await apiClient.get<RodadaResumo[]>(`/pecas/${pecaId}/etapas/${etapaId}/rodadas`)
      return data
    },
    enabled: !!pecaId && !!etapaId,
  })
}

export function useAnaliseCapabilidade(
  pecaId: number | undefined,
  etapaId: number | undefined,
  filtros: FiltrosAnalise
) {
  return useQuery({
    queryKey: ["analise", pecaId, etapaId, filtros],
    queryFn: async () => {
      const { data } = await apiClient.get<AnaliseCapabilidadeResponse>(
        `/analise/pecas/${pecaId}/etapas/${etapaId}/capabilidade`,
        {
          params: {
            rodada_id: filtros.rodadaId,
            data_inicio: filtros.dataInicio,
            data_fim: filtros.dataFim,
            operador_id: filtros.operadorId,
          },
        }
      )
      return data
    },
    enabled: !!pecaId && !!etapaId,
  })
}

export function useCartaControle(
  pecaId: number | undefined,
  etapaId: number | undefined,
  filtros: FiltrosAnalise
) {
  return useQuery({
    queryKey: ["carta-controle", pecaId, etapaId, filtros],
    queryFn: async () => {
      const { data } = await apiClient.get<CartaControleResponse>(
        `/analise/pecas/${pecaId}/etapas/${etapaId}/carta-controle`,
        {
          params: {
            rodada_id: filtros.rodadaId,
            data_inicio: filtros.dataInicio,
            data_fim: filtros.dataFim,
            operador_id: filtros.operadorId,
          },
        }
      )
      return data
    },
    enabled: !!pecaId && !!etapaId,
  })
}
