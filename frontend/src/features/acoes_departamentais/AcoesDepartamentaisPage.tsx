import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  useAcoesDepartamentaisPendentes,
  useConcluirAcaoDepartamentalGenerico,
} from "@/features/acoes_departamentais/api"
import { ConcluirAcaoDialog } from "@/features/acoes_departamentais/ConcluirAcaoDialog"
import { useAuth } from "@/features/auth/AuthContext"
import { useDepartamentos } from "@/features/departamentos/api"
import { getApiError } from "@/lib/api-client"
import type { AcaoDepartamentalListItem } from "@/types/api"

export function AcoesDepartamentaisPage() {
  const { usuario } = useAuth()
  const ehQualidade = usuario?.perfil === "analista_qualidade" || usuario?.perfil === "gestor_qualidade"
  const navigate = useNavigate()

  const [departamentoFiltro, setDepartamentoFiltro] = useState<string>(
    ehQualidade ? "" : usuario?.departamento_id ? String(usuario.departamento_id) : ""
  )
  const { data: departamentos } = useDepartamentos()
  const { data: acoes, isLoading } = useAcoesDepartamentaisPendentes(
    departamentoFiltro ? Number(departamentoFiltro) : undefined
  )
  const concluir = useConcluirAcaoDepartamentalGenerico()

  const [acaoSelecionada, setAcaoSelecionada] = useState<AcaoDepartamentalListItem | null>(null)

  function handleConfirmarConclusao(observacao: string) {
    if (!acaoSelecionada) return
    concluir.mutate(
      { ncId: acaoSelecionada.nc_id, acaoId: acaoSelecionada.id, observacao },
      {
        onSuccess: () => {
          toast.success("Tratativa concluída")
          setAcaoSelecionada(null)
        },
        onError: (error) => toast.error(getApiError(error).detail),
      }
    )
  }

  if (!ehQualidade && !usuario?.departamento_id) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-semibold tracking-tight">Tratativas por Departamento</h1>
        <p className="text-muted-foreground">
          Seu usuário ainda não tem um departamento definido. Peça ao Gestor de Qualidade para
          atribuir um departamento ao seu usuário.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold tracking-tight">Tratativas por Departamento</h1>

      {ehQualidade && (
        <div className="max-w-xs space-y-1.5">
          <Select
            value={departamentoFiltro}
            onValueChange={(v) => setDepartamentoFiltro(v ?? "")}
            items={{ "": "Todos os departamentos", ...Object.fromEntries((departamentos ?? []).map((d) => [String(d.id), d.nome])) }}
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Todos os departamentos" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">Todos os departamentos</SelectItem>
              {(departamentos ?? []).map((d) => (
                <SelectItem key={d.id} value={String(d.id)}>
                  {d.nome}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}

      <div className="rounded-md border bg-background">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nº RNC</TableHead>
              <TableHead>Peça</TableHead>
              <TableHead>Departamento</TableHead>
              <TableHead>Descrição</TableHead>
              <TableHead>Criada em</TableHead>
              <TableHead className="text-right">Ações</TableHead>
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
            {!isLoading && acoes?.length === 0 && (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-muted-foreground">
                  Nenhuma tratativa pendente.
                </TableCell>
              </TableRow>
            )}
            {acoes?.map((acao) => (
              <TableRow
                key={acao.id}
                className="cursor-pointer"
                onClick={() => navigate(`/nao-conformidades/${acao.nc_id}`)}
              >
                <TableCell className="font-medium">{acao.numero_rnc}</TableCell>
                <TableCell>
                  {acao.peca_codigo} — {acao.peca_descricao}
                </TableCell>
                <TableCell>{acao.departamento.nome}</TableCell>
                <TableCell className="max-w-xs truncate">{acao.descricao}</TableCell>
                <TableCell>{new Date(acao.criado_em).toLocaleDateString("pt-BR")}</TableCell>
                <TableCell className="text-right">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation()
                      setAcaoSelecionada(acao)
                    }}
                  >
                    Concluir
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <ConcluirAcaoDialog
        open={!!acaoSelecionada}
        onOpenChange={(open) => !open && setAcaoSelecionada(null)}
        onConfirmar={handleConfirmarConclusao}
        pendente={concluir.isPending}
      />
    </div>
  )
}
