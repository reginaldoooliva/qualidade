import { useEffect, useState } from "react"
import { ArrowLeft, History } from "lucide-react"
import { useNavigate, useParams } from "react-router-dom"
import { toast } from "sonner"

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { useAuth } from "@/features/auth/AuthContext"
import { AcoesCorretivasCard } from "@/features/plano_acao/AcoesCorretivasCard"
import { useAtualizarConclusao, useAvancarVerificacao, usePlanoAcao, useTrocarMetodologia } from "@/features/plano_acao/api"
import { CincoPorquesForm } from "@/features/plano_acao/CincoPorquesForm"
import { IshikawaBoard } from "@/features/plano_acao/IshikawaBoard"
import { StatusPlanoBadge } from "@/features/plano_acao/StatusBadges"
import { VerificacaoCard } from "@/features/plano_acao/VerificacaoCard"
import { getApiError } from "@/lib/api-client"
import type { MetodologiaCausaRaiz } from "@/types/api"

const METODOLOGIA_LABEL: Record<MetodologiaCausaRaiz, string> = {
  ishikawa: "Ishikawa (Espinha de Peixe)",
  cinco_porques: "5 Porquês",
  livre: "Análise livre",
}

export function PlanoAcaoDetailPage() {
  const { planoId } = useParams<{ planoId: string }>()
  const id = Number(planoId)
  const navigate = useNavigate()
  const { usuario } = useAuth()
  const podeEditarPerfil = usuario?.perfil === "analista_qualidade" || usuario?.perfil === "gestor_qualidade"

  const { data: plano, isLoading } = usePlanoAcao(id)
  const trocarMetodologia = useTrocarMetodologia(id)
  const atualizarConclusao = useAtualizarConclusao(id)
  const avancarVerificacao = useAvancarVerificacao(id)

  const [conclusao, setConclusao] = useState("")
  const [metodologiaPendente, setMetodologiaPendente] = useState<MetodologiaCausaRaiz | null>(null)

  useEffect(() => {
    if (plano) setConclusao(plano.conclusao_causa_raiz ?? "")
  }, [plano])

  if (isLoading || !plano) {
    return <div className="text-muted-foreground">Carregando...</div>
  }

  const podeEditar = podeEditarPerfil && plano.status !== "encerrado"
  const acoesCicloAtual = plano.acoes_corretivas.filter((a) => a.ciclo === plano.ciclo)
  const podeAvancarVerificacao =
    podeEditar &&
    plano.status === "em_andamento" &&
    acoesCicloAtual.length > 0 &&
    acoesCicloAtual.every((a) => a.status === "concluida")

  function handleAvancar() {
    avancarVerificacao.mutate(undefined, {
      onSuccess: () => toast.success("Plano aguardando verificação de eficácia"),
      onError: (error) => toast.error(getApiError(error).detail),
    })
  }

  function handleSalvarConclusao() {
    atualizarConclusao.mutate(conclusao, {
      onSuccess: () => toast.success("Conclusão salva"),
      onError: (error) => toast.error(getApiError(error).detail),
    })
  }

  function confirmarTrocaMetodologia() {
    if (!metodologiaPendente) return
    trocarMetodologia.mutate(metodologiaPendente, {
      onSuccess: () => {
        toast.success("Metodologia alterada")
        setMetodologiaPendente(null)
      },
      onError: (error) => {
        toast.error(getApiError(error).detail)
        setMetodologiaPendente(null)
      },
    })
  }

  return (
    <div className="space-y-4">
      <Button variant="ghost" size="sm" onClick={() => navigate(`/nao-conformidades/${plano.nc_id}`)}>
        <ArrowLeft className="size-4" />
        RNC {plano.numero_rnc}
      </Button>

      <div className="flex flex-wrap items-center justify-between gap-3 rounded-md border bg-background p-4">
        <div className="flex items-center gap-2">
          <h1 className="text-xl font-semibold">Plano de Ação — {plano.numero_rnc}</h1>
          <StatusPlanoBadge status={plano.status} />
          {plano.ciclo > 1 && <Badge variant="outline">Ciclo {plano.ciclo}</Badge>}
        </div>
        {podeEditar && plano.status === "em_andamento" && (
          <Button onClick={handleAvancar} disabled={!podeAvancarVerificacao || avancarVerificacao.isPending}>
            {avancarVerificacao.isPending ? "Avançando..." : "Avançar para verificação de eficácia"}
          </Button>
        )}
      </div>
      {plano.status === "em_andamento" && !podeAvancarVerificacao && podeEditar && (
        <p className="text-sm text-muted-foreground">
          Todas as ações corretivas do ciclo atual precisam estar "Concluída" para avançar.
        </p>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Investigação de causa raiz</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Metodologia</label>
            <Select
              value={plano.metodologia_causa_raiz}
              onValueChange={(v) => {
                if (v && v !== plano.metodologia_causa_raiz) setMetodologiaPendente(v as MetodologiaCausaRaiz)
              }}
              items={METODOLOGIA_LABEL}
            >
              <SelectTrigger className="w-full sm:w-72" disabled={!podeEditar}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(METODOLOGIA_LABEL).map(([value, label]) => (
                  <SelectItem key={value} value={value}>
                    {label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {plano.metodologia_causa_raiz === "ishikawa" && <IshikawaBoard plano={plano} disabled={!podeEditar} />}
          {plano.metodologia_causa_raiz === "cinco_porques" && (
            <CincoPorquesForm plano={plano} disabled={!podeEditar} />
          )}

          <div className="space-y-1.5">
            <label className="text-sm font-medium">Conclusão da causa raiz</label>
            <Textarea
              rows={3}
              value={conclusao}
              onChange={(e) => setConclusao(e.target.value)}
              disabled={!podeEditar}
              placeholder={
                plano.metodologia_causa_raiz === "livre"
                  ? "Descreva a causa raiz identificada..."
                  : "Preenchido automaticamente ao marcar uma causa como raiz — pode ser ajustado manualmente."
              }
            />
            {podeEditar && conclusao !== (plano.conclusao_causa_raiz ?? "") && (
              <Button size="sm" onClick={handleSalvarConclusao} disabled={atualizarConclusao.isPending}>
                {atualizarConclusao.isPending ? "Salvando..." : "Salvar conclusão"}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      <AcoesCorretivasCard plano={plano} podeEditar={podeEditar} />

      <VerificacaoCard plano={plano} podeEditar={podeEditarPerfil} />

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <History className="size-4" />
            Histórico
          </CardTitle>
        </CardHeader>
        <CardContent>
          {plano.historico.length === 0 ? (
            <p className="text-sm text-muted-foreground">Sem eventos registrados.</p>
          ) : (
            <ul className="space-y-2 text-sm">
              {plano.historico.map((evento, i) => (
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

      <AlertDialog open={!!metodologiaPendente} onOpenChange={(open) => !open && setMetodologiaPendente(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Trocar metodologia de investigação?</AlertDialogTitle>
            <AlertDialogDescription>
              Os dados já preenchidos na metodologia atual serão removidos da tela ativa (permanecem preservados no
              histórico/auditoria) e a conclusão da causa raiz será limpa.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction onClick={confirmarTrocaMetodologia}>Trocar metodologia</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
