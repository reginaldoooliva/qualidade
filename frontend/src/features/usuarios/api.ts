import { useQuery } from "@tanstack/react-query"

import { apiClient } from "@/lib/api-client"
import type { Usuario } from "@/types/api"

export function useUsuarios() {
  return useQuery({
    queryKey: ["usuarios"],
    queryFn: async () => {
      const { data } = await apiClient.get<Usuario[]>("/usuarios")
      return data
    },
  })
}
