import { useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { AlertTriangle, ArrowLeft, Info } from "lucide-react"
import { toast } from "sonner"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/features/auth/AuthContext"
import { useReabrirColeta, useRodada } from "@/features/coleta/api"
import { contarAmostrasCompletas, FinalizarColetaDialog, MOTIVO_LABEL } from "@/features/coleta/FinalizarColetaDialog"
import { GradeColeta } from "@/features/coleta/GradeColeta"
import { getApiError } from "@/lib/api-client"

const STATUS_LABEL: Record<string, string> = {
  em_andamento: "Em andamento",
  finalizada: "Finalizada",
  finalizada_com_pendencia: "Finalizada com pendência",
}

export function ColetaDetailPage() {
  const { rodadaId } = useParams<{ rodadaId: string }>()
  const id = Number(rodadaId)
  const navigate = useNavigate()
  const { usuario } = useAuth()
  const podeReabrir = usuario?.perfil === "analista_qualidade" || usuario?.perfil === "gestor_qualidade"

  const { data: rodada, isLoading } = useRodada(id)
  const reabrirColeta = useReabrirColeta()
  const [dialogFinalizarAberto, setDialogFinalizarAberto] = useState(false)
  const [sugestaoRnc, setSugestaoRnc] = useState(false)

  if (isLoading || !rodada) {
    return <div className="text-muted-foreground">Carregando...</div>
  }

  const amostrasCompletas = contarAmostrasCompletas(rodada)
  const emAndamento = rodada.status === "em_andamento"

  function handleReabrir() {
    reabrirColeta.mutate(id, {
      onSuccess: () => {
        toast.success("Rodada reaberta")
        setSugestaoRnc(false)
      },
      onError: (error) => toast.error(getApiError(error).detail),
    })
  }

  return (
    <div className="space-y-4">
      <Button variant="ghost" size="sm" onClick={() => navigate("/coleta/nova")}>
        <ArrowLeft className="size-4" />
        Nova coleta
      </Button>

      <div className="flex flex-wrap items-center justify-between gap-3 rounded-md border bg-background p-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-semibold">
              {rodada.peca.codigo} — Ordem {rodada.ordem.numero_ordem} — Etapa {rodada.etapa.numero_etapa}
            </h1>
            <Badge variant={emAndamento ? "default" : "secondary"}>{STATUS_LABEL[rodada.status]}</Badge>
          </div>
          <p className="text-muted-foreground">
            {rodada.peca.descricao} · {rodada.etapa.descricao ?? `Etapa ${rodada.etapa.numero_etapa}`}
          </p>
          <p className="mt-1 text-sm">
            Amostras completas: <strong>{amostrasCompletas}</strong> de <strong>{rodada.amostras_alvo}</strong>
          </p>
        </div>
        <div className="flex gap-2">
          {emAndamento && <Button onClick={() => setDialogFinalizarAberto(true)}>Finalizar coleta</Button>}
          {!emAndamento && podeReabrir && (
            <Button variant="outline" onClick={handleReabrir} disabled={reabrirColeta.isPending}>
              {reabrirColeta.isPending ? "Reabrindo..." : "Reabrir rodada"}
            </Button>
          )}
        </div>
      </div>

      {!emAndamento && rodada.motivo_encerramento_antecipado && (
        <div className="flex items-start gap-2 rounded-md border border-amber-300 bg-amber-50 p-3 text-sm text-amber-900">
          <AlertTriangle className="mt-0.5 size-4 shrink-0" />
          <div>
            Encerrada com pendência — motivo:{" "}
            <strong>{MOTIVO_LABEL[rodada.motivo_encerramento_antecipado] ?? rodada.motivo_encerramento_antecipado}</strong>
            {rodada.motivo_detalhe && <> — {rodada.motivo_detalhe}</>}
          </div>
        </div>
      )}

      {sugestaoRnc && (
        <div className="flex items-start justify-between gap-3 rounded-md border border-blue-300 bg-blue-50 p-3 text-sm text-blue-900">
          <div className="flex items-start gap-2">
            <Info className="mt-0.5 size-4 shrink-0" />
            <div>Há medições fora de especificação (ou a coleta foi encerrada por não conformidade).</div>
          </div>
          <Button
            size="sm"
            variant="outline"
            className="shrink-0 border-blue-400 bg-transparent text-blue-900 hover:bg-blue-100"
            onClick={() => {
              const params = new URLSearchParams({
                pecaId: String(rodada.peca.id),
                ordemId: String(rodada.ordem.id),
                etapaId: String(rodada.etapa.id),
                rodadaId: String(rodada.id),
                descricao: `Não conformidade identificada na coleta (Ordem ${rodada.ordem.numero_ordem}, Etapa ${rodada.etapa.numero_etapa}).`,
              })
              navigate(`/nao-conformidades/nova?${params.toString()}`)
            }}
          >
            Abrir RNC
          </Button>
        </div>
      )}

      <GradeColeta rodada={rodada} somenteLeitura={!emAndamento} />

      <FinalizarColetaDialog
        open={dialogFinalizarAberto}
        onOpenChange={setDialogFinalizarAberto}
        rodada={rodada}
        onFinalizado={(sugestao) => setSugestaoRnc(sugestao)}
      />
    </div>
  )
}
