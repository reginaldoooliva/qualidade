import { useState } from "react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"

export function ConcluirAcaoDialog({
  open,
  onOpenChange,
  onConfirmar,
  pendente,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  onConfirmar: (observacao: string) => void
  pendente: boolean
}) {
  const [observacao, setObservacao] = useState("")

  function handleConfirmar() {
    if (!observacao.trim()) return
    onConfirmar(observacao)
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(v) => {
        if (!v) setObservacao("")
        onOpenChange(v)
      }}
    >
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Concluir tratativa</DialogTitle>
        </DialogHeader>
        <div className="space-y-1.5">
          <Label>Observação / referência</Label>
          <Textarea
            autoFocus
            rows={3}
            placeholder="Ex.: baixa registrada na OP-1234"
            value={observacao}
            onChange={(e) => setObservacao(e.target.value)}
          />
        </div>
        <DialogFooter>
          <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button type="button" onClick={handleConfirmar} disabled={pendente || !observacao.trim()}>
            {pendente ? "Salvando..." : "Concluir"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
