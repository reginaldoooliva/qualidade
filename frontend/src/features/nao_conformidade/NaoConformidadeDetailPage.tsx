import { useEffect, useState } from "react"
import { AlertTriangle, ArrowRight, Download, History, Plus, Trash2 } from "lucide-react"
import { useNavigate, useParams } from "react-router-dom"
import { toast } from "sonner"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { ConcluirAcaoDialog } from "@/features/acoes_departamentais/ConcluirAcaoDialog"
import { FotoAutenticada } from "@/components/FotoAutenticada"
import { Input } from "@/components/ui/input"
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
import { useDepartamentos } from "@/features/departamentos/api"
import {
  useAdicionarAcaoDepartamental,
  useConcluirAcaoDepartamental,
  useEncerrarNC,
  useNaoConformidade,
  useRemoverAcaoDepartamental,
  useTratarNC,
} from "@/features/nao_conformidade/api"
import { StatusNCBadge } from "@/features/nao_conformidade/StatusNCBadge"
import { baixarRelatorioRnc } from "@/features/relatorios/api"
import { useUsuarios } from "@/features/usuarios/api"
import { getApiError } from "@/lib/api-client"
import type { AcaoDepartamental, DisposicaoNC } from "@/types/api"

const DISPOSICAO_LABEL: Record<DisposicaoNC, string> = {
  retrabalho: "Retrabalho",
  sucata: "Sucata",
  uso_como_esta: "Uso como está (concessão)",
  devolucao_fornecedor: "Devolução ao fornecedor",
  reclassificacao: "Reclassificação",
}

