import { useState } from "react"
import { Plus, Ruler, Search } from "lucide-react"
import { toast } from "sonner"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { FotoAutenticada } from "@/components/FotoAutenticada"
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
import { useTiposInstrumento, useToggleStatusTipoInstrumento } from "@/features/tipos_instrumento/api"
import { TipoInstrumentoFormDialog } from "@/features/tipos_instrumento/TipoInstrumentoFormDialog"
import { getApiError } from "@/lib/api-client"
import type { TipoInstrumento } from "@/types/api"

export function TiposInstrumentoListPage() {
  const { usuario } = useAuth()
  const podeCadastrar = usuario?.perfil === "analista_qualidade" || usuario?.perfil === "gestor_qualidade"

  const [busca, setBusca] = useState("")
  const [dialogAberto, setDialogAberto] = useState(false)
  const [tipoEditando, setTipoEditando] = useState<TipoInstrumento | undefined>(undefined)

  const { data: tipos, isLoading } = useTiposInstrumento({ busca: busca || undefined })
  const toggleStatus = useToggleStatusTipoInstrumento()

  function handleToggleStatus(tipoId: number, statusAtual: string) {
    toggleStatus.mutate(
      { tipoId, ativar: statusAtual === "inativo" },
      { onError: (error) => toast.error(getApiError(error).detail) }
    )
  }

  function handleNovo() {
    setTipoEditando(undefined)
    setDialogAberto(true)
  }

  function handleEditar(tipo: TipoInstrumento) {
    setTipoEditando(tipo)
    setDialogAberto(true)
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Tipos de Instrumento</h1>
        {podeCadastrar && (
          <Button onClick={handleNovo}>
            <Plus className="size-4" />
            Novo tipo de instrumento
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
              <TableHead className="w-16">Imagem</TableHead>
              <TableHead>Instrumento</TableHead>
              <TableHead>Descrição da função</TableHead>
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
            {!isLoading && tipos?.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-muted-foreground">
                  Nenhum tipo de instrumento encontrado.
                </TableCell>
              </TableRow>
            )}
            {tipos?.map((tipo) => (
              <TableRow key={tipo.id} className="cursor-pointer" onClick={() => handleEditar(tipo)}>
                <TableCell onClick={(e) => e.stopPropagation()}>
                  {tipo.tem_imagem ? (
                    <FotoAutenticada
                      url={`/tipos-instrumento/${tipo.id}/imagem`}
                      alt={tipo.nome}
                      className="size-10 rounded-md border object-cover"
                    />
                  ) : (
                    <div className="flex size-10 items-center justify-center rounded-md border bg-muted text-muted-foreground">
                      <Ruler className="size-4" />
                    </div>
                  )}
                </TableCell>
                <TableCell className="font-medium">{tipo.nome}</TableCell>
                <TableCell className="max-w-sm truncate text-muted-foreground">
                  {tipo.descricao_funcao ?? "—"}
                </TableCell>
                <TableCell>
                  <Badge variant={tipo.status === "ativo" ? "default" : "secondary"}>
                    {tipo.status === "ativo" ? "Ativo" : "Inativo"}
                  </Badge>
                </TableCell>
                {podeCadastrar && (
                  <TableCell className="text-right" onClick={(e) => e.stopPropagation()}>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleToggleStatus(tipo.id, tipo.status)}
                    >
                      {tipo.status === "ativo" ? "Inativar" : "Ativar"}
                    </Button>
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <TipoInstrumentoFormDialog open={dialogAberto} onOpenChange={setDialogAberto} tipo={tipoEditando} />
    </div>
  )
}
