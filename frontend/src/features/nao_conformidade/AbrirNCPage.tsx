import { useEffect, useState } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
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
import { FotoUploadInput } from "@/components/FotoUploadInput"
import { useCaracteristicasByEtapa } from "@/features/caracteristicas/api"
import { useEtapasByPeca } from "@/features/etapas/api"
import { useFornecedores } from "@/features/fornecedores/api"
import { useMaquinas } from "@/features/maquinas/api"
import { useAbrirNC, useUploadFotosNC } from "@/features/nao_conformidade/api"
import { usePeca } from "@/features/pecas/api"
import { PecaBuscaInput } from "@/features/pecas/PecaBuscaInput"
import { useUsuarios } from "@/features/usuarios/api"
import { getApiError } from "@/lib/api-client"
import type { ClassificacaoNC, DeteccaoNC, OrigemNC, PecaListItem, TipoNC } from "@/types/api"

const TIPO_LABEL: Record<TipoNC, string> = {
  processo: "Processo interno",
  fornecedor: "Recebimento de fornecedor",
  cliente: "Devolução de cliente",
}

const CLASSIFICACAO_LABEL: Record<ClassificacaoNC, string> = {
  critica: "Crítica",
  maior: "Maior",
  menor: "Menor",
}

const ORIGEM_LABEL: Record<OrigemNC, string> = {
  processo: "Processo",
  materia_prima: "Matéria-prima",
  projeto: "Projeto/Desenho",
  instrumento: "Instrumento de medição",
  mao_de_obra: "Mão de obra",
  outro: "Outro",
}

const DETECCAO_LABEL: Record<DeteccaoNC, string> = {
  interno: "Interno",
  cliente: "Cliente",
  fornecedor: "Fornecedor",
}

