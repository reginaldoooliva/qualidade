import { createContext, useContext, useEffect, useState, type ReactNode } from "react"

import { getToken, setToken } from "@/lib/api-client"
import type { Usuario } from "@/types/api"
import { useMe } from "@/features/auth/api"

interface AuthContextValue {
  usuario: Usuario | null
  isLoading: boolean
  login: (token: string, usuario: Usuario) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null)
  const hasToken = !!getToken()
  const { data, isLoading, isError } = useMe(hasToken)

  useEffect(() => {
    if (data) setUsuario(data)
  }, [data])

  useEffect(() => {
    if (isError) {
      setToken(null)
      setUsuario(null)
    }
  }, [isError])

  function login(token: string, novoUsuario: Usuario) {
    setToken(token)
    setUsuario(novoUsuario)
  }

  function logout() {
    setToken(null)
    setUsuario(null)
  }

  // Enquanto o token existir mas `usuario` ainda não tiver sido propagado do resultado da
  // query (o `useEffect` acima roda um frame depois de `data` chegar), continue reportando
  // "carregando" — caso contrário há uma janela em que RequireAuth vê usuario=null e
  // isLoading=false e redireciona para /login antes do estado ser atualizado.
  const effectiveLoading = hasToken && (isLoading || (!!data && !usuario))

  return (
    <AuthContext.Provider value={{ usuario, isLoading: effectiveLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) throw new Error("useAuth deve ser usado dentro de <AuthProvider>")
  return context
}
