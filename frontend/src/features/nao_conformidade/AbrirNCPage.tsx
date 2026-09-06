import { useEffect, useState } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
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
import { Textarea } from "@/components/ui/textarea"
import { useAbrirNC } from "@/features/nao_conformidade/api"
import { useCaracteristicasByEtapa } from "@/features/caracteristicas/api"
import { useEtapasByPeca } from "@/features/etapas/api"
import { usePeca } from "@/features/pecas/api"
import { PecaBuscaInput } from "@/features/pecas/PecaBuscaInput"
import { getApiError } from "@/lib/api-client"
import type { ClassificacaoNC, OrigemNC, PecaListItem } from "@/types/api"

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

  const abrirNC = useAbrirNC()

  const pronto = !!peca && descricao.trim() !== "" && Number(quantidade) > 0 && !!classificacao && !!origem

  function handleSubmit() {
    if (!peca || !classificacao || !origem) return
    abrirNC.mutate(
      {
        peca_id: peca.id,
        etapa_id: etapaId ? Number(etapaId) : undefined,
        caracteristica_id: caracteristicaId ? Number(caracteristicaId) : undefined,
        ordem_id: ordemIdPrefill,
        rodada_id: rodadaIdPrefill,
        descricao_problema: descricao,
        quantidade_afetada: Number(quantidade),
        classificacao,
        origem,
      },
      {
        onSuccess: (nc) => {
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
          <CardTitle className="text-base">1. Peça</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <PecaBuscaInput value={peca} onChange={setPeca} />
        </CardContent>
      </Card>

      {peca && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">2. Etapa e característica (opcional)</CardTitle>
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

      {peca && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">3. Problema</CardTitle>
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
          </CardContent>
        </Card>
      )}

      <Button size="lg" className="w-full" disabled={!pronto || abrirNC.isPending} onClick={handleSubmit}>
        {abrirNC.isPending ? "Abrindo..." : "Abrir RNC"}
      </Button>
    </div>
  )
}
