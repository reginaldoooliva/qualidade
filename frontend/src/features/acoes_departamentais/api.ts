import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { apiClient } from "@/lib/api-client"
import type { AcaoDepartamental, AcaoDepartamentalListItem } from "@/types/api"

export function useAcoesDepartamentaisPendentes(departamentoId?: number) {
  return useQuery({
    queryKey: ["acoes-departamentais", { departamentoId }],
    queryFn: async () => {
      const { data } = await apiClient.get<AcaoDepartamentalListItem[]>("/acoes-departamentais", {
        params: { departamento_id: departamentoId },
      })
      return data
    },
  })
}

export function useConcluirAcaoDepartamentalGenerico() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ ncId, acaoId, observacao }: { ncId: number; acaoId: number; observacao: string }) => {
      const { data } = await apiClient.patch<AcaoDepartamental>(
        `/nao-conformidades/${ncId}/acoes-departamentais/${acaoId}/concluir`,
        { observacao }
      )
      return data
    },
    onSuccess: (_data, { ncId }) => {
      queryClient.invalidateQueries({ queryKey: ["nao-conformidades", ncId] })
      queryClient.invalidateQueries({ queryKey: ["acoes-departamentais"] })
    },
  })
}
