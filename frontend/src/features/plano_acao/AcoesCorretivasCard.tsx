import { useState } from "react"
import { Plus } from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
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
import { Textarea } from "@/components/ui/textarea"
import { useAdicionarAcao, useConcluirAcao } from "@/features/plano_acao/api"
import { StatusAcaoBadge } from "@/features/plano_acao/StatusBadges"
import { useUsuarios } from "@/features/usuarios/api"
import { getApiError } from "@/lib/api-client"
import { formatarDataBR } from "@/lib/utils"
import type { PlanoDeAcaoDetalhe } from "@/types/api"

export function AcoesCorretivasCard({ plano, podeEditar }: { plano: PlanoDeAcaoDetalhe; podeEditar: boolean }) {
  const [formAberto, setFormAberto] = useState(false)
  const [descricao, setDescricao] = useState("")
  const [responsavelId, setResponsavelId] = useState("")
  const [prazo, setPrazo] = useState("")

  const { data: usuarios } = useUsuarios()
  const usuarioItems = Object.fromEntries((usuarios ?? []).map((u) => [String(u.id), u.nome]))
  const adicionarAcao = useAdicionarAcao(plano.id)
  const concluirAcao = useConcluirAcao(plano.id)

  const acoesCicloAtual = plano.acoes_corretivas.filter((a) => a.ciclo === plano.ciclo)
  const acoesAnteriores = plano.acoes_corretivas.filter((a) => a.ciclo !== plano.ciclo)

  function handleAdicionar() {
    if (!descricao.trim() || !responsavelId || !prazo) return
    adicionarAcao.mutate(
      { descricao, responsavel_id: Number(responsavelId), prazo },
      {
        onSuccess: () => {
          setDescricao("")
          setResponsavelId("")
          setPrazo("")
          setFormAberto(false)
        },
        onError: (error) => toast.error(getApiError(error).detail),
      }
    )
  }

  function renderTabela(acoes: PlanoDeAcaoDetalhe["acoes_corretivas"], permiteConcluir: boolean) {
    return (
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Descrição</TableHead>
            <TableHead>Responsável</TableHead>
            <TableHead>Prazo</TableHead>
            <TableHead>Status</TableHead>
            {permiteConcluir && <TableHead />}
          </TableRow>
        </TableHeader>
        <TableBody>
          {acoes.map((acao) => (
            <TableRow key={acao.id}>
              <TableCell>{acao.descricao}</TableCell>
              <TableCell>{acao.responsavel_nome}</TableCell>
              <TableCell>{formatarDataBR(acao.prazo)}</TableCell>
              <TableCell>
                <StatusAcaoBadge status={acao.status} />
              </TableCell>
              {permiteConcluir && (
                <TableCell>
                  {acao.status !== "concluida" && podeEditar && (
                    <Button size="sm" variant="outline" onClick={() => concluirAcao.mutate(acao.id)}>
                      Concluir
                    </Button>
                  )}
                </TableCell>
              )}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    )
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <CardTitle className="text-base">Ações corretivas</CardTitle>
        {podeEditar && !formAberto && (
          <Button size="sm" variant="outline" onClick={() => setFormAberto(true)}>
            <Plus className="size-4" />
            Adicionar ação
          </Button>
        )}
      </CardHeader>
      <CardContent className="space-y-3">
        {formAberto && (
          <div className="space-y-3 rounded-md border bg-muted/30 p-3">
            <div className="space-y-1.5">
              <Label>Descrição da ação</Label>
              <Textarea rows={2} value={descricao} onChange={(e) => setDescricao(e.target.value)} />
            </div>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div className="space-y-1.5">
                <Label>Responsável</Label>
                <Select value={responsavelId} onValueChange={(v) => setResponsavelId(v ?? "")} items={usuarioItems}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Selecione" />
                  </SelectTrigger>
                  <SelectContent>
                    {(usuarios ?? []).map((u) => (
                      <SelectItem key={u.id} value={String(u.id)}>
                        {u.nome}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1.5">
                <Label>Prazo</Label>
                <Input type="date" value={prazo} onChange={(e) => setPrazo(e.target.value)} />
              </div>
            </div>
            <div className="flex gap-2">
              <Button
                size="sm"
                onClick={handleAdicionar}
                disabled={!descricao.trim() || !responsavelId || !prazo || adicionarAcao.isPending}
              >
                {adicionarAcao.isPending ? "Salvando..." : "Salvar ação"}
              </Button>
              <Button size="sm" variant="ghost" onClick={() => setFormAberto(false)}>
                Cancelar
              </Button>
            </div>
          </div>
        )}

        {acoesCicloAtual.length === 0 ? (
          <p className="text-sm text-muted-foreground">Nenhuma ação corretiva cadastrada neste ciclo.</p>
        ) : (
          renderTabela(acoesCicloAtual, true)
        )}

        {acoesAnteriores.length > 0 && (
          <details className="text-sm">
            <summary className="cursor-pointer text-muted-foreground">
              Ações de ciclos anteriores ({acoesAnteriores.length})
            </summary>
            <div className="mt-2">{renderTabela(acoesAnteriores, false)}</div>
          </details>
        )}
      </CardContent>
    </Card>
  )
}
