import { Circle, CircleCheck, Search, Wrench } from "lucide-react"

import type { StatusNC } from "@/types/api"

const CONFIG: Record<StatusNC, { label: string; icon: typeof Circle; cor: string }> = {
  aberta: { label: "Aberta", icon: Circle, cor: "var(--muted-foreground)" },
  em_analise: { label: "Em análise", icon: Search, cor: "var(--status-warning)" },
  em_tratamento: { label: "Em tratamento", icon: Wrench, cor: "var(--status-warning)" },
  encerrada: { label: "Encerrada", icon: CircleCheck, cor: "var(--status-good)" },
}

export function StatusNCBadge({ status }: { status: StatusNC }) {
  const { label, icon: Icon, cor } = CONFIG[status]
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
