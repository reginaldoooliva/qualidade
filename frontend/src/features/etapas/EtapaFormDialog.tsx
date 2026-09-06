import { zodResolver } from "@hookform/resolvers/zod"
import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { useCreateEtapa, useUpdateEtapa } from "@/features/etapas/api"
import { getApiError } from "@/lib/api-client"
import type { Etapa } from "@/types/api"

const schema = z.object({
  numero_etapa: z.coerce.number().int().min(1, "Informe o número da etapa"),
  descricao: z.string().optional(),
  freq_numerador: z.coerce.number().int().min(1, "Mínimo 1"),
  freq_denominador: z.coerce.number().int().min(1, "Mínimo 1"),
})

type FormValues = z.infer<typeof schema>

const VALORES_VAZIOS: FormValues = {
  numero_etapa: 10,
  descricao: "",
  freq_numerador: 1,
  freq_denominador: 1,
}

export function EtapaFormDialog({
  open,
  onOpenChange,
  pecaId,
  etapa,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  pecaId: number
  etapa?: Etapa
}) {
  const isEdicao = !!etapa
  const createEtapa = useCreateEtapa(pecaId)
  const updateEtapa = useUpdateEtapa(etapa?.id ?? 0, pecaId)
  const mutation = isEdicao ? updateEtapa : createEtapa

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: VALORES_VAZIOS,
  })

  useEffect(() => {
    if (open) {
      form.reset(
        etapa
          ? {
              numero_etapa: etapa.numero_etapa,
              descricao: etapa.descricao ?? "",
              freq_numerador: etapa.freq_numerador,
              freq_denominador: etapa.freq_denominador,
            }
          : VALORES_VAZIOS
      )
    }
  }, [open, etapa, form])

  function onSubmit(values: FormValues) {
    mutation.mutate(values, {
      onSuccess: () => {
        toast.success(isEdicao ? "Etapa atualizada" : "Etapa cadastrada")
        onOpenChange(false)
      },
      onError: (error) => {
        const apiError = getApiError(error)
        if (apiError.code === "ETAPA_NUMERO_DUPLICADO") {
          form.setError("numero_etapa", { message: apiError.detail })
        } else {
          toast.error(apiError.detail)
        }
      },
    })
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{isEdicao ? "Editar etapa" : "Nova etapa"}</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="numero_etapa"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nº da etapa</FormLabel>
                  <FormControl>
                    <Input type="number" autoFocus {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="descricao"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Descrição</FormLabel>
                  <FormControl>
                    <Input placeholder="Ex: Torneamento" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="freq_numerador"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Frequência — numerador</FormLabel>
                    <FormControl>
                      <Input type="number" min={1} {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="freq_denominador"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Frequência — denominador</FormLabel>
                    <FormControl>
                      <Input type="number" min={1} {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <FormDescription>
              Ex: 1/10 mede 1 peça a cada 10 produzidas nesta etapa — usado para calcular
              automaticamente a quantidade de amostras da coleta.
            </FormDescription>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancelar
              </Button>
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending ? "Salvando..." : "Salvar"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