export function AbrirNCPage() {
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const pecaIdPrefill = params.get("pecaId") ? Number(params.get("pecaId")) : undefined
  const etapaIdPrefill = params.get("etapaId") ? Number(params.get("etapaId")) : undefined
  const ordemIdPrefill = params.get("ordemId") ? Number(params.get("ordemId")) : undefined
  const rodadaIdPrefill = params.get("rodadaId") ? Number(params.get("rodadaId")) : undefined
  const caracteristicaIdPrefill = params.get("caracteristicaId")
    ? Number(params.get("caracteristicaId"))
    : undefined
  const descricaoPrefill = params.get("descricao") ?? ""

  const { data: pecaPrefetch } = usePeca(pecaIdPrefill)
  const [peca, setPeca] = useState<PecaListItem | null>(null)

  useEffect(() => {
    if (pecaPrefetch && !peca) {
      setPeca({ ...pecaPrefetch, numero_caracteristicas: 0 })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pecaPrefetch])

  const [tipo, setTipo] = useState<TipoNC>("processo")

  const { data: etapas } = useEtapasByPeca(peca?.id)
  const [etapaId, setEtapaId] = useState<string>("")
  useEffect(() => {
    if (etapaIdPrefill && etapas?.some((e) => e.id === etapaIdPrefill)) {
      setEtapaId(String(etapaIdPrefill))
    }
  }, [etapas, etapaIdPrefill])
  const etapaItems = Object.fromEntries(
    (etapas ?? []).map((e) => [String(e.id), `Etapa ${e.numero_etapa}${e.descricao ? ` — ${e.descricao}` : ""}`])
  )

  const { data: caracteristicas } = useCaracteristicasByEtapa(etapaId ? Number(etapaId) : undefined)
  const [caracteristicaId, setCaracteristicaId] = useState<string>("")
  useEffect(() => {
    if (caracteristicaIdPrefill && caracteristicas?.some((c) => c.id === caracteristicaIdPrefill)) {
      setCaracteristicaId(String(caracteristicaIdPrefill))
    }
  }, [caracteristicas, caracteristicaIdPrefill])
  const caracteristicaItems = Object.fromEntries((caracteristicas ?? []).map((c) => [String(c.id), c.nome]))

  const [descricao, setDescricao] = useState(descricaoPrefill)
  const [quantidade, setQuantidade] = useState("1")
  const [classificacao, setClassificacao] = useState<ClassificacaoNC | "">("")
  const [origem, setOrigem] = useState<OrigemNC | "">("")
  const [modoFalha, setModoFalha] = useState("")
  const [fotos, setFotos] = useState<File[]>([])

  // Tipo = processo
  const { data: maquinas } = useMaquinas()
  const maquinasAtivas = (maquinas ?? []).filter((m) => m.status === "ativo")
  const { data: usuarios } = useUsuarios()
  const [maquinaId, setMaquinaId] = useState<string>("")
  const [operadoresIds, setOperadoresIds] = useState<number[]>([])
  const [setup, setSetup] = useState(false)
  const [deteccao, setDeteccao] = useState<DeteccaoNC | "">("")

  // Tipo = fornecedor
  const { data: fornecedores } = useFornecedores()
  const fornecedoresAtivos = (fornecedores ?? []).filter((f) => f.status === "ativo")
  const [fornecedorId, setFornecedorId] = useState<string>("")
  const [numeroNfEntrada, setNumeroNfEntrada] = useState("")

  // Tipo = cliente
  const [cliente, setCliente] = useState("")
  const [vendedor, setVendedor] = useState("")
  const [numeroNf, setNumeroNf] = useState("")
  const [dataEmissaoNf, setDataEmissaoNf] = useState("")

  const abrirNC = useAbrirNC()
  const uploadFotos = useUploadFotosNC()

  const pronto =
    !!peca &&
    descricao.trim() !== "" &&
    Number(quantidade) > 0 &&
    !!classificacao &&
    !!origem &&
    (tipo !== "fornecedor" || !!fornecedorId) &&
    (tipo !== "cliente" || cliente.trim() !== "")

  function toggleOperador(usuarioId: number, marcado: boolean) {
    setOperadoresIds((atual) =>
      marcado ? [...atual, usuarioId] : atual.filter((id) => id !== usuarioId)
    )
  }

  function handleSubmit() {
    if (!peca || !classificacao || !origem) return
    abrirNC.mutate(
      {
        tipo,
        peca_id: peca.id,
        etapa_id: etapaId ? Number(etapaId) : undefined,
        caracteristica_id: caracteristicaId ? Number(caracteristicaId) : undefined,
        ordem_id: ordemIdPrefill,
        rodada_id: rodadaIdPrefill,
        descricao_problema: descricao,
        quantidade_afetada: Number(quantidade),
        classificacao,
        origem,
        modo_falha: modoFalha || undefined,
        deteccao: tipo === "processo" && deteccao ? deteccao : undefined,
        maquina_id: tipo === "processo" && maquinaId ? Number(maquinaId) : undefined,
        operadores_ids: tipo === "processo" ? operadoresIds : undefined,
        setup: tipo === "processo" ? setup : undefined,
        fornecedor_id: tipo === "fornecedor" ? Number(fornecedorId) : undefined,
        numero_nf_entrada: tipo === "fornecedor" ? numeroNfEntrada || undefined : undefined,
        cliente: tipo === "cliente" ? cliente : undefined,
        vendedor: tipo === "cliente" ? vendedor || undefined : undefined,
        numero_nf: tipo === "cliente" ? numeroNf || undefined : undefined,
        data_emissao_nf: tipo === "cliente" ? dataEmissaoNf || undefined : undefined,
      },
      {
        onSuccess: async (nc) => {
          if (fotos.length > 0) {
            try {
              await uploadFotos.mutateAsync({ ncId: nc.id, arquivos: fotos })
            } catch {
              toast.error("RNC aberta, mas houve falha ao enviar as fotos. Tente anexar novamente na tela da RNC.")
            }
          }
          toast.success(`RNC ${nc.numero_rnc} aberta`)
          navigate(`/nao-conformidades/${nc.id}`)
        },
        onError: (error) => toast.error(getApiError(error).detail),
      }
    )
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <h1 className="text-2xl font-semibold tracking-tight">Abrir RNC</h1>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">1. Tipo de RNC</CardTitle>
        </CardHeader>
        <CardContent>
          <Select value={tipo} onValueChange={(v) => setTipo((v as TipoNC) ?? "processo")} items={TIPO_LABEL}>
            <SelectTrigger className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(TIPO_LABEL).map(([value, label]) => (
                <SelectItem key={value} value={value}>
                  {label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">2. Peça</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <PecaBuscaInput value={peca} onChange={setPeca} />
        </CardContent>
      </Card>

      {peca && tipo === "processo" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">3. Etapa e característica (opcional)</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div className="space-y-1.5">
              <Label>Etapa</Label>
              <Select value={etapaId} onValueChange={(v) => setEtapaId(v ?? "")} items={etapaItems}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Nenhuma" />
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
            <div className="space-y-1.5">
              <Label>Característica envolvida</Label>
              <Select
                value={caracteristicaId}
                onValueChange={(v) => setCaracteristicaId(v ?? "")}
                items={caracteristicaItems}
              >
                <SelectTrigger className="w-full" disabled={!etapaId}>
                  <SelectValue placeholder="Nenhuma" />
                </SelectTrigger>
                <SelectContent>
                  {(caracteristicas ?? []).map((c) => (
                    <SelectItem key={c.id} value={String(c.id)}>
                      {c.nome}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>
      )}

      {peca && tipo === "processo" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">4. Máquina e operador(es) (opcional)</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div className="space-y-1.5">
                <Label>Máquina</Label>
                <Select
                  value={maquinaId}
                  onValueChange={(v) => setMaquinaId(v ?? "")}
                  items={Object.fromEntries(maquinasAtivas.map((m) => [String(m.id), m.descricao]))}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Nenhuma" />
                  </SelectTrigger>
                  <SelectContent>
                    {maquinasAtivas.map((m) => (
                      <SelectItem key={m.id} value={String(m.id)}>
                        {m.codigo} — {m.descricao}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1.5">
                <Label>Detecção</Label>
                <Select
                  value={deteccao}
                  onValueChange={(v) => setDeteccao((v as DeteccaoNC) ?? "")}
                  items={DETECCAO_LABEL}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Onde foi encontrado" />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(DETECCAO_LABEL).map(([value, label]) => (
                      <SelectItem key={value} value={value}>
                        {label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-1.5">
              <Label>Operador(es) envolvido(s)</Label>
              <div className="flex flex-wrap gap-x-4 gap-y-2 rounded-md border p-3">
                {(usuarios ?? []).map((u) => (
                  <label key={u.id} className="flex items-center gap-2 text-sm">
                    <Checkbox
                      checked={operadoresIds.includes(u.id)}
                      onCheckedChange={(marcado) => toggleOperador(u.id, marcado === true)}
                    />
                    {u.nome}
                  </label>
                ))}
              </div>
            </div>
            <label className="flex items-center gap-2 text-sm">
              <Checkbox checked={setup} onCheckedChange={(v) => setSetup(v === true)} />
              Ocorreu durante troca de setup
            </label>
          </CardContent>
        </Card>
      )}

      {peca && tipo === "fornecedor" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">3. Fornecedor</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div className="space-y-1.5">
              <Label>Fornecedor</Label>
              <Select
                value={fornecedorId}
                onValueChange={(v) => setFornecedorId(v ?? "")}
                items={Object.fromEntries(fornecedoresAtivos.map((f) => [String(f.id), f.nome]))}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Selecione" />
                </SelectTrigger>
                <SelectContent>
                  {fornecedoresAtivos.map((f) => (
                    <SelectItem key={f.id} value={String(f.id)}>
                      {f.codigo} — {f.nome}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label>Nº da NF de entrada</Label>
              <Input value={numeroNfEntrada} onChange={(e) => setNumeroNfEntrada(e.target.value)} />
            </div>
          </CardContent>
        </Card>
      )}

      {peca && tipo === "cliente" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">3. Cliente</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div className="space-y-1.5">
              <Label>Cliente</Label>
              <Input value={cliente} onChange={(e) => setCliente(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label>Vendedor</Label>
              <Input value={vendedor} onChange={(e) => setVendedor(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label>Nº da NF</Label>
              <Input value={numeroNf} onChange={(e) => setNumeroNf(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label>Data de emissão</Label>
              <Input type="date" value={dataEmissaoNf} onChange={(e) => setDataEmissaoNf(e.target.value)} />
            </div>
          </CardContent>
        </Card>
      )}

      {peca && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">{tipo === "processo" ? "5" : "4"}. Problema</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-1.5">
              <Label>Descrição do problema</Label>
              <Textarea
                rows={4}
                value={descricao}
                onChange={(e) => setDescricao(e.target.value)}
                placeholder="O que foi observado..."
              />
            </div>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
              <div className="space-y-1.5">
                <Label>Quantidade de peças afetadas</Label>
                <Input type="number" min={1} value={quantidade} onChange={(e) => setQuantidade(e.target.value)} />
              </div>
              <div className="space-y-1.5">
                <Label>Classificação</Label>
                <Select
                  value={classificacao}
                  onValueChange={(v) => setClassificacao((v as ClassificacaoNC) ?? "")}
                  items={CLASSIFICACAO_LABEL}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Selecione" />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(CLASSIFICACAO_LABEL).map(([value, label]) => (
                      <SelectItem key={value} value={value}>
                        {label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1.5">
                <Label>Origem</Label>
                <Select value={origem} onValueChange={(v) => setOrigem((v as OrigemNC) ?? "")} items={ORIGEM_LABEL}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Selecione" />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(ORIGEM_LABEL).map(([value, label]) => (
                      <SelectItem key={value} value={value}>
                        {label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-1.5">
              <Label>Modo de falha (opcional)</Label>
              <Input
                placeholder="Ex.: trinca, rebarba, fora de medida..."
                value={modoFalha}
                onChange={(e) => setModoFalha(e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <Label>Fotos</Label>
              <FotoUploadInput arquivos={fotos} onChange={setFotos} />
            </div>
          </CardContent>
        </Card>
      )}

      <Button size="lg" className="w-full" disabled={!pronto || abrirNC.isPending} onClick={handleSubmit}>
        {abrirNC.isPending ? "Abrindo..." : "Abrir RNC"}
      </Button>
    </div>
  )
}
