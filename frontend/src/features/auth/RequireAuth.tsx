import { Navigate, Outlet } from "react-router-dom"

import type { Perfil } from "@/types/api"
import { useAuth } from "@/features/auth/AuthContext"

export function RequireAuth({ perfis }: { perfis?: Perfil[] }) {
  const { usuario, isLoading } = useAuth()

  if (isLoading) {
    return <div className="flex h-svh items-center justify-center text-muted-foreground">Carregando...</div>
  }

  if (!usuario) {
    return <Navigate to="/login" replace />
  }

  if (perfis && !perfis.includes(usuario.perfil)) {
    return <Navigate to="/" replace />
  }

  return <Outlet />
}
