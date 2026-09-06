import { useEffect, useState } from "react"
import { ArrowRight, Download, History } from "lucide-react"
import { useNavigate, useParams } from "react-router-dom"
import { toast } from "sonner"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { useAuth } from "@/features/auth/AuthContext"
import { useEncerrarNC, useNaoConformidade, useTratarNC } from "@/features/nao_conformidade/api"
import { StatusNCBadge } from "@/features/nao_conformidade/StatusNCBadge"
import { baixarRelatorioRnc } from "@/features/relatorios/api"
import { useUsuarios } from "@/features/usuarios/api"
import { getApiError } from "@/lib/api-client"
import type { DisposicaoNC } from "@/types/api"

const DISPOSICAO_LABEL: Record<DisposicaoNC, string> = {
  retrabalho: "Retrabalho",
  sucata: "Sucata",
  uso_como_esta: "Uso como está (concessão)",
  devolucao_fornecedor: "Devolução ao fornecedor",
  reclassificacao: "Reclassificação",
}

const CLASSIFICACAO_LABEL: Record<string, string> = { critica: "Crítica", maior: "Maior", menor: "Menor" }
const ORIGEM_LABEL: Record<string, string> = {
  processo: "Processo",
  materia_prima: "Matéria-prima",
  projeto: "Projeto/Desenho",
  instrumento: "Instrumento de medição",
  mao_de_obra: "Mão de obra",
  outro: "Outro",
}

