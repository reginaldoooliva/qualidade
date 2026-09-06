import { zodResolver } from "@hookform/resolvers/zod"
import { useForm, useWatch } from "react-hook-form"
import { toast } from "sonner"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useFinalizarColeta } from "@/features/coleta/api"
import { getApiError } from "@/lib/api-client"
import type { RodadaColetaDetalhe } from "@/types/api"

export const MOTIVO_LABEL: Record<string, string> = {
  ordem_interrompida: "Ordem interrompida",
  ordem_cancelada: "Ordem cancelada",
  quantidade_menor_que_previsto: "Quantidade produzida menor que o previsto",
  nao_conformidade_processo: "Não conformidade identificada no processo",
  outro: "Outro",
}

const schema = z.object({
  motivo_encerramento_antecipado: z
    .enum([
      "ordem_interrompida",
      "ordem_cancelada",
      "quantidade_menor_que_previsto",
      "nao_conformidade_processo",
      "outro",
    ])
    .optional(),
  motivo_detalhe: z.string().optional(),
})

type FormValues = z.infer<typeof schema>

export function contarAmostrasCompletas(rodada: RodadaColetaDetalhe): number {
  const porAmostra = new Map<number, number>()
  for (const m of rodada.medicoes) {
    porAmostra.set(m.amostra_numero, (porAmostra.get(m.amostra_numero) ?? 0) + 1)
  }
  const totalCaracteristicas = rodada.caracteristicas.length
  let completas = 0
  for (const contagem of porAmostra.values()) {
    if (contagem >= totalCaracteristicas) completas += 1
  }
  return completas
}

export function FinalizarColetaDialog({
  open,
  onOpenChange,
  rodada,
  onFinalizado,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  rodada: RodadaColetaDetalhe
  onFinalizado?: (sugestaoAbrirRnc: boolean) => void
}) {
  const finalizar = useFinalizarColeta(rodada.id)
  const amostrasCompletas = contarAmostrasCompletas(rodada)
  const incompleta = amostrasCompletas < rodada.amostras_alvo

  const form = useForm<FormValues>({ resolver: zodResolver(schema), defaultValues: {} })
  const motivo = useWatch({ control: form.control, name: "motivo_encerramento_antecipado" })

  function onSubmit(values: FormValues) {
    finalizar.mutate(values, {
      onSuccess: (data) => {
        toast.success(
          data.status === "finalizada" ? "Coleta finalizada com sucesso" : "Coleta finalizada com pendência"
        )
        onOpenChange(false)
        onFinalizado?.(data.sugestao_abrir_rnc)
      },
      onError: (error) => toast.error(getApiError(error).detail),
    })
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Finalizar coleta</DialogTitle>
          <DialogDescription>
            {incompleta
              ? `Faltam ${rodada.amostras_alvo - amostrasCompletas} de ${rodada.amostras_alvo} amostra(s). Informe o motivo do encerramento antecipado.`
              : `Todas as ${rodada.amostras_alvo} amostras foram medidas.`}
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            {incompleta && (
              <>
                <FormField
                  control={form.control}
                  name="motivo_encerramento_antecipado"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Motivo do encerramento antecipado</FormLabel>
                      <Select onValueChange={field.onChange} value={field.value} items={MOTIVO_LABEL}>
                        <FormControl>
                          <SelectTrigger className="w-full">
                            <SelectValue placeholder="Selecione" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {Object.entries(MOTIVO_LABEL).map(([value, label]) => (
                            <SelectItem key={value} value={value}>
                              {label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                {motivo === "outro" && (
                  <FormField
                    control={form.control}
                    name="motivo_detalhe"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Descreva o motivo</FormLabel>
                        <FormControl>
                          <Input {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                )}
              </>
            )}
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancelar
              </Button>
              <Button type="submit" disabled={finalizar.isPending || (incompleta && !motivo)}>
                {finalizar.isPending ? "Finalizando..." : "Finalizar"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
