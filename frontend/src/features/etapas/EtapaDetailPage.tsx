import { useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { ArrowLeft, Plus } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useAuth } from "@/features/auth/AuthContext"
import { useCaracteristicasByEtapa } from "@/features/caracteristicas/api"
import { CaracteristicaFormDialog } from "@/features/caracteristicas/CaracteristicaFormDialog"
import { useEtapa } from "@/features/etapas/api"
import { EtapaFormDialog } from "@/features/etapas/EtapaFormDialog"
import { usePeca } from "@/features/pecas/api"
import type { Caracteristica } from "@/types/api"

export function EtapaDetailPage() {
  const { pecaId, etapaId } = useParams<{ pecaId: string; etapaId: string }>()
  const pecaIdNum = Number(pecaId)
  const etapaIdNum = Number(etapaId)
  const navigate = useNavigate()
  const { usuario } = useAuth()
  const podeCadastrar = usuario?.perfil === "analista_qualidade" || usuario?.perfil === "gestor_qualidade"

  const { data: peca } = usePeca(pecaIdNum)
  const { data: etapa, isLoading } = useEtapa(etapaIdNum)
  const { data: caracteristicas } = useCaracteristicasByEtapa(etapaIdNum)

  const [dialogEtapaAberto, setDialogEtapaAberto] = useState(false)
  const [dialogCaracteristicaAberto, setDialogCaracteristicaAberto] = useState(false)
  const [caracteristicaEditando, setCaracteristicaEditando] = useState<Caracteristica | undefined>()

  if (isLoading || !etapa) {
    return <div className="text-muted-foreground">Carregando...</div>
  }

  return (
    <div className="space-y-6">
      <Button variant="ghost" size="sm" onClick={() => navigate(`/pecas/${pecaIdNum}`)}>
        <ArrowLeft className="size-4" />
        Voltar para {peca?.codigo ?? "peça"}
      </Button>

      <div className="flex items-start justify-between rounded-md border bg-background p-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-semibold">Etapa {etapa.numero_etapa}</h1>
            <Badge variant={etapa.status === "ativo" ? "default" : "secondary"}>
              {etapa.status === "ativo" ? "Ativa" : "Inativa"}
            </Badge>
          </div>
          <p className="text-muted-foreground">{etapa.descricao ?? "Sem descrição"}</p>
          <p className="mt-2 text-sm">
            Frequência de medição:{" "}
            <strong>
              {etapa.freq_numerador}/{etapa.freq_denominador}
            </strong>
          </p>
        </div>
        {podeCadastrar && (
          <Button variant="outline" onClick={() => setDialogEtapaAberto(true)}>
            Editar etapa
          </Button>
        )}
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Características (cotas)</h2>
          {podeCadastrar && (
            <Button
              size="sm"
              onClick={() => {
                setCaracteristicaEditando(undefined)
                setDialogCaracteristicaAberto(true)
              }}
            >
              <Plus className="size-4" />
              Nova característica
            </Button>
          )}
        </div>

        <div className="rounded-md border bg-background">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Nominal</TableHead>
                <TableHead>LIE</TableHead>
                <TableHead>LSE</TableHead>
                <TableHead>Unidade</TableHead>
                <TableHead>Instrumento</TableHead>
                <TableHead>Status</TableHead>
                {podeCadastrar && <TableHead className="text-right">Ações</TableHead>}
              </TableRow>
            </TableHeader>
            <TableBody>
              {caracteristicas?.length === 0 && (
                <TableRow>
                  <TableCell colSpan={8} className="text-center text-muted-foreground">
                    Nenhuma característica cadastrada.
                  </TableCell>
                </TableRow>
              )}
              {caracteristicas?.map((c) => (
                <TableRow key={c.id}>
                  <TableCell className="font-medium">
                    {c.nome}
                    {c.posicao_desenho && (
                      <span className="ml-1 text-muted-foreground">(item {c.posicao_desenho})</span>
                    )}
                  </TableCell>
                  <TableCell>{c.nominal.toFixed(c.casas_decimais)}</TableCell>
                  <TableCell>{c.lie.toFixed(c.casas_decimais)}</TableCell>
                  <TableCell>{c.lse.toFixed(c.casas_decimais)}</TableCell>
                  <TableCell>{c.unidade}</TableCell>
                  <TableCell>{c.tipo_instrumento?.nome ?? "—"}</TableCell>
                  <TableCell>
                    <Badge variant={c.status === "ativo" ? "default" : "secondary"}>
                      {c.status === "ativo" ? "Ativa" : "Inativa"}
                    </Badge>
                  </TableCell>
                  {podeCadastrar && (
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setCaracteristicaEditando(c)
                          setDialogCaracteristicaAberto(true)
                        }}
                      >
                        Editar
                      </Button>
                    </TableCell>
                  )}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>

      <EtapaFormDialog
        open={dialogEtapaAberto}
        onOpenChange={setDialogEtapaAberto}
        pecaId={pecaIdNum}
        etapa={etapa}
      />
      <CaracteristicaFormDialog
        open={dialogCaracteristicaAberto}
        onOpenChange={setDialogCaracteristicaAberto}
        etapaId={etapaIdNum}
        caracteristica={caracteristicaEditando}
      />
    </div>
  )
}
