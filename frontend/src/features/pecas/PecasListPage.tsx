import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Plus, Search } from "lucide-react"
import { toast } from "sonner"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useAuth } from "@/features/auth/AuthContext"
import { usePecas, useToggleStatusPeca } from "@/features/pecas/api"
import { PecaFormDialog } from "@/features/pecas/PecaFormDialog"
import { getApiError } from "@/lib/api-client"

export function PecasListPage() {
  const { usuario } = useAuth()
  const podeCadastrar = usuario?.perfil === "analista_qualidade" || usuario?.perfil === "gestor_qualidade"

  const [busca, setBusca] = useState("")
  const [dialogAberto, setDialogAberto] = useState(false)
  const navigate = useNavigate()

  const { data: pecas, isLoading } = usePecas({ busca: busca || undefined })
  const toggleStatus = useToggleStatusPeca()

  function handleToggleStatus(pecaId: number, statusAtual: string) {
    toggleStatus.mutate(
      { pecaId, ativar: statusAtual === "inativo" },
      { onError: (error) => toast.error(getApiError(error).detail) }
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Peças</h1>
        {podeCadastrar && (
          <Button onClick={() => setDialogAberto(true)}>
            <Plus className="size-4" />
            Nova peça
          </Button>
        )}
      </div>

      <div className="relative max-w-sm">
        <Search className="absolute left-2.5 top-2.5 size-4 text-muted-foreground" />
        <Input
          placeholder="Buscar por código ou descrição..."
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          className="pl-8"
        />
      </div>

      <div className="rounded-md border bg-background">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Código</TableHead>
              <TableHead>Descrição</TableHead>
              <TableHead>Cliente</TableHead>
              <TableHead className="text-center">Características</TableHead>
              <TableHead>Status</TableHead>
              {podeCadastrar && <TableHead className="text-right">Ações</TableHead>}
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-muted-foreground">
                  Carregando...
                </TableCell>
              </TableRow>
            )}
            {!isLoading && pecas?.length === 0 && (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-muted-foreground">
                  Nenhuma peça encontrada.
                </TableCell>
              </TableRow>
            )}
            {pecas?.map((peca) => (
              <TableRow
                key={peca.id}
                className="cursor-pointer"
                onClick={() => navigate(`/pecas/${peca.id}`)}
              >
                <TableCell className="font-medium">{peca.codigo}</TableCell>
                <TableCell>{peca.descricao}</TableCell>
                <TableCell>{peca.cliente ?? "—"}</TableCell>
                <TableCell className="text-center">{peca.numero_caracteristicas}</TableCell>
                <TableCell>
                  <Badge variant={peca.status === "ativo" ? "default" : "secondary"}>
                    {peca.status === "ativo" ? "Ativa" : "Inativa"}
                  </Badge>
                </TableCell>
                {podeCadastrar && (
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleToggleStatus(peca.id, peca.status)
                      }}
                    >
                      {peca.status === "ativo" ? "Inativar" : "Ativar"}
                    </Button>
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <PecaFormDialog open={dialogAberto} onOpenChange={setDialogAberto} />
    </div>
  )
}