export function NaoConformidadeDetailPage() {
  const { ncId } = useParams<{ ncId: string }>()
  const id = Number(ncId)
  const navigate = useNavigate()
  const { usuario } = useAuth()
  const podeTratar = usuario?.perfil === "analista_qualidade" || usuario?.perfil === "gestor_qualidade"

  const { data: nc, isLoading } = useNaoConformidade(id)
  const { data: usuarios } = useUsuarios()
  const tratarNC = useTratarNC(id)
  const encerrarNC = useEncerrarNC(id)

  const [causaPreliminar, setCausaPreliminar] = useState("")
  const [disposicao, setDisposicao] = useState<string>("")
  const [responsavelId, setResponsavelId] = useState<string>("")
  const [necessitaPlano, setNecessitaPlano] = useState(false)
  const [exportando, setExportando] = useState(false)

  useEffect(() => {
    if (nc) {
      setCausaPreliminar(nc.causa_raiz_preliminar ?? "")
      setDisposicao(nc.disposicao ?? "")
      setResponsavelId(nc.responsavel_analise_id ? String(nc.responsavel_analise_id) : "")
      setNecessitaPlano(nc.necessita_plano_acao)
    }
  }, [nc])

  if (isLoading || !nc) {
    return <div className="text-muted-foreground">Carregando...</div>
  }

  const usuarioItems = Object.fromEntries((usuarios ?? []).map((u) => [String(u.id), u.nome]))
  const rncId = nc.id
  const numeroRnc = nc.numero_rnc

  function handleSalvarTratamento() {
    tratarNC.mutate(
      {
        causa_raiz_preliminar: causaPreliminar || null,
        disposicao: (disposicao as DisposicaoNC) || null,
        responsavel_analise_id: responsavelId ? Number(responsavelId) : null,
        necessita_plano_acao: necessitaPlano,
      },
      {
        onSuccess: () => toast.success("Tratamento salvo"),
        onError: (error) => toast.error(getApiError(error).detail),
      }
    )
  }

  function handleEncerrar() {
    encerrarNC.mutate(undefined, {
      onSuccess: () => toast.success("RNC encerrada"),
      onError: (error) => toast.error(getApiError(error).detail),
    })
  }

  async function handleExportar() {
    setExportando(true)
    try {
      await baixarRelatorioRnc(rncId, numeroRnc)
    } catch (error) {
      toast.error(getApiError(error).detail)
    } finally {
      setExportando(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-md border bg-background p-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-semibold">{nc.numero_rnc}</h1>
            <StatusNCBadge status={nc.status} />
            {nc.tem_plano_aberto && (
              <Badge variant="outline" className="border-amber-400 text-amber-700">
                Plano de Ação ainda em aberto
              </Badge>
            )}
          </div>
          <p className="text-muted-foreground">
            {nc.peca.codigo} — {nc.peca.descricao}
            {nc.etapa && ` · Etapa ${nc.etapa.numero_etapa}`}
            {nc.caracteristica && ` · ${nc.caracteristica.nome}`}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExportar} disabled={exportando}>
            <Download className="size-4" />
            {exportando ? "Gerando..." : "Exportar PDF"}
          </Button>
          {podeTratar && nc.status === "em_tratamento" && (
            <Button onClick={handleEncerrar} disabled={encerrarNC.isPending}>
              {encerrarNC.isPending ? "Encerrando..." : "Encerrar RNC"}
            </Button>
          )}
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Problema</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>{nc.descricao_problema}</p>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <div>
              <div className="text-xs text-muted-foreground">Quantidade afetada</div>
              <div className="font-medium">{nc.quantidade_afetada}</div>
            </div>
            <div>
              <div className="text-xs text-muted-foreground">Classificação</div>
              <div className="font-medium">{CLASSIFICACAO_LABEL[nc.classificacao]}</div>
            </div>
            <div>
              <div className="text-xs text-muted-foreground">Origem</div>
              <div className="font-medium">{ORIGEM_LABEL[nc.origem]}</div>
            </div>
            <div>
              <div className="text-xs text-muted-foreground">Aberta por</div>
              <div className="font-medium">
                {nc.aberto_por_nome} em {new Date(nc.data_abertura).toLocaleDateString("pt-BR")}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Análise e tratamento</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {!podeTratar ? (
            <p className="text-sm text-muted-foreground">
              {nc.disposicao
                ? `Disposição definida: ${DISPOSICAO_LABEL[nc.disposicao]}`
                : "Aguardando análise da Qualidade."}
            </p>
          ) : (
            <>
              <div className="space-y-1.5">
                <Label>Causa raiz (preliminar)</Label>
                <Textarea
                  rows={2}
                  value={causaPreliminar}
                  onChange={(e) => setCausaPreliminar(e.target.value)}
                  disabled={nc.status === "encerrada"}
                />
              </div>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <div className="space-y-1.5">
                  <Label>Disposição da peça</Label>
                  <Select
                    value={disposicao}
                    onValueChange={(v) => setDisposicao(v ?? "")}
                    items={DISPOSICAO_LABEL}
                  >
                    <SelectTrigger className="w-full" disabled={nc.status === "encerrada"}>
                      <SelectValue placeholder="Selecione" />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(DISPOSICAO_LABEL).map(([value, label]) => (
                        <SelectItem key={value} value={value}>
                          {label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1.5">
                  <Label>Responsável pela análise</Label>
                  <Select
                    value={responsavelId}
                    onValueChange={(v) => setResponsavelId(v ?? "")}
                    items={usuarioItems}
                  >
                    <SelectTrigger className="w-full" disabled={nc.status === "encerrada"}>
                      <SelectValue placeholder="Selecione" />
                    </SelectTrigger>
                    <SelectContent>
                      {(usuarios ?? []).map((u) => (
                        <SelectItem key={u.id} value={String(u.id)}>
                          {u.nome}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <label className="flex items-center gap-2 text-sm">
                <Checkbox
                  checked={necessitaPlano}
                  onCheckedChange={setNecessitaPlano}
                  disabled={nc.status === "encerrada"}
                />
                Necessário Plano de Ação
              </label>
              {nc.status !== "encerrada" && (
                <Button onClick={handleSalvarTratamento} disabled={tratarNC.isPending}>
                  {tratarNC.isPending ? "Salvando..." : "Salvar tratamento"}
                </Button>
              )}
            </>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Plano de Ação</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {nc.planos_acao.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              {nc.necessita_plano_acao
                ? "Marcado como necessário — será criado ao salvar o tratamento."
                : "Nenhum Plano de Ação vinculado."}
            </p>
          ) : (
            [...nc.planos_acao].reverse().map((plano) => (
              <div key={plano.id} className="flex items-center justify-between gap-3 rounded-md border p-3">
                <div className="text-sm">
                  Plano #{plano.id}
                  {plano.ciclo > 1 && ` · ciclo ${plano.ciclo}`}
                  {plano.id === nc.plano_acao_ativo_id && (
                    <Badge variant="secondary" className="ml-2">
                      Ativo
                    </Badge>
                  )}
                </div>
                <Button variant="outline" size="sm" onClick={() => navigate(`/planos-acao/${plano.id}`)}>
                  Ver plano ({plano.status})
                  <ArrowRight className="size-4" />
                </Button>
              </div>
            ))
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <History className="size-4" />
            Histórico
          </CardTitle>
        </CardHeader>
        <CardContent>
          {nc.historico.length === 0 ? (
            <p className="text-sm text-muted-foreground">Sem eventos registrados.</p>
          ) : (
            <ul className="space-y-2 text-sm">
              {nc.historico.map((evento, i) => (
                <li key={i} className="flex items-start justify-between gap-3 border-b pb-2 last:border-0">
                  <div>
                    <span className="font-medium">{evento.usuario_nome}</span> — {evento.detalhe ?? evento.acao}
                  </div>
                  <span className="shrink-0 text-xs text-muted-foreground">
                    {new Date(evento.criado_em).toLocaleString("pt-BR")}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
