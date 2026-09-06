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
import { useEtapasByPeca } from "@/features/etapas/api"
import { EtapaFormDialog } from "@/features/etapas/EtapaFormDialog"
import { usePeca } from "@/features/pecas/api"
import { PecaFormDialog } from "@/features/pecas/PecaFormDialog"
import type { Etapa } from "@/types/api"

export function PecaDetailPage() {
  const { pecaId } = useParams<{ pecaId: string }>()
  const id = Number(pecaId)
  const navigate = useNavigate()
  const { usuario } = useAuth()
  const podeCadastrar = usuario?.perfil === "analista_qualidade" || usuario?.perfil === "gestor_qualidade"

  const { data: peca, isLoading } = usePeca(id)
  const { data: etapas } = useEtapasByPeca(id)

  const [dialogPecaAberto, setDialogPecaAberto] = useState(false)
  const [dialogEtapaAberto, setDialogEtapaAberto] = useState(false)
  const [etapaEditando, setEtapaEditando] = useState<Etapa | undefined>()

  if (isLoading || !peca) {
    return <div className="text-muted-foreground">Carregando...</div>
  }

  return (
    <div className="space-y-6">
      <Button variant="ghost" size="sm" onClick={() => navigate("/pecas")}>
        <ArrowLeft className="size-4" />
        Voltar
      </Button>

      <div className="flex items-start justify-between rounded-md border bg-background p-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-semibold">{peca.codigo}</h1>
            <Badge variant={peca.status === "ativo" ? "default" : "secondary"}>
              {peca.status === "ativo" ? "Ativa" : "Inativa"}
            </Badge>
          </div>
          <p className="text-muted-foreground">{peca.descricao}</p>
          <dl className="mt-3 grid grid-cols-2 gap-x-8 gap-y-1 text-sm sm:grid-cols-4">
            <div>
              <dt className="text-muted-foreground">Cliente</dt>
              <dd>{peca.cliente ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Revisão</dt>
              <dd>{peca.revisao}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Material</dt>
              <dd>{peca.material ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Desenho</dt>
              <dd>{peca.desenho ?? "—"}</dd>
            </div>
          </dl>
        </div>
        {podeCadastrar && (
          <Button variant="outline" onClick={() => setDialogPecaAberto(true)}>
            Editar peça
          </Button>
        )}
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Etapas do processo</h2>
          {podeCadastrar && (
            <Button
              size="sm"
              onClick={() => {
                setEtapaEditando(undefined)
                setDialogEtapaAberto(true)
              }}
            >
              <Plus className="size-4" />
              Nova etapa
            </Button>
          )}
        </div>

        <div className="rounded-md border bg-background">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nº etapa</TableHead>
                <TableHead>Descrição</TableHead>
                <TableHead>Frequência de medição</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {etapas?.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-muted-foreground">
                    Nenhuma etapa cadastrada.
                  </TableCell>
                </TableRow>
              )}
              {etapas?.map((etapa) => (
                <TableRow
                  key={etapa.id}
                  className="cursor-pointer"
                  onClick={() => navigate(`/pecas/${id}/etapas/${etapa.id}`)}
                >
                  <TableCell className="font-medium">{etapa.numero_etapa}</TableCell>
                  <TableCell>{etapa.descricao ?? "—"}</TableCell>
                  <TableCell>
                    {etapa.freq_numerador}/{etapa.freq_denominador}
                  </TableCell>
                  <TableCell>
                    <Badge variant={etapa.status === "ativo" ? "default" : "secondary"}>
                      {etapa.status === "ativo" ? "Ativa" : "Inativa"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    {podeCadastrar && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation()
                          setEtapaEditando(etapa)
                          setDialogEtapaAberto(true)
                        }}
                      >
                        Editar
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>

      <PecaFormDialog open={dialogPecaAberto} onOpenChange={setDialogPecaAberto} peca={peca} />
      <EtapaFormDialog
        open={dialogEtapaAberto}
        onOpenChange={setDialogEtapaAberto}
        pecaId={id}
        etapa={etapaEditando}
      />
    </div>
  )
}
