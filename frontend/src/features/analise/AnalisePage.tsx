import { useEffect, useState } from "react"
import { AlertTriangle } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useAnaliseCapabilidade, useCartaControle } from "@/features/analise/api"
import { CartaControleChart } from "@/features/analise/CartaControleChart"
import { HistogramaChart } from "@/features/analise/HistogramaChart"
import { StatusCpkBadge } from "@/features/analise/StatusCpkBadge"
import { useEtapasByPeca } from "@/features/etapas/api"
import { PecaBuscaInput } from "@/features/pecas/PecaBuscaInput"
import type { CartaControleCaracteristica, PecaListItem } from "@/types/api"

const STATUS_RODADA_LABEL: Record<string, string> = {
  finalizada: "Finalizada",
  finalizada_com_pendencia: "Com pendência",
}

export function AnalisePage() {
  const [peca, setPeca] = useState<PecaListItem | null>(null)
  const { data: etapas } = useEtapasByPeca(peca?.id)
  const [etapaId, setEtapaId] = useState<string>("")

  const [rodadaId, setRodadaId] = useState<string>("todas")
  const [dataInicio, setDataInicio] = useState("")
  const [dataFim, setDataFim] = useState("")
  const [operadorId, setOperadorId] = useState<string>("todos")

  useEffect(() => {
    setEtapaId("")
  }, [peca?.id])

  useEffect(() => {
    setRodadaId("todas")
    setDataInicio("")
    setDataFim("")
    setOperadorId("todos")
  }, [etapaId])

  const etapaIdNum = etapaId ? Number(etapaId) : undefined

  const etapasAtivas = etapas?.filter((e) => e.status === "ativo") ?? []
  const etapaItems = Object.fromEntries(
    etapasAtivas.map((e) => [String(e.id), `Etapa ${e.numero_etapa}${e.descricao ? ` — ${e.descricao}` : ""}`])
  )

  const filtrosAtivos = {
    rodadaId: rodadaId !== "todas" ? Number(rodadaId) : undefined,
    dataInicio: dataInicio || undefined,
    dataFim: dataFim || undefined,
    operadorId: operadorId !== "todos" ? Number(operadorId) : undefined,
  }
  const { data: analise, isLoading } = useAnaliseCapabilidade(peca?.id, etapaIdNum, filtrosAtivos)
  const { data: cartaControle } = useCartaControle(peca?.id, etapaIdNum, filtrosAtivos)

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold tracking-tight">Análise Cp/Cpk</h1>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Peça e etapa</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <PecaBuscaInput value={peca} onChange={setPeca} />
          {peca && (
            <Select value={etapaId} onValueChange={(v) => setEtapaId(v ?? "")} items={etapaItems}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Selecione a etapa" />
              </SelectTrigger>
              <SelectContent>
                {etapasAtivas.map((e) => (
                  <SelectItem key={e.id} value={String(e.id)}>
                    {etapaItems[String(e.id)]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        </CardContent>
      </Card>

      {etapaIdNum && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Filtros</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <div className="space-y-1.5">
                <Label>Rodada</Label>
                <Select
                  value={rodadaId}
                  onValueChange={(v) => setRodadaId(v ?? "todas")}
                  items={{
                    todas: "Todas as rodadas",
                    ...Object.fromEntries(
                      (analise?.rodadas_incluidas ?? []).map((r) => [String(r.id), `Ordem ${r.numero_ordem}`])
                    ),
                  }}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="todas">Todas as rodadas</SelectItem>
                    {analise?.rodadas_incluidas.map((r) => (
                      <SelectItem key={r.id} value={String(r.id)}>
                        Ordem {r.numero_ordem}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1.5">
                <Label>Operador</Label>
                <Select
                  value={operadorId}
                  onValueChange={(v) => setOperadorId(v ?? "todos")}
                  items={{
                    todos: "Todos os operadores",
                    ...Object.fromEntries((analise?.operadores_disponiveis ?? []).map((o) => [String(o.id), o.nome])),
                  }}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="todos">Todos os operadores</SelectItem>
                    {analise?.operadores_disponiveis.map((o) => (
                      <SelectItem key={o.id} value={String(o.id)}>
                        {o.nome}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1.5">
                <Label>De</Label>
                <Input type="date" value={dataInicio} onChange={(e) => setDataInicio(e.target.value)} />
              </div>
              <div className="space-y-1.5">
                <Label>Até</Label>
                <Input type="date" value={dataFim} onChange={(e) => setDataFim(e.target.value)} />
              </div>
            </div>

            {!!analise?.rodadas_incluidas.length && (
              <div className="mt-3 flex flex-wrap gap-2">
                {analise.rodadas_incluidas.map((r) => (
                  <Badge key={r.id} variant={r.status === "finalizada" ? "outline" : "secondary"} className="gap-1">
                    {r.status === "finalizada_com_pendencia" && <AlertTriangle className="size-3" />}
                    Ordem {r.numero_ordem} · {STATUS_RODADA_LABEL[r.status] ?? r.status}
                  </Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {isLoading && <div className="text-muted-foreground">Calculando...</div>}

      {analise && analise.caracteristicas.length === 0 && (
        <div className="text-muted-foreground">Esta etapa não possui características cadastradas.</div>
      )}

      {analise?.caracteristicas.map((c) => (
        <Card key={c.caracteristica_id}>
          <CardHeader className="flex flex-row flex-wrap items-center justify-between gap-2 space-y-0">
            <CardTitle className="text-base">{c.nome}</CardTitle>
            <StatusCpkBadge classificacao={c.classificacao} />
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm sm:grid-cols-4 lg:grid-cols-7">
              <Estatistica label="Nº amostras" valor={String(c.n_amostras)} />
              <Estatistica
                label="Média"
                valor={c.media !== null ? c.media.toFixed(c.casas_decimais) : "—"}
              />
              <Estatistica
                label="Desvio padrão"
                valor={c.desvio_padrao !== null ? c.desvio_padrao.toFixed(c.casas_decimais) : "—"}
              />
              <Estatistica label="LIE" valor={c.lie.toFixed(c.casas_decimais)} />
              <Estatistica label="LSE" valor={c.lse.toFixed(c.casas_decimais)} />
              <Estatistica label="Cp" valor={c.cp !== null ? c.cp.toFixed(2) : "—"} />
              <Estatistica label="Cpk" valor={c.cpk !== null ? c.cpk.toFixed(2) : "—"} />
            </div>

            {c.n_amostras > 0 && c.n_amostras < 2 && (
              <p className="text-sm text-muted-foreground">
                Apenas 1 amostra — desvio padrão e Cp/Cpk exigem no mínimo 2 amostras.
              </p>
            )}
            {c.baixa_robustez && c.n_amostras >= 2 && (
              <div className="flex items-center gap-2 rounded-md border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-900">
                <AlertTriangle className="size-4 shrink-0" />
                Baixo número de amostras — resultado pode não ser estatisticamente robusto (ideal ≥{" "}
                {analise.limiar_baixa_robustez}).
              </div>
            )}

            {c.n_amostras > 0 ? (
              <HistogramaChart
                valores={c.valores}
                lie={c.lie}
                lse={c.lse}
                nominal={c.nominal}
                casasDecimais={c.casas_decimais}
                unidade={c.unidade}
              />
            ) : (
              <div className="flex h-24 items-center justify-center text-sm text-muted-foreground">
                Sem medições para os filtros selecionados.
              </div>
            )}

            <CartaControleSecao
              carta={cartaControle?.caracteristicas.find((cc) => cc.caracteristica_id === c.caracteristica_id)}
            />
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

function Estatistica({ label, valor }: { label: string; valor: string }) {
  return (
    <div>
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="font-medium tabular-nums">{valor}</div>
    </div>
  )
}

function CartaControleSecao({ carta }: { carta: CartaControleCaracteristica | undefined }) {
  if (!carta || !carta.exibir) {
    return (
      <div className="space-y-1 border-t pt-4">
        <h4 className="text-sm font-medium">Carta de Controle X-barra e R</h4>
        <p className="text-sm text-muted-foreground">
          Exibida a partir de 2 rodadas finalizadas com pelo menos 2 amostras cada.
        </p>
      </div>
    )
  }

  const pontosX = carta.subgrupos.map((s) => ({
    label: `Ordem ${s.numero_ordem}`,
    valor: s.media,
    foraControle: s.fora_controle_x,
  }))
  const pontosR = carta.subgrupos.map((s) => ({
    label: `Ordem ${s.numero_ordem}`,
    valor: s.amplitude,
    foraControle: s.fora_controle_r,
  }))

  return (
    <div className="space-y-3 border-t pt-4">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium">Carta de Controle X-barra e R</h4>
        <span className="text-xs text-muted-foreground">
          {carta.subgrupos.length} subgrupo(s) · tamanho médio {carta.tamanho_amostra_medio?.toFixed(1)}
        </span>
      </div>
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <CartaControleChart
          titulo="X-barra (média por rodada)"
          pontos={pontosX}
          linhaCentral={carta.linha_central_x!}
          lsc={carta.lsc_x!}
          lic={carta.lic_x!}
          casasDecimais={carta.casas_decimais}
          unidade={carta.unidade}
        />
        <CartaControleChart
          titulo="R (amplitude por rodada)"
          pontos={pontosR}
          linhaCentral={carta.linha_central_r!}
          lsc={carta.lsc_r!}
          lic={carta.lic_r!}
          casasDecimais={carta.casas_decimais}
          unidade={carta.unidade}
        />
      </div>
    </div>
  )
}
