import { useState } from "react"
import { Download } from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useAuth } from "@/features/auth/AuthContext"
import { useEtapasByPeca } from "@/features/etapas/api"
import { PecaBuscaInput } from "@/features/pecas/PecaBuscaInput"
import {
  baixarRelatorioConsolidadoNc,
  baixarRelatorioConsolidadoPecas,
  baixarRelatorioCpkPeca,
  baixarRelatorioDadosBrutos,
  useConsolidadoNaoConformidades,
  useConsolidadoPecas,
} from "@/features/relatorios/api"
import { StatusCpkBadge } from "@/features/analise/StatusCpkBadge"
import { getApiError } from "@/lib/api-client"
import type { PecaListItem } from "@/types/api"

function useBaixando() {
  const [baixando, setBaixando] = useState<string | null>(null)
  async function executar(chave: string, acao: () => Promise<void>) {
    setBaixando(chave)
    try {
      await acao()
    } catch (error) {
      toast.error(getApiError(error).detail)
    } finally {
      setBaixando(null)
    }
  }
  return { baixando, executar }
}

function RelatorioCpkCard() {
  const [peca, setPeca] = useState<PecaListItem | null>(null)
  const [dataInicio, setDataInicio] = useState("")
  const [dataFim, setDataFim] = useState("")
  const { baixando, executar } = useBaixando()

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Cp/Cpk por peça (PDF)</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <PecaBuscaInput value={peca} onChange={setPeca} />
        {peca && (
          <>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label>De</Label>
                <Input type="date" value={dataInicio} onChange={(e) => setDataInicio(e.target.value)} />
              </div>
              <div className="space-y-1.5">
                <Label>Até</Label>
                <Input type="date" value={dataFim} onChange={(e) => setDataFim(e.target.value)} />
              </div>
            </div>
            <Button
              disabled={baixando === "cpk"}
              onClick={() =>
                executar("cpk", () =>
                  baixarRelatorioCpkPeca(peca.id, peca.codigo, {
                    dataInicio: dataInicio || undefined,
                    dataFim: dataFim || undefined,
                  })
                )
              }
            >
              <Download className="size-4" />
              {baixando === "cpk" ? "Gerando..." : "Baixar PDF"}
            </Button>
          </>
        )}
      </CardContent>
    </Card>
  )
}

