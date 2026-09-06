import { Circle, CircleCheck, Clock, History, Loader, TriangleAlert } from "lucide-react"

import type { StatusAcaoCorretivaCalculado, StatusPlanoAcao } from "@/types/api"

function Badge({ label, icon: Icon, cor }: { label: string; icon: typeof Circle; cor: string }) {
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

const CONFIG_PLANO: Record<StatusPlanoAcao, { label: string; icon: typeof Circle; cor: string }> = {
  aberto: { label: "Aberto", icon: Circle, cor: "var(--muted-foreground)" },
  em_andamento: { label: "Em andamento", icon: Loader, cor: "var(--status-warning)" },
  aguardando_verificacao: { label: "Aguardando verificação", icon: Clock, cor: "var(--status-warning)" },
  encerrado: { label: "Encerrado", icon: CircleCheck, cor: "var(--status-good)" },
  reaberto: { label: "Reaberto", icon: History, cor: "var(--status-critical)" },
}

export function StatusPlanoBadge({ status }: { status: StatusPlanoAcao }) {
  const cfg = CONFIG_PLANO[status]
  return <Badge label={cfg.label} icon={cfg.icon} cor={cfg.cor} />
}

const CONFIG_ACAO: Record<StatusAcaoCorretivaCalculado, { label: string; icon: typeof Circle; cor: string }> = {
  pendente: { label: "Pendente", icon: Circle, cor: "var(--muted-foreground)" },
  concluida: { label: "Concluída", icon: CircleCheck, cor: "var(--status-good)" },
  atrasada: { label: "Atrasada", icon: TriangleAlert, cor: "var(--status-critical)" },
}

export function StatusAcaoBadge({ status }: { status: StatusAcaoCorretivaCalculado }) {
  const cfg = CONFIG_ACAO[status]
  return <Badge label={cfg.label} icon={cfg.icon} cor={cfg.cor} />
}
