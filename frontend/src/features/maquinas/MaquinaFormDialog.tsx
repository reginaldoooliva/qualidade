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
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { useCreateMaquina, useUpdateMaquina } from "@/features/maquinas/api"
import { getApiError } from "@/lib/api-client"
import type { Maquina } from "@/types/api"

const schema = z.object({
  codigo: z.string().min(1, "Informe o código"),
  descricao: z.string().min(1, "Informe a descrição"),
})

type FormValues = z.infer<typeof schema>

const VALORES_VAZIOS: FormValues = { codigo: "", descricao: "" }

export function MaquinaFormDialog({
  open,
  onOpenChange,
  maquina,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  maquina?: Maquina
}) {
  const isEdicao = !!maquina
  const createMaquina = useCreateMaquina()
  const updateMaquina = useUpdateMaquina(maquina?.id ?? 0)
  const mutation = isEdicao ? updateMaquina : createMaquina

  const form = useForm<FormValues>({ resolver: zodResolver(schema), defaultValues: VALORES_VAZIOS })

  useEffect(() => {
    if (open) {
      form.reset(maquina ? { codigo: maquina.codigo, descricao: maquina.descricao } : VALORES_VAZIOS)
    }
  }, [open, maquina, form])

  function onSubmit(values: FormValues) {
    mutation.mutate(values, {
      onSuccess: () => {
        toast.success(isEdicao ? "Máquina atualizada" : "Máquina cadastrada")
        onOpenChange(false)
      },
      onError: (error) => {
        const apiError = getApiError(error)
        if (apiError.code === "CODIGO_DUPLICADO") {
          form.setError("codigo", { message: apiError.detail })
        } else {
          toast.error(apiError.detail)
        }
      },
    })
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{isEdicao ? "Editar máquina" : "Nova máquina"}</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="codigo"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Código</FormLabel>
                  <FormControl>
                    <Input autoFocus {...field} />
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
                    <Input placeholder="Torno CNC 1" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
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