function RelatorioDadosBrutosCard() {
  const [peca, setPeca] = useState<PecaListItem | null>(null)
  const [etapaId, setEtapaId] = useState<string>("")
  const [dataInicio, setDataInicio] = useState("")
  const [dataFim, setDataFim] = useState("")
  const { data: etapas } = useEtapasByPeca(peca?.id)
  const etapaItems = Object.fromEntries(
    (etapas ?? []).map((e) => [String(e.id), `Etapa ${e.numero_etapa}${e.descricao ? ` — ${e.descricao}` : ""}`])
  )
  const { baixando, executar } = useBaixando()

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Dados brutos de coleta (Excel)</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <PecaBuscaInput value={peca} onChange={setPeca} />
        {peca && (
          <>
            <div className="space-y-1.5">
              <Label>Etapa (opcional — todas se não selecionar)</Label>
              <Select value={etapaId} onValueChange={(v) => setEtapaId(v ?? "")} items={etapaItems}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Todas as etapas" />
                </SelectTrigger>
                <SelectContent>
                  {(etapas ?? []).map((e) => (
                    <SelectItem key={e.id} value={String(e.id)}>
                      {etapaItems[String(e.id)]}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label>De</Label>
                <Input type="date" value={dataInicio} onChange={(e) => setDataInicio(e.target.value)} />
              </div>
              <div className="space-y-1.5">
                <Label>Até</Label>
                <Input type="date" value={dataFim} onChange={(e) => setDataFim(e.target.value)} />
              </div>
            </div>
            <Button
              disabled={baixando === "dados"}
              onClick={() =>
                executar("dados", () =>
                  baixarRelatorioDadosBrutos(peca.id, peca.codigo, etapaId ? Number(etapaId) : undefined, {
                    dataInicio: dataInicio || undefined,
                    dataFim: dataFim || undefined,
                  })
                )
              }
            >
              <Download className="size-4" />
              {baixando === "dados" ? "Gerando..." : "Baixar Excel"}
            </Button>
          </>
        )}
      </CardContent>
    </Card>
  )
}

function ConsolidadoPecasCard() {
  const { data: itens, isLoading } = useConsolidadoPecas()
  const { baixando, executar } = useBaixando()

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <CardTitle className="text-base">Consolidado de peças (visão gerencial)</CardTitle>
        <Button
          variant="outline"
          size="sm"
          disabled={baixando === "consolidado-pecas"}
          onClick={() => executar("consolidado-pecas", baixarRelatorioConsolidadoPecas)}
        >
          <Download className="size-4" />
          PDF
        </Button>
      </CardHeader>
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Peça</TableHead>
              <TableHead>Característica crítica</TableHead>
              <TableHead>Cpk</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Nº amostras</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-muted-foreground">
                  Carregando...
                </TableCell>
              </TableRow>
            )}
            {itens?.map((item) => (
              <TableRow key={item.peca_id}>
                <TableCell>
                  {item.codigo} — {item.descricao}
                </TableCell>
                <TableCell>{item.caracteristica_critica ?? "—"}</TableCell>
                <TableCell className="tabular-nums">{item.cpk_critico?.toFixed(2) ?? "—"}</TableCell>
                <TableCell>
                  <StatusCpkBadge classificacao={item.classificacao} />
                </TableCell>
                <TableCell className="tabular-nums">{item.n_amostras}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

function ConsolidadoNcCard() {
  const [dataInicio, setDataInicio] = useState("")
  const [dataFim, setDataFim] = useState("")
  const filtros = { dataInicio: dataInicio || undefined, dataFim: dataFim || undefined }
  const { data, isLoading } = useConsolidadoNaoConformidades(filtros)
  const { baixando, executar } = useBaixando()

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <CardTitle className="text-base">Não Conformidades — Consolidado</CardTitle>
        <Button
          variant="outline"
          size="sm"
          disabled={baixando === "consolidado-nc"}
          onClick={() => executar("consolidado-nc", () => baixarRelatorioConsolidadoNc(filtros))}
        >
          <Download className="size-4" />
          PDF
        </Button>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-3 sm:w-80">
          <div className="space-y-1.5">
            <Label>De</Label>
            <Input type="date" value={dataInicio} onChange={(e) => setDataInicio(e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <Label>Até</Label>
            <Input type="date" value={dataFim} onChange={(e) => setDataFim(e.target.value)} />
          </div>
        </div>

        {isLoading && <p className="text-sm text-muted-foreground">Carregando...</p>}

        {data && (
          <>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <Indicador label="Total de RNCs" valor={data.total_rnc} />
              <Indicador label="Encerradas" valor={data.total_encerradas} />
              <Indicador
                label="Tempo médio tratamento"
                valor={data.tempo_medio_tratamento_dias !== null ? `${data.tempo_medio_tratamento_dias.toFixed(1)}d` : "—"}
              />
              <Indicador label="Taxa de reincidência" valor={`${(data.taxa_reincidencia * 100).toFixed(0)}%`} />
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <Distribuicao titulo="Por peça" dados={data.por_peca} />
              <Distribuicao titulo="Por classificação" dados={data.por_classificacao} />
              <Distribuicao titulo="Por origem" dados={data.por_origem} />
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}

function Indicador({ label, valor }: { label: string; valor: string | number }) {
  return (
    <div className="rounded-md border p-3">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="text-xl font-semibold tabular-nums">{valor}</div>
    </div>
  )
}

function Distribuicao({ titulo, dados }: { titulo: string; dados: Record<string, number> }) {
  const entradas = Object.entries(dados)
  return (
    <div className="space-y-1.5">
      <div className="text-sm font-medium">{titulo}</div>
      {entradas.length === 0 ? (
        <p className="text-sm text-muted-foreground">Sem dados.</p>
      ) : (
        <ul className="space-y-1 text-sm">
          {entradas.map(([chave, valor]) => (
            <li key={chave} className="flex items-center justify-between border-b pb-1">
              <span className="truncate">{chave}</span>
              <span className="tabular-nums font-medium">{valor}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export function RelatoriosPage() {
  const { usuario } = useAuth()
  const ehGestor = usuario?.perfil === "gestor_qualidade"

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold tracking-tight">Relatórios</h1>

      <RelatorioCpkCard />
      <RelatorioDadosBrutosCard />

      {ehGestor && (
        <>
          <ConsolidadoPecasCard />
          <ConsolidadoNcCard />
        </>
      )}
    </div>
  )
}
