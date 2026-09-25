import { useState } from "react"
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
import { useMaquinas, useToggleStatusMaquina } from "@/features/maquinas/api"
import { MaquinaFormDialog } from "@/features/maquinas/MaquinaFormDialog"
import { getApiError } from "@/lib/api-client"

export function MaquinasListPage() {
  const { usuario } = useAuth()
  const podeCadastrar = usuario?.perfil === "analista_qualidade" || usuario?.perfil === "gestor_qualidade"

  const [busca, setBusca] = useState("")
  const [dialogAberto, setDialogAberto] = useState(false)

  const { data: maquinas, isLoading } = useMaquinas({ busca: busca || undefined })
  const toggleStatus = useToggleStatusMaquina()

  function handleToggleStatus(maquinaId: number, statusAtual: string) {
    toggleStatus.mutate(
      { maquinaId, ativar: statusAtual === "inativo" },
      { onError: (error) => toast.error(getApiError(error).detail) }
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Máquinas</h1>
        {podeCadastrar && (
          <Button onClick={() => setDialogAberto(true)}>
            <Plus className="size-4" />
            Nova máquina
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
              <TableHead>Status</TableHead>
              {podeCadastrar && <TableHead className="text-right">Ações</TableHead>}
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && (
              <TableRow>
                <TableCell colSpan={4} className="text-center text-muted-foreground">
                  Carregando...
                </TableCell>
              </TableRow>
            )}
            {!isLoading && maquinas?.length === 0 && (
              <TableRow>
                <TableCell colSpan={4} className="text-center text-muted-foreground">
                  Nenhuma máquina encontrada.
                </TableCell>
              </TableRow>
            )}
            {maquinas?.map((maquina) => (
              <TableRow key={maquina.id}>
                <TableCell className="font-medium">{maquina.codigo}</TableCell>
                <TableCell>{maquina.descricao}</TableCell>
                <TableCell>
                  <Badge variant={maquina.status === "ativo" ? "default" : "secondary"}>
                    {maquina.status === "ativo" ? "Ativa" : "Inativa"}
                  </Badge>
                </TableCell>
                {podeCadastrar && (
                  <TableCell className="text-right">
                    <Button variant="ghost" size="sm" onClick={() => handleToggleStatus(maquina.id, maquina.status)}>
                      {maquina.status === "ativo" ? "Inativar" : "Ativar"}
                    </Button>
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <MaquinaFormDialog open={dialogAberto} onOpenChange={setDialogAberto} />
    </div>
  )
}
