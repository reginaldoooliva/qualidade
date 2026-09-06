import { LogOut } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/features/auth/AuthContext"

const PERFIL_LABEL: Record<string, string> = {
  operador: "Operador",
  analista_qualidade: "Analista de Qualidade",
  gestor_qualidade: "Gestor de Qualidade",
}

export function Topbar() {
  const { usuario, logout } = useAuth()

  return (
    <header className="flex h-14 items-center justify-between border-b bg-background px-4">
      <div className="text-sm font-medium text-primary md:hidden">Qualidade</div>
      <div />
      <div className="flex items-center gap-3">
        {usuario && (
          <div className="flex items-center gap-2 text-right text-sm leading-tight">
            <div className="hidden sm:block">
              <div className="font-medium">{usuario.nome}</div>
            </div>
            <Badge variant="secondary">{PERFIL_LABEL[usuario.perfil]}</Badge>
          </div>
        )}
        <Button variant="ghost" size="icon" onClick={logout} title="Sair">
          <LogOut className="size-4" />
        </Button>
      </div>
    </header>
  )
}
