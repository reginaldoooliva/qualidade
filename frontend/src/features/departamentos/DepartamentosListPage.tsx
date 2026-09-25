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
import { useDepartamentos, useToggleStatusDepartamento } from "@/features/departamentos/api"
import { DepartamentoFormDialog } from "@/features/departamentos/DepartamentoFormDialog"
import { getApiError } from "@/lib/api-client"

export function DepartamentosListPage() {
  const { usuario } = useAuth()
  const podeCadastrar = usuario?.perfil === "analista_qualidade" || usuario?.perfil === "gestor_qualidade"

  const [busca, setBusca] = useState("")
  const [dialogAberto, setDialogAberto] = useState(false)

  const { data: departamentos, isLoading } = useDepartamentos({ busca: busca || undefined })
  const toggleStatus = useToggleStatusDepartamento()

  function handleToggleStatus(departamentoId: number, statusAtual: string) {
    toggleStatus.mutate(
      { departamentoId, ativar: statusAtual === "inativo" },
      { onError: (error) => toast.error(getApiError(error).detail) }
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Departamentos</h1>
        {podeCadastrar && (
          <Button onClick={() => setDialogAberto(true)}>
            <Plus className="size-4" />
            Novo departamento
          </Button>
        )}
      </div>

      <div className="relative max-w-sm">
        <Search className="absolute left-2.5 top-2.5 size-4 text-muted-foreground" />
        <Input
          placeholder="Buscar por nome..."
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          className="pl-8"
        />
      </div>

      <div className="rounded-md border bg-background">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nome</TableHead>
              <TableHead>Status</TableHead>
              {podeCadastrar && <TableHead className="text-right">Ações</TableHead>}
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && (
              <TableRow>
                <TableCell colSpan={3} className="text-center text-muted-foreground">
                  Carregando...
                </TableCell>
              </TableRow>
            )}
            {!isLoading && departamentos?.length === 0 && (
              <TableRow>
                <TableCell colSpan={3} className="text-center text-muted-foreground">
                  Nenhum departamento encontrado.
                </TableCell>
              </TableRow>
            )}
            {departamentos?.map((departamento) => (
              <TableRow key={departamento.id}>
                <TableCell className="font-medium">{departamento.nome}</TableCell>
                <TableCell>
                  <Badge variant={departamento.status === "ativo" ? "default" : "secondary"}>
                    {departamento.status === "ativo" ? "Ativo" : "Inativo"}
                  </Badge>
                </TableCell>
                {podeCadastrar && (
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleToggleStatus(departamento.id, departamento.status)}
                    >
                      {departamento.status === "ativo" ? "Inativar" : "Ativar"}
                    </Button>
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <DepartamentoFormDialog open={dialogAberto} onOpenChange={setDialogAberto} />
    </div>
  )
}