const TIPO_LABEL: Record<string, string> = {
  processo: "Processo interno",
  fornecedor: "Recebimento de fornecedor",
  cliente: "Devolução de cliente",
}
const DETECCAO_LABEL: Record<string, string> = { interno: "Interno", cliente: "Cliente", fornecedor: "Fornecedor" }
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
  const { data: departamentos } = useDepartamentos()
  const tratarNC = useTratarNC(id)
  const encerrarNC = useEncerrarNC(id)
  const adicionarAcaoDepartamental = useAdicionarAcaoDepartamental(id)
  const removerAcaoDepartamental = useRemoverAcaoDepartamental(id)
  const concluirAcaoDepartamental = useConcluirAcaoDepartamental(id)

  const [causaPreliminar, setCausaPreliminar] = useState("")
  const [disposicao, setDisposicao] = useState<string>("")
  const [responsavelId, setResponsavelId] = useState<string>("")
  const [necessitaPlano, setNecessitaPlano] = useState(false)
  const [exportando, setExportando] = useState(false)
  const [avisoPendencia, setAvisoPendencia] = useState(false)
  const [novoDepartamentoId, setNovoDepartamentoId] = useState("")
  const [novaDescricaoTratativa, setNovaDescricaoTratativa] = useState("")
  const [acaoParaConcluir, setAcaoParaConcluir] = useState<AcaoDepartamental | null>(null)

  useEffect(() => {
    if (nc) {
      setCausaPreliminar(nc.causa_raiz_preliminar ?? "")
      setDisposicao(nc.disposicao ?? "")
      setResponsavelId(
        nc.responsavel_analise_id ? String(nc.responsavel_analise_id) : usuario ? String(usuario.id) : ""
      )
      setNecessitaPlano(nc.necessita_plano_acao)
    }
  }, [nc, usuario])

  useEffect(() => {
    if (nc && !nc.tem_acao_departamental_pendente) {
      setAvisoPendencia(false)
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

  function handleEncerrar(ignorarPendencias = false) {
    encerrarNC.mutate(
      { ignorarPendencias },
      {
        onSuccess: () => {
          toast.success("RNC encerrada")
          setAvisoPendencia(false)
        },
        onError: (error) => {
          const apiError = getApiError(error)
          if (apiError.code === "ACOES_DEPARTAMENTAIS_PENDENTES") {
            setAvisoPendencia(true)
          } else {
            toast.error(apiError.detail)
          }
        },
      }
    )
  }

  function handleAdicionarAcaoDepartamental() {
    if (!novoDepartamentoId || !novaDescricaoTratativa.trim()) return
    adicionarAcaoDepartamental.mutate(
      { departamento_id: Number(novoDepartamentoId), descricao: novaDescricaoTratativa },
      {
        onSuccess: () => {
          toast.success("Tratativa departamental adicionada")
          setNovoDepartamentoId("")
          setNovaDescricaoTratativa("")
        },
        onError: (error) => toast.error(getApiError(error).detail),
      }
    )
  }

  function handleRemoverAcaoDepartamental(acaoId: number) {
    removerAcaoDepartamental.mutate(acaoId, {
      onSuccess: () => toast.success("Tratativa removida"),
      onError: (error) => toast.error(getApiError(error).detail),
    })
  }

  function handleConcluirAcaoDepartamental(observacao: string) {
    if (!acaoParaConcluir) return
    concluirAcaoDepartamental.mutate(
      { acaoId: acaoParaConcluir.id, observacao },
      {
        onSuccess: () => {
          toast.success("Tratativa concluída")
          setAcaoParaConcluir(null)
        },
        onError: (error) => toast.error(getApiError(error).detail),
      }
    )
  }

  function podeConcluirAcao(acao: AcaoDepartamental): boolean {
    if (podeTratar) return true
    return !!usuario?.departamento_id && usuario.departamento_id === acao.departamento_id
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
            <Badge variant="outline">{TIPO_LABEL[nc.tipo]}</Badge>
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
            {nc.fornecedor && ` · Fornecedor: ${nc.fornecedor.nome}`}
            {nc.cliente && ` · Cliente: ${nc.cliente}`}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExportar} disabled={exportando}>
            <Download className="size-4" />
            {exportando ? "Gerando..." : "Exportar PDF"}
          </Button>
          {podeTratar && nc.status === "em_tratamento" && (
            <Button onClick={() => handleEncerrar(false)} disabled={encerrarNC.isPending}>
              {encerrarNC.isPending ? "Encerrando..." : "Encerrar RNC"}
            </Button>
          )}
        </div>
      </div>

      {avisoPendencia && (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-amber-400 bg-amber-50 p-3 text-sm text-amber-900">
          <div className="flex items-center gap-2">
            <AlertTriangle className="size-4 shrink-0" />
            Ainda há tratativa(s) departamental(is) pendente(s). Conclua-as ou encerre mesmo assim.
          </div>
          <Button size="sm" variant="outline" onClick={() => handleEncerrar(true)} disabled={encerrarNC.isPending}>
            Encerrar mesmo assim
          </Button>
        </div>
      )}

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

      {(nc.maquina || nc.operadores.length > 0 || nc.modo_falha || nc.deteccao || nc.numero_nf_entrada || nc.numero_nf) && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Contexto</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
            {nc.deteccao && (
              <div>
                <div className="text-xs text-muted-foreground">Detecção</div>
                <div className="font-medium">{DETECCAO_LABEL[nc.deteccao]}</div>
              </div>
            )}
            {nc.maquina && (
              <div>
                <div className="text-xs text-muted-foreground">Máquina</div>
                <div className="font-medium">{nc.maquina.codigo} — {nc.maquina.descricao}</div>
              </div>
            )}
            {nc.operadores.length > 0 && (
              <div>
                <div className="text-xs text-muted-foreground">Operador(es)</div>
                <div className="font-medium">{nc.operadores.map((o) => o.nome).join(", ")}</div>
              </div>
            )}
            {nc.setup && (
              <div>
                <div className="text-xs text-muted-foreground">Setup</div>
                <div className="font-medium">Ocorreu durante troca de setup</div>
              </div>
            )}
            {nc.modo_falha && (
              <div>
                <div className="text-xs text-muted-foreground">Modo de falha</div>
                <div className="font-medium">{nc.modo_falha}</div>
              </div>
            )}
            {nc.numero_nf_entrada && (
              <div>
                <div className="text-xs text-muted-foreground">Nº NF de entrada</div>
                <div className="font-medium">{nc.numero_nf_entrada}</div>
              </div>
            )}
            {nc.vendedor && (
              <div>
                <div className="text-xs text-muted-foreground">Vendedor</div>
                <div className="font-medium">{nc.vendedor}</div>
              </div>
            )}
            {nc.numero_nf && (
              <div>
                <div className="text-xs text-muted-foreground">Nº NF</div>
                <div className="font-medium">{nc.numero_nf}</div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {nc.fotos.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Fotos</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-3">
            {nc.fotos.map((foto) => (
              <FotoAutenticada
                key={foto.id}
                url={`/nao-conformidades/${nc.id}/fotos/${foto.id}`}
                alt={foto.nome_arquivo}
                className="size-28 rounded-md border object-cover"
              />
            ))}
          </CardContent>
        </Card>
      )}

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
          <CardTitle className="text-base">Tratativas por Departamento</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {nc.acoes_departamentais.length === 0 ? (
            <p className="text-sm text-muted-foreground">Nenhuma tratativa departamental atribuída.</p>
          ) : (
            <div className="space-y-2">
              {nc.acoes_departamentais.map((acao) => (
                <div key={acao.id} className="rounded-md border p-3 text-sm">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{acao.departamento.nome}</span>
                        <Badge variant={acao.status === "concluida" ? "default" : "outline"}>
                          {acao.status === "concluida" ? "Concluída" : "Pendente"}
                        </Badge>
                      </div>
                      <p className="mt-1">{acao.descricao}</p>
                      {acao.status === "concluida" && (
                        <p className="mt-1 text-xs text-muted-foreground">
                          Concluída por {acao.concluido_por_nome} em{" "}
                          {acao.concluido_em && new Date(acao.concluido_em).toLocaleString("pt-BR")} —{" "}
                          {acao.observacao_conclusao}
                        </p>
                      )}
                    </div>
                    <div className="flex shrink-0 gap-2">
                      {acao.status === "pendente" && podeConcluirAcao(acao) && (
                        <Button size="sm" onClick={() => setAcaoParaConcluir(acao)}>
                          Concluir
                        </Button>
                      )}
                      {acao.status === "pendente" && podeTratar && (
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleRemoverAcaoDepartamental(acao.id)}
                          disabled={removerAcaoDepartamental.isPending}
                        >
                          <Trash2 className="size-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {podeTratar && nc.status !== "encerrada" && (
            <div className="flex flex-wrap items-end gap-2 border-t pt-3">
              <div className="min-w-40 flex-1 space-y-1.5">
                <Label>Departamento</Label>
                <Select
                  value={novoDepartamentoId}
                  onValueChange={(v) => setNovoDepartamentoId(v ?? "")}
                  items={Object.fromEntries((departamentos ?? []).map((d) => [String(d.id), d.nome]))}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Selecione" />
                  </SelectTrigger>
                  <SelectContent>
                    {(departamentos ?? [])
                      .filter((d) => d.status === "ativo")
                      .map((d) => (
                        <SelectItem key={d.id} value={String(d.id)}>
                          {d.nome}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="min-w-56 flex-[2] space-y-1.5">
                <Label>Descrição da tratativa</Label>
                <Input
                  placeholder="Ex.: Dar baixa da peça sucateada na ordem"
                  value={novaDescricaoTratativa}
                  onChange={(e) => setNovaDescricaoTratativa(e.target.value)}
                />
              </div>
              <Button
                onClick={handleAdicionarAcaoDepartamental}
                disabled={adicionarAcaoDepartamental.isPending || !novoDepartamentoId || !novaDescricaoTratativa.trim()}
              >
                <Plus className="size-4" />
                Adicionar
              </Button>
            </div>
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

      <ConcluirAcaoDialog
        open={!!acaoParaConcluir}
        onOpenChange={(open) => !open && setAcaoParaConcluir(null)}
        onConfirmar={handleConcluirAcaoDepartamental}
        pendente={concluirAcaoDepartamental.isPending}
      />
    </div>
  )
}
