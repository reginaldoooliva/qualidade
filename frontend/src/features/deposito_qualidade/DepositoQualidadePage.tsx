import { useState } from "react"
import { LockOpen, Plus, Search } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
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
import { useBloqueios, useBuscarBloqueiosPorCodigoPeca } from "@/features/deposito_qualidade/api"
import { LiberarBloqueioDialog } from "@/features/deposito_qualidade/LiberarBloqueioDialog"
import { NovoBloqueioDialog } from "@/features/deposito_qualidade/NovoBloqueioDialog"
import type { BloqueioDeposito, PecaListItem } from "@/types/api"

function StatusBadge({ status }: { status: BloqueioDeposito["status"] }) {
  return status === "bloqueado" ? (
    <Badge variant="destructive">Bloqueado</Badge>
  ) : (
    <Badge variant="secondary">Liberado</Badge>
  )
}

export function DepositoQualidadePage() {
  const { usuario } = useAuth()
  const podeCadastrar = usuario?.perfil === "analista_qualidade" || usuario?.perfil === "gestor_qualidade"

  const [buscaInput, setBuscaInput] = useState("")
  const [codigoBuscado, setCodigoBuscado] = useState<string | undefined>(undefined)
  const { data: resultado, isFetching, isError } = useBuscarBloqueiosPorCodigoPeca(codigoBuscado)

  const [dialogAberto, setDialogAberto] = useState(false)
  const [bloqueioParaLiberar, setBloqueioParaLiberar] = useState<BloqueioDeposito | null>(null)

  const { data: bloqueiosGerais, isLoading } = useBloqueios()

  const pecaEncontradaComoListItem: PecaListItem | null = resultado
    ? { ...resultado.peca, numero_caracteristicas: 0 }
    : null

  function handleBuscar() {
    setCodigoBuscado(buscaInput.trim() || undefined)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Depósito da Qualidade</h1>
        {podeCadastrar && (
          <Button onClick={() => setDialogAberto(true)}>
            <Plus className="size-4" />
            Novo bloqueio
          </Button>
        )}
      </div>

      <Card>
        <CardContent className="space-y-4 pt-6">
          <div className="flex gap-2">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-2.5 top-2.5 size-4 text-muted-foreground" />
              <Input
                placeholder="Digite o código da peça..."
                value={buscaInput}
                onChange={(e) => setBuscaInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleBuscar()}
                className="pl-8"
              />
            </div>
            <Button variant="outline" onClick={handleBuscar} disabled={isFetching}>
              Buscar
            </Button>
          </div>

          {isError && codigoBuscado && (
            <p className="text-sm text-muted-foreground">
              Nenhuma peça encontrada com o código "{codigoBuscado}".
            </p>
          )}

          {resultado && (
            <div className="space-y-3">
              <div className="flex items-center justify-between rounded-md border bg-muted/30 px-3 py-2">
                <div>
                  <div className="font-medium">{resultado.peca.codigo}</div>
                  <div className="text-sm text-muted-foreground">{resultado.peca.descricao}</div>
                </div>
                {podeCadastrar && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setDialogAberto(true)}
                  >
                    <Plus className="size-4" />
                    Bloquear novamente
                  </Button>
                )}
              </div>

              {resultado.bloqueios.length === 0 && (
                <p className="text-sm text-muted-foreground">
                  Esta peça nunca foi bloqueada no depósito da qualidade.
                </p>
              )}

              {resultado.bloqueios.map((bloqueio) => (
                <Card key={bloqueio.id}>
                  <CardContent className="space-y-2 pt-6">
                    <div className="flex items-center justify-between">
                      <StatusBadge status={bloqueio.status} />
                      <span className="text-xs text-muted-foreground">
                        {new Date(bloqueio.criado_em).toLocaleString("pt-BR")} por {bloqueio.criado_por_nome}
                      </span>
                    </div>
                    <p className="text-sm">{bloqueio.motivo}</p>
                    {bloqueio.caracteristica_atencao && (
                      <p className="text-sm text-muted-foreground">
                        <span className="font-medium">Característica de atenção:</span>{" "}
                        {bloqueio.caracteristica_atencao}
                      </p>
                    )}
                    {bloqueio.cliente && (
                      <p className="text-sm text-muted-foreground">
                        <span className="font-medium">Cliente:</span> {bloqueio.cliente}
                      </p>
                    )}
                    {bloqueio.tem_foto && (
                      <FotoAutenticada
                        url={`/deposito-qualidade/${bloqueio.id}/foto`}
                        alt="Foto do bloqueio"
                        className="h-32 w-32 rounded-md border object-cover"
                      />
                    )}
                    {bloqueio.status === "liberado" && (
                      <p className="text-sm text-muted-foreground">
                        <span className="font-medium">Liberado</span> em{" "}
                        {bloqueio.data_liberacao && new Date(bloqueio.data_liberacao).toLocaleString("pt-BR")} por{" "}
                        {bloqueio.liberado_por_nome} — {bloqueio.observacao_liberacao}
                      </p>
                    )}
                    {podeCadastrar && bloqueio.status === "bloqueado" && (
                      <Button variant="outline" size="sm" onClick={() => setBloqueioParaLiberar(bloqueio)}>
                        <LockOpen className="size-4" />
                        Liberar
                      </Button>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <div className="space-y-2">
        <h2 className="text-lg font-medium">Todos os bloqueios</h2>
        <div className="rounded-md border bg-background">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Peça</TableHead>
                <TableHead>Motivo</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Registrado por</TableHead>
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
              {!isLoading && bloqueiosGerais?.length === 0 && (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-muted-foreground">
                    Nenhum bloqueio registrado.
                  </TableCell>
                </TableRow>
              )}
              {bloqueiosGerais?.map((bloqueio) => (
                <TableRow key={bloqueio.id}>
                  <TableCell className="font-medium">{bloqueio.peca.codigo}</TableCell>
                  <TableCell className="max-w-md truncate">{bloqueio.motivo}</TableCell>
                  <TableCell>
                    <StatusBadge status={bloqueio.status} />
                  </TableCell>
                  <TableCell>{bloqueio.criado_por_nome}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>

      <NovoBloqueioDialog
        open={dialogAberto}
        onOpenChange={setDialogAberto}
        pecaInicial={pecaEncontradaComoListItem}
      />
      <LiberarBloqueioDialog
        open={!!bloqueioParaLiberar}
        onOpenChange={(open) => !open && setBloqueioParaLiberar(null)}
        bloqueio={bloqueioParaLiberar}
      />
    </div>
  )
}
