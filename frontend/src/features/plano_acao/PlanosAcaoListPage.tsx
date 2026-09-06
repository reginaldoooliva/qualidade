import { useState } from "react"
import { ArrowRight, CalendarClock } from "lucide-react"
import { useNavigate } from "react-router-dom"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useIndicadoresPlanoAcao, usePlanosAcao } from "@/features/plano_acao/api"
import { StatusAcaoBadge, StatusPlanoBadge } from "@/features/plano_acao/StatusBadges"
import { formatarDataBR } from "@/lib/utils"
import type { PlanoDeAcaoListItem, StatusPlanoAcao } from "@/types/api"

const STATUS_LABEL: Record<StatusPlanoAcao, string> = {
  aberto: "Aberto",
  em_andamento: "Em andamento",
  aguardando_verificacao: "Aguardando verificação",
  encerrado: "Encerrado",
  reaberto: "Reaberto",
}

function IndicadorCard({ label, valor, destaque }: { label: string; valor: number; destaque?: boolean }) {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="text-xs text-muted-foreground">{label}</div>
        <div className={`text-2xl font-semibold tabular-nums ${destaque && valor > 0 ? "text-amber-600" : ""}`}>
          {valor}
        </div>
      </CardContent>
    </Card>
  )
}

function PlanoAcaoCard({ plano }: { plano: PlanoDeAcaoListItem }) {
  const navigate = useNavigate()

  return (
    <Card className="flex flex-col">
      <CardHeader className="space-y-1.5">
        <div className="flex items-start justify-between gap-2">
          <div>
            <div className="font-semibold">{plano.numero_rnc}</div>
            <div className="text-xs text-muted-foreground">
              {plano.peca_codigo} — {plano.peca_descricao}
            </div>
          </div>
          <div className="flex flex-col items-end gap-1">
            <StatusPlanoBadge status={plano.status} />
            {plano.ciclo > 1 && (
              <Badge variant="outline" className="text-xs">
                Ciclo {plano.ciclo}
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex flex-1 flex-col gap-3">
        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          <span>
            <span className="font-medium text-foreground">{plano.total_acoes}</span> ações
          </span>
          <span>
            <span className="font-medium text-foreground">{plano.acoes_concluidas}</span> concluídas
          </span>
          {plano.acoes_atrasadas > 0 && (
            <span className="text-destructive">
              <span className="font-medium">{plano.acoes_atrasadas}</span> atrasadas
            </span>
          )}
          {plano.proximo_prazo && (
            <span className="ml-auto flex items-center gap-1">
              <CalendarClock className="size-3.5" />
              {formatarDataBR(plano.proximo_prazo)}
            </span>
          )}
        </div>

        {plano.acoes.length === 0 ? (
          <p className="text-sm text-muted-foreground">Nenhuma ação corretiva cadastrada.</p>
        ) : (
          <ul className="space-y-2">
            {plano.acoes.map((acao) => (
              <li key={acao.id} className="rounded-md border p-2 text-sm">
                <div className="flex items-start justify-between gap-2">
                  <span className="line-clamp-2">{acao.descricao}</span>
                  <StatusAcaoBadge status={acao.status} />
                </div>
                <div className="mt-1 flex items-center justify-between text-xs text-muted-foreground">
                  <span>{acao.responsavel_nome}</span>
                  <span>Prazo: {formatarDataBR(acao.prazo)}</span>
                </div>
              </li>
            ))}
          </ul>
        )}

        <Button
          variant="outline"
          size="sm"
          className="mt-auto self-end"
          onClick={() => navigate(`/planos-acao/${plano.id}`)}
        >
          Ver plano
          <ArrowRight className="size-4" />
        </Button>
      </CardContent>
    </Card>
  )
}

export function PlanosAcaoListPage() {
  const [status, setStatus] = useState<string>("todos")

  const { data: indicadores } = useIndicadoresPlanoAcao()
  const { data: planos, isLoading } = usePlanosAcao({
    status: status !== "todos" ? (status as StatusPlanoAcao) : undefined,
  })

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold tracking-tight">Planos de Ação</h1>

      {indicadores && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
          <IndicadorCard label="Planos ativos" valor={indicadores.total_ativos} />
          <IndicadorCard label="Aguardando verificação" valor={indicadores.aguardando_verificacao} />
          <IndicadorCard label="Planos atrasados" valor={indicadores.planos_atrasados} destaque />
          <IndicadorCard label="Ações atrasadas" valor={indicadores.acoes_atrasadas} destaque />
          <IndicadorCard label="Encerrados no mês" valor={indicadores.encerrados_no_mes} />
        </div>
      )}

      <Card>
        <CardContent className="flex flex-wrap items-end gap-3 p-4">
          <div className="space-y-1.5">
            <Label>Status</Label>
            <Select
              value={status}
              onValueChange={(v) => setStatus(v ?? "todos")}
              items={{ todos: "Todos os status", ...STATUS_LABEL }}
            >
              <SelectTrigger className="w-56">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todos">Todos os status</SelectItem>
                {Object.entries(STATUS_LABEL).map(([value, label]) => (
                  <SelectItem key={value} value={value}>
                    {label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {isLoading && <p className="text-muted-foreground">Carregando...</p>}

      {!isLoading && planos?.length === 0 && (
        <Card>
          <CardContent className="p-8 text-center text-muted-foreground">
            Nenhum Plano de Ação encontrado.
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        {planos?.map((plano) => (
          <PlanoAcaoCard key={plano.id} plano={plano} />
        ))}
      </div>
    </div>
  )
}
