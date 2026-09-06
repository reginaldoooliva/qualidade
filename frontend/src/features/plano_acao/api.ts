import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { apiClient } from "@/lib/api-client"
import type {
  CategoriaIshikawa,
  IndicadoresPlanoAcao,
  MetodologiaCausaRaiz,
  PlanoDeAcaoDetalhe,
  PlanoDeAcaoListItem,
  ResultadoVerificacao,
  StatusPlanoAcao,
} from "@/types/api"

export function usePlanosAcao(filtros: { status?: StatusPlanoAcao } = {}) {
  return useQuery({
    queryKey: ["planos-acao", "lista", filtros],
    queryFn: async () => {
      const { data } = await apiClient.get<PlanoDeAcaoListItem[]>("/planos-acao", { params: filtros })
      return data
    },
  })
}

export function useIndicadoresPlanoAcao() {
  return useQuery({
    queryKey: ["planos-acao", "indicadores"],
    queryFn: async () => {
      const { data } = await apiClient.get<IndicadoresPlanoAcao>("/planos-acao/indicadores")
      return data
    },
  })
}

export function usePlanoAcao(planoId: number | undefined) {
  return useQuery({
    queryKey: ["planos-acao", planoId],
    queryFn: async () => {
      const { data } = await apiClient.get<PlanoDeAcaoDetalhe>(`/planos-acao/${planoId}`)
      return data
    },
    enabled: !!planoId,
  })
}

function useInvalidatePlano(_planoId: number) {
  const queryClient = useQueryClient()
  return () => {
    queryClient.invalidateQueries({ queryKey: ["planos-acao"] })
    queryClient.invalidateQueries({ queryKey: ["nao-conformidades"] })
  }
}

export function useTrocarMetodologia(planoId: number) {
  const invalidate = useInvalidatePlano(planoId)
  return useMutation({
    mutationFn: async (metodologia: MetodologiaCausaRaiz) => {
      const { data } = await apiClient.patch<PlanoDeAcaoDetalhe>(`/planos-acao/${planoId}/metodologia`, {
        metodologia_causa_raiz: metodologia,
      })
      return data
    },
    onSuccess: invalidate,
  })
}

export function useAtualizarConclusao(planoId: number) {
  const invalidate = useInvalidatePlano(planoId)
  return useMutation({
    mutationFn: async (conclusao_causa_raiz: string) => {
      const { data } = await apiClient.patch<PlanoDeAcaoDetalhe>(`/planos-acao/${planoId}/conclusao-causa-raiz`, {
        conclusao_causa_raiz,
      })
      return data
    },
    onSuccess: invalidate,
  })
}

export function useAdicionarCausaIshikawa(planoId: number) {
  const invalidate = useInvalidatePlano(planoId)
  return useMutation({
    mutationFn: async (dados: { categoria: CategoriaIshikawa; descricao_causa: string }) => {
      const { data } = await apiClient.post<PlanoDeAcaoDetalhe>(`/planos-acao/${planoId}/causas-ishikawa`, dados)
      return data
    },
    onSuccess: invalidate,
  })
}

export function useMarcarCausaIshikawa(planoId: number) {
  const invalidate = useInvalidatePlano(planoId)
  return useMutation({
    mutationFn: async ({ causaId, marcada }: { causaId: number; marcada: boolean }) => {
      const { data } = await apiClient.patch<PlanoDeAcaoDetalhe>(
        `/planos-acao/${planoId}/causas-ishikawa/${causaId}/marcar-raiz`,
        { marcada_como_raiz: marcada }
      )
      return data
    },
    onSuccess: invalidate,
  })
}

export function useRemoverCausaIshikawa(planoId: number) {
  const invalidate = useInvalidatePlano(planoId)
  return useMutation({
    mutationFn: async (causaId: number) => {
      await apiClient.delete(`/planos-acao/${planoId}/causas-ishikawa/${causaId}`)
    },
    onSuccess: invalidate,
  })
}

export function useUpsertCausa5Porques(planoId: number) {
  const invalidate = useInvalidatePlano(planoId)
  return useMutation({
    mutationFn: async (dados: { nivel: number; pergunta: string; resposta: string }) => {
      const { data } = await apiClient.put<PlanoDeAcaoDetalhe>(`/planos-acao/${planoId}/causas-5porques`, dados)
      return data
    },
    onSuccess: invalidate,
  })
}

export function useMarcarCausa5Porques(planoId: number) {
  const invalidate = useInvalidatePlano(planoId)
  return useMutation({
    mutationFn: async ({ causaId, marcada }: { causaId: number; marcada: boolean }) => {
      const { data } = await apiClient.patch<PlanoDeAcaoDetalhe>(
        `/planos-acao/${planoId}/causas-5porques/${causaId}/marcar-raiz`,
        { marcada_como_raiz: marcada }
      )
      return data
    },
    onSuccess: invalidate,
  })
}

export function useAdicionarAcao(planoId: number) {
  const invalidate = useInvalidatePlano(planoId)
  return useMutation({
    mutationFn: async (dados: { descricao: string; responsavel_id: number; prazo: string }) => {
      const { data } = await apiClient.post<PlanoDeAcaoDetalhe>(`/planos-acao/${planoId}/acoes`, dados)
      return data
    },
    onSuccess: invalidate,
  })
}

export function useConcluirAcao(planoId: number) {
  const invalidate = useInvalidatePlano(planoId)
  return useMutation({
    mutationFn: async (acaoId: number) => {
      const { data } = await apiClient.patch<PlanoDeAcaoDetalhe>(`/planos-acao/${planoId}/acoes/${acaoId}/concluir`)
      return data
    },
    onSuccess: invalidate,
  })
}

export function useAvancarVerificacao(planoId: number) {
  const invalidate = useInvalidatePlano(planoId)
  return useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.post<PlanoDeAcaoDetalhe>(`/planos-acao/${planoId}/avancar-verificacao`)
      return data
    },
    onSuccess: invalidate,
  })
}

export function useRegistrarVerificacao(planoId: number) {
  const invalidate = useInvalidatePlano(planoId)
  return useMutation({
    mutationFn: async (dados: {
      data_verificacao: string
      responsavel_id: number
      resultado: ResultadoVerificacao
      observacoes?: string
    }) => {
      const { data } = await apiClient.post<PlanoDeAcaoDetalhe>(`/planos-acao/${planoId}/verificacao`, dados)
      return data
    },
    onSuccess: invalidate,
  })
}
