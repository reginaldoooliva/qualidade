import { NavLink } from "react-router-dom"
import {
  AlertOctagon,
  BarChart3,
  Building2,
  ClipboardCheck,
  ClipboardList,
  Cog,
  FileText,
  LayoutDashboard,
  ListChecks,
  ListTodo,
  Ruler,
  Truck,
  Users,
  Warehouse,
} from "lucide-react"

import { cn } from "@/lib/utils"
import { useAuth } from "@/features/auth/AuthContext"
import type { Perfil } from "@/types/api"

interface NavItem {
  to: string
  label: string
  icon: React.ComponentType<{ className?: string }>
  perfis?: Perfil[]
}

const NAV_ITEMS: NavItem[] = [
  { to: "/coleta/nova", label: "Coleta", icon: ListChecks },
  { to: "/analise", label: "Análise Cp/Cpk", icon: BarChart3 },
  { to: "/nao-conformidades", label: "Não Conformidade", icon: AlertOctagon },
  { to: "/planos-acao", label: "Planos de Ação", icon: ClipboardCheck },
  { to: "/acoes-departamentais", label: "Tratativas", icon: ListTodo },
  { to: "/pecas", label: "Peças", icon: ClipboardList },
  { to: "/fornecedores", label: "Fornecedores", icon: Truck },
  { to: "/maquinas", label: "Máquinas", icon: Cog },
  { to: "/departamentos", label: "Departamentos", icon: Building2 },
  { to: "/deposito-qualidade", label: "Depósito da Qualidade", icon: Warehouse },
  { to: "/tipos-instrumento", label: "Tipos de Instrumento", icon: Ruler },
  {
    to: "/relatorios",
    label: "Relatórios",
    icon: FileText,
    perfis: ["analista_qualidade", "gestor_qualidade"],
  },
  {
    to: "/usuarios",
    label: "Usuários",
    icon: Users,
    perfis: ["gestor_qualidade"],
  },
]

export function Sidebar() {
  const { usuario } = useAuth()

  const itens = NAV_ITEMS.filter((item) => !item.perfis || (usuario && item.perfis.includes(usuario.perfil)))

  return (
    <aside className="hidden w-60 shrink-0 border-r border-sidebar-border bg-sidebar text-sidebar-foreground md:flex md:flex-col">
      <div className="flex h-14 items-center gap-2 border-b border-sidebar-border px-4 font-semibold">
        <span className="flex size-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-chart-5 text-primary-foreground shadow-sm">
          <LayoutDashboard className="size-4" />
        </span>
        <span>Qualidade</span>
      </div>
      <nav className="flex-1 space-y-1 p-2">
        {itens.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-md border-l-2 border-transparent px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "border-l-chart-5 bg-sidebar-primary text-sidebar-primary-foreground"
                  : "text-sidebar-foreground/80 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
              )
            }
          >
            <Icon className="size-4" />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
