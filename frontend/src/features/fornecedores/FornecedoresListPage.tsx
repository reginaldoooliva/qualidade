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
import { useFornecedores, useToggleStatusFornecedor } from "@/features/fornecedores/api"
import { FornecedorFormDialog } from "@/features/fornecedores/FornecedorFormDialog"
import { getApiError } from "@/lib/api-client"

export function FornecedoresListPage() {
  const { usuario } = useAuth()
  const podeCadastrar = usuario?.perfil === "analista_qualidade" || usuario?.perfil === "gestor_qualidade"

  const [busca, setBusca] = useState("")
  const [dialogAberto, setDialogAberto] = useState(false)

  const { data: fornecedores, isLoading } = useFornecedores({ busca: busca || undefined })
  const toggleStatus = useToggleStatusFornecedor()

  function handleToggleStatus(fornecedorId: number, statusAtual: string) {
    toggleStatus.mutate(
      { fornecedorId, ativar: statusAtual === "inativo" },
      { onError: (error) => toast.error(getApiError(error).detail) }
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Fornecedores</h1>
        {podeCadastrar && (
          <Button onClick={() => setDialogAberto(true)}>
            <Plus className="size-4" />
            Novo fornecedor
          </Button>
        )}
      </div>

      <div className="relative max-w-sm">
        <Search className="absolute left-2.5 top-2.5 size-4 text-muted-foreground" />
        <Input
          placeholder="Buscar por código ou nome..."
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
              <TableHead>Nome</TableHead>
              <TableHead>CNPJ</TableHead>
              <TableHead>Status</TableHead>
              {podeCadastrar && <TableHead className="text-right">Ações</TableHead>}
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-muted-foreground">
                  Carregando...
                </TableCell>
              </TableRow>
            )}
            {!isLoading && fornecedores?.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-muted-foreground">
                  Nenhum fornecedor encontrado.
                </TableCell>
              </TableRow>
            )}
            {fornecedores?.map((fornecedor) => (
              <TableRow key={fornecedor.id}>
                <TableCell className="font-medium">{fornecedor.codigo}</TableCell>
                <TableCell>{fornecedor.nome}</TableCell>
                <TableCell>{fornecedor.cnpj ?? "—"}</TableCell>
                <TableCell>
                  <Badge variant={fornecedor.status === "ativo" ? "default" : "secondary"}>
                    {fornecedor.status === "ativo" ? "Ativo" : "Inativo"}
                  </Badge>
                </TableCell>
                {podeCadastrar && (
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleToggleStatus(fornecedor.id, fornecedor.status)}
                    >
                      {fornecedor.status === "ativo" ? "Inativar" : "Ativar"}
                    </Button>
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <FornecedorFormDialog open={dialogAberto} onOpenChange={setDialogAberto} />
    </div>
  )
}
