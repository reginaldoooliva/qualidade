import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
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
import { useIniciarColeta, useOrdemPorNumero } from "@/features/coleta/api"
import { useEtapasByPeca } from "@/features/etapas/api"
import { PecaBuscaInput } from "@/features/pecas/PecaBuscaInput"
import { getApiError } from "@/lib/api-client"
import type { PecaListItem } from "@/types/api"

export function NovaColetaPage() {
  const navigate = useNavigate()

  const [peca, setPeca] = useState<PecaListItem | null>(null)

  const [numeroOrdem, setNumeroOrdem] = useState("")
  const [numeroOrdemConfirmado, setNumeroOrdemConfirmado] = useState("")
  const { data: ordemExistente, isFetched: ordemFoiChecada } = useOrdemPorNumero(peca?.id, numeroOrdemConfirmado)
  const [quantidadeOrdem, setQuantidadeOrdem] = useState("")

  const { data: etapas } = useEtapasByPeca(peca?.id)
  const [etapaId, setEtapaId] = useState<string>("")
  const etapaSelecionada = etapas?.find((e) => String(e.id) === etapaId)
  const etapasAtivas = etapas?.filter((e) => e.status === "ativo") ?? []
  const etapaItems = Object.fromEntries(
    etapasAtivas.map((e) => [String(e.id), `Etapa ${e.numero_etapa}${e.descricao ? ` — ${e.descricao}` : ""}`])
  )

  const [amostrasAjustadas, setAmostrasAjustadas] = useState("")
  const [justificativa, setJustificativa] = useState("")

  const iniciarColeta = useIniciarColeta()

  useEffect(() => {
    setNumeroOrdem("")
    setNumeroOrdemConfirmado("")
    setQuantidadeOrdem("")
    setEtapaId("")
  }, [peca?.id])

  useEffect(() => {
    setAmostrasAjustadas("")
    setJustificativa("")
  }, [etapaId])

  const quantidade = ordemExistente ? ordemExistente.quantidade : Number(quantidadeOrdem) || 0
  const amostrasCalculadas =
    etapaSelecionada && quantidade > 0
      ? Math.max(1, Math.ceil((quantidade * etapaSelecionada.freq_numerador) / etapaSelecionada.freq_denominador))
      : null

  const prontoParaIniciar =
    !!peca &&
    numeroOrdemConfirmado.trim() !== "" &&
    (ordemExistente ? true : Number(quantidadeOrdem) > 0) &&
    !!etapaSelecionada

  function confirmarOrdem() {
    setNumeroOrdemConfirmado(numeroOrdem.trim())
  }

  function handleIniciar() {
    if (!peca || !etapaSelecionada) return
    iniciarColeta.mutate(
      {
        peca_id: peca.id,
        numero_ordem: numeroOrdemConfirmado,
        quantidade_ordem: ordemExistente ? undefined : Number(quantidadeOrdem),
        etapa_id: etapaSelecionada.id,
        amostras_ajustadas: amostrasAjustadas ? Number(amostrasAjustadas) : undefined,
        justificativa_ajuste: justificativa || undefined,
      },
      {
        onSuccess: (rodada) => navigate(`/coleta/${rodada.id}`),
        onError: (error) => toast.error(getApiError(error).detail),
      }
    )
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <h1 className="text-2xl font-semibold tracking-tight">Nova coleta</h1>

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
            <CardTitle className="text-base">2. Ordem de produção</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-1.5">
              <Label>Nº da ordem</Label>
              <Input
                name="numero_ordem"
                value={numeroOrdem}
                onChange={(e) => setNumeroOrdem(e.target.value)}
                onBlur={confirmarOrdem}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault()
                    confirmarOrdem()
                  }
                }}
                placeholder="Ex: OP-4521"
              />
            </div>
            {numeroOrdemConfirmado &&
              ordemFoiChecada &&
              (ordemExistente ? (
                <p className="text-sm text-muted-foreground">
                  Ordem já cadastrada — quantidade: <strong>{ordemExistente.quantidade}</strong> (reaproveitada de
                  outra etapa desta peça)
                </p>
              ) : (
                <div className="space-y-1.5">
                  <Label>Quantidade a produzir (ordem nova)</Label>
                  <Input
                    name="quantidade_ordem"
                    type="number"
                    min={1}
                    value={quantidadeOrdem}
                    onChange={(e) => setQuantidadeOrdem(e.target.value)}
                  />
                </div>
              ))}
          </CardContent>
        </Card>
      )}

      {peca && numeroOrdemConfirmado && (ordemExistente || Number(quantidadeOrdem) > 0) && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">3. Etapa</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Select value={etapaId} onValueChange={(value) => setEtapaId(value ?? "")} items={etapaItems}>
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

            {etapaSelecionada && amostrasCalculadas !== null && (
              <div className="space-y-3 rounded-md border bg-muted/30 p-3">
                <p className="text-sm">
                  Frequência de medição:{" "}
                  <strong>
                    {etapaSelecionada.freq_numerador}/{etapaSelecionada.freq_denominador}
                  </strong>{" "}
                  — esta rodada terá <strong>{amostrasCalculadas}</strong> amostra(s).
                </p>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1.5">
                    <Label>Ajustar nº de amostras (opcional)</Label>
                    <Input
                      name="amostras_ajustadas"
                      type="number"
                      min={1}
                      placeholder={String(amostrasCalculadas)}
                      value={amostrasAjustadas}
                      onChange={(e) => setAmostrasAjustadas(e.target.value)}
                    />
                  </div>
                  <div className="space-y-1.5">
                    <Label>Justificativa do ajuste (opcional)</Label>
                    <Input
                      name="justificativa_ajuste"
                      value={justificativa}
                      onChange={(e) => setJustificativa(e.target.value)}
                    />
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <Button
        size="lg"
        className="w-full"
        disabled={!prontoParaIniciar || iniciarColeta.isPending}
        onClick={handleIniciar}
      >
        {iniciarColeta.isPending ? "Iniciando..." : "Iniciar coleta"}
      </Button>
    </div>
  )
}
