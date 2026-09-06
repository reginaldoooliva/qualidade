import { CircleAlert, CircleCheck, TriangleAlert } from "lucide-react"

import type { ClassificacaoCpk } from "@/types/api"

const CONFIG: Record<ClassificacaoCpk, { label: string; icon: typeof CircleCheck; cor: string }> = {
  capaz: { label: "Capaz", icon: CircleCheck, cor: "var(--status-good)" },
  atencao: { label: "Atenção", icon: TriangleAlert, cor: "var(--status-warning)" },
  nao_capaz: { label: "Não capaz", icon: CircleAlert, cor: "var(--status-critical)" },
}

export function StatusCpkBadge({ classificacao }: { classificacao: ClassificacaoCpk | null }) {
  if (!classificacao) {
    return <span className="text-sm text-muted-foreground">Sem dados suficientes</span>
  }

  const { label, icon: Icon, cor } = CONFIG[classificacao]

  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium"
      style={{ backgroundColor: `color-mix(in oklab, ${cor} 16%, transparent)`, color: cor }}
    >
      <Icon className="size-3.5" />
      {label}
    </span>
  )
}
