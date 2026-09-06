import { useQuery } from "@tanstack/react-query"

import { apiClient } from "@/lib/api-client"
import { baixarArquivo } from "@/lib/download"
import type { ConsolidadoNaoConformidade, ItemConsolidadoPeca } from "@/types/api"

export interface FiltrosRelatorio {
  dataInicio?: string
  dataFim?: string
  operadorId?: number
}

export function baixarRelatorioCpkPeca(pecaId: number, codigo: string, filtros: FiltrosRelatorio = {}) {
  return baixarArquivo(
    `/relatorios/pecas/${pecaId}/cpk`,
    { data_inicio: filtros.dataInicio, data_fim: filtros.dataFim, operador_id: filtros.operadorId },
    `cpk_${codigo}.pdf`
  )
}

export function baixarRelatorioDadosBrutos(
  pecaId: number,
  codigo: string,
  etapaId: number | undefined,
  filtros: FiltrosRelatorio = {}
) {
  return baixarArquivo(
    `/relatorios/pecas/${pecaId}/dados-brutos`,
    { etapa_id: etapaId, data_inicio: filtros.dataInicio, data_fim: filtros.dataFim, operador_id: filtros.operadorId },
    `dados_brutos_${codigo}.xlsx`
  )
}

export function baixarRelatorioRnc(ncId: number, numeroRnc: string) {
  return baixarArquivo(`/relatorios/nao-conformidades/${ncId}`, {}, `${numeroRnc}.pdf`)
}

export function baixarRelatorioConsolidadoPecas() {
  return baixarArquivo("/relatorios/pecas/consolidado/pdf", {}, "consolidado_pecas.pdf")
}

export function baixarRelatorioConsolidadoNc(filtros: FiltrosRelatorio = {}) {
  return baixarArquivo(
    "/relatorios/nao-conformidades/consolidado/pdf",
    { data_inicio: filtros.dataInicio, data_fim: filtros.dataFim },
    "consolidado_nao_conformidades.pdf"
  )
}

export function useConsolidadoPecas() {
  return useQuery({
    queryKey: ["relatorios", "pecas-consolidado"],
    queryFn: async () => {
      const { data } = await apiClient.get<ItemConsolidadoPeca[]>("/relatorios/pecas/consolidado")
      return data
    },
  })
}

export function useConsolidadoNaoConformidades(filtros: FiltrosRelatorio) {
  return useQuery({
    queryKey: ["relatorios", "nc-consolidado", filtros],
    queryFn: async () => {
      const { data } = await apiClient.get<ConsolidadoNaoConformidade>("/relatorios/nao-conformidades/consolidado", {
        params: { data_inicio: filtros.dataInicio, data_fim: filtros.dataFim },
      })
      return data
    },
  })
}
