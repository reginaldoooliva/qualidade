import { useEffect, useState } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { FotoUploadInput } from "@/components/FotoUploadInput"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { useCriarBloqueio, useUploadFotoBloqueio } from "@/features/deposito_qualidade/api"
import { PecaBuscaInput } from "@/features/pecas/PecaBuscaInput"
import { getApiError } from "@/lib/api-client"
import type { PecaListItem } from "@/types/api"

export function NovoBloqueioDialog({
  open,
  onOpenChange,
  pecaInicial,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  pecaInicial?: PecaListItem | null
}) {
  const [peca, setPeca] = useState<PecaListItem | null>(null)
  const [motivo, setMotivo] = useState("")
  const [caracteristicaAtencao, setCaracteristicaAtencao] = useState("")
  const [cliente, setCliente] = useState("")
  const [foto, setFoto] = useState<File | null>(null)

  const criarBloqueio = useCriarBloqueio()
  const uploadFoto = useUploadFotoBloqueio()

  useEffect(() => {
    if (open) {
      setPeca(pecaInicial ?? null)
      setMotivo("")
      setCaracteristicaAtencao("")
      setCliente("")
      setFoto(null)
    }
  }, [open, pecaInicial])

  const pronto = !!peca && motivo.trim() !== ""

  function handleSubmit() {
    if (!peca || motivo.trim() === "") return
    criarBloqueio.mutate(
      {
        peca_id: peca.id,
        motivo,
        caracteristica_atencao: caracteristicaAtencao || undefined,
        cliente: cliente || undefined,
      },
      {
        onSuccess: async (bloqueio) => {
          if (foto) {
            try {
              await uploadFoto.mutateAsync({ bloqueioId: bloqueio.id, arquivo: foto })
            } catch {
              toast.error("Bloqueio registrado, mas houve falha ao enviar a foto.")
            }
          }
          toast.success(`Peça ${peca.codigo} bloqueada no depósito da qualidade`)
          onOpenChange(false)
        },
        onError: (error) => toast.error(getApiError(error).detail),
      }
    )
  }

  const salvando = criarBloqueio.isPending || uploadFoto.isPending

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Novo bloqueio no depósito da qualidade</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Peça</Label>
            <PecaBuscaInput value={peca} onChange={setPeca} />
          </div>
          <div className="space-y-2">
            <Label>Motivo do bloqueio</Label>
            <Textarea
              placeholder="Ex.: peça entregue ao cliente X com diâmetro maior que o especificado."
              value={motivo}
              onChange={(e) => setMotivo(e.target.value)}
              rows={3}
            />
          </div>
          <div className="space-y-2">
            <Label>Característica de desenho a que se atentar (opcional)</Label>
            <Textarea
              placeholder="Ex.: diâmetro externo, posição 1 do desenho."
              value={caracteristicaAtencao}
              onChange={(e) => setCaracteristicaAtencao(e.target.value)}
              rows={2}
            />
          </div>
          <div className="space-y-2">
            <Label>Cliente (opcional)</Label>
            <Input value={cliente} onChange={(e) => setCliente(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label>Foto (opcional)</Label>
            <FotoUploadInput
              arquivos={foto ? [foto] : []}
              onChange={(arquivos) => setFoto(arquivos[arquivos.length - 1] ?? null)}
            />
          </div>
        </div>
        <DialogFooter>
          <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button type="button" disabled={!pronto || salvando} onClick={handleSubmit}>
            {salvando ? "Salvando..." : "Registrar bloqueio"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
