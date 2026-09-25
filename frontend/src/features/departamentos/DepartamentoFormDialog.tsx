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
import { useCreateDepartamento, useUpdateDepartamento } from "@/features/departamentos/api"
import { getApiError } from "@/lib/api-client"
import type { Departamento } from "@/types/api"

const schema = z.object({
  nome: z.string().min(1, "Informe o nome"),
})

type FormValues = z.infer<typeof schema>

const VALORES_VAZIOS: FormValues = { nome: "" }

export function DepartamentoFormDialog({
  open,
  onOpenChange,
  departamento,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  departamento?: Departamento
}) {
  const isEdicao = !!departamento
  const createDepartamento = useCreateDepartamento()
  const updateDepartamento = useUpdateDepartamento(departamento?.id ?? 0)
  const mutation = isEdicao ? updateDepartamento : createDepartamento

  const form = useForm<FormValues>({ resolver: zodResolver(schema), defaultValues: VALORES_VAZIOS })

  useEffect(() => {
    if (open) {
      form.reset(departamento ? { nome: departamento.nome } : VALORES_VAZIOS)
    }
  }, [open, departamento, form])

  function onSubmit(values: FormValues) {
    mutation.mutate(values, {
      onSuccess: () => {
        toast.success(isEdicao ? "Departamento atualizado" : "Departamento cadastrado")
        onOpenChange(false)
      },
      onError: (error) => {
        const apiError = getApiError(error)
        if (apiError.code === "NOME_DUPLICADO") {
          form.setError("nome", { message: apiError.detail })
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
          <DialogTitle>{isEdicao ? "Editar departamento" : "Novo departamento"}</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="nome"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nome</FormLabel>
                  <FormControl>
                    <Input autoFocus placeholder="Engenharia" {...field} />
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
