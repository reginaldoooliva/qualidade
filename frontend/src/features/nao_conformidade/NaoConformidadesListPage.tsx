import { useState } from "react"
import { AlertTriangle, Plus } from "lucide-react"
import { useNavigate } from "react-router-dom"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useIndicadoresNC, useNaoConformidades } from "@/features/nao_conformidade/api"
import { StatusNCBadge } from "@/features/nao_conformidade/StatusNCBadge"
import type { StatusNC } from "@/types/api"

const STATUS_LABEL: Record<StatusNC, string> = {
  aberta: "Aberta",
  em_analise: "Em análise",
  em_tratamento: "Em tratamento",
  encerrada: "Encerrada",
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

export function NaoConformidadesListPage() {
  const navigate = useNavigate()
  const [status, setStatus] = useState<string>("todas")

  const { data: indicadores } = useIndicadoresNC()
  const { data: ncs, isLoading } = useNaoConformidades({
    status: status !== "todas" ? (status as StatusNC) : undefined,
  })

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Não Conformidades</h1>
        <Button onClick={() => navigate("/nao-conformidades/nova")}>
          <Plus className="size-4" />
          Abrir RNC
        </Button>
      </div>

      {indicadores && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          <IndicadorCard label="Abertas" valor={indicadores.abertas} />
          <IndicadorCard label="Em análise" valor={indicadores.em_analise} />
          <IndicadorCard label="Em tratamento" valor={indicadores.em_tratamento} />
          <IndicadorCard label="Encerradas no mês" valor={indicadores.encerradas_no_mes} />
          <IndicadorCard label="Encerradas c/ plano aberto" valor={indicadores.com_plano_aberto} destaque />
          <IndicadorCard label="Ações corretivas atrasadas" valor={indicadores.acoes_atrasadas} destaque />
        </div>
      )}

      <Card>
        <CardContent className="flex flex-wrap items-end gap-3 p-4">
          <div className="space-y-1.5">
            <Label>Status</Label>
            <Select
              value={status}
              onValueChange={(v) => setStatus(v ?? "todas")}
              items={{ todas: "Todos os status", ...STATUS_LABEL }}
            >
              <SelectTrigger className="w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todas">Todos os status</SelectItem>
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

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nº RNC</TableHead>
                <TableHead>Peça</TableHead>
                <TableHead>Descrição</TableHead>
                <TableHead>Classificação</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Plano de Ação</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-muted-foreground">
                    Carregando...
                  </TableCell>
                </TableRow>
              )}
              {!isLoading && ncs?.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-muted-foreground">
                    Nenhuma RNC encontrada.
                  </TableCell>
                </TableRow>
              )}
              {ncs?.map((nc) => (
                <TableRow
                  key={nc.id}
                  className="cursor-pointer"
                  onClick={() => navigate(`/nao-conformidades/${nc.id}`)}
                >
                  <TableCell className="font-medium">{nc.numero_rnc}</TableCell>
                  <TableCell>
                    {nc.peca_codigo} — {nc.peca_descricao}
                  </TableCell>
                  <TableCell className="max-w-xs truncate">{nc.descricao_problema}</TableCell>
                  <TableCell className="capitalize">{nc.classificacao}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <StatusNCBadge status={nc.status} />
                      {nc.tem_plano_aberto && (
                        <span title="RNC encerrada com Plano de Ação ainda em aberto">
                          <AlertTriangle className="size-4 text-amber-600" />
                        </span>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    {nc.plano_acao_id ? (
                      <Badge variant="outline">{nc.plano_acao_status}</Badge>
                    ) : (
                      <span className="text-muted-foreground">—</span>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
