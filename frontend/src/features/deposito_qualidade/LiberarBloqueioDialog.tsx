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
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { useLiberarBloqueio } from "@/features/deposito_qualidade/api"
import { getApiError } from "@/lib/api-client"
import type { BloqueioDeposito } from "@/types/api"

export function LiberarBloqueioDialog({
  open,
  onOpenChange,
  bloqueio,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  bloqueio: BloqueioDeposito | null
}) {
  const [observacao, setObservacao] = useState("")
  const liberarBloqueio = useLiberarBloqueio()

  useEffect(() => {
    if (open) setObservacao("")
  }, [open])

  function handleSubmit() {
    if (!bloqueio || observacao.trim() === "") return
    liberarBloqueio.mutate(
      { bloqueioId: bloqueio.id, observacao_liberacao: observacao },
      {
        onSuccess: () => {
          toast.success(`Peça ${bloqueio.peca.codigo} liberada do depósito da qualidade`)
          onOpenChange(false)
        },
        onError: (error) => toast.error(getApiError(error).detail),
      }
    )
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Liberar bloqueio</DialogTitle>
        </DialogHeader>
        <div className="space-y-2">
          <Label>Observação da liberação</Label>
          <Textarea
            placeholder="Ex.: retrabalho concluído, peça conforme desenho."
            value={observacao}
            onChange={(e) => setObservacao(e.target.value)}
            rows={3}
            autoFocus
          />
        </div>
        <DialogFooter>
          <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button
            type="button"
            disabled={observacao.trim() === "" || liberarBloqueio.isPending}
            onClick={handleSubmit}
          >
            {liberarBloqueio.isPending ? "Liberando..." : "Liberar"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
