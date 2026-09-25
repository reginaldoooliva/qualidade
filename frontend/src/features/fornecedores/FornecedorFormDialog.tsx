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
import { useCreateFornecedor, useUpdateFornecedor } from "@/features/fornecedores/api"
import { getApiError } from "@/lib/api-client"
import type { Fornecedor } from "@/types/api"

const schema = z.object({
  codigo: z.string().min(1, "Informe o código"),
  nome: z.string().min(1, "Informe o nome"),
  cnpj: z.string().optional(),
})

type FormValues = z.infer<typeof schema>

const VALORES_VAZIOS: FormValues = { codigo: "", nome: "", cnpj: "" }

export function FornecedorFormDialog({
  open,
  onOpenChange,
  fornecedor,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  fornecedor?: Fornecedor
}) {
  const isEdicao = !!fornecedor
  const createFornecedor = useCreateFornecedor()
  const updateFornecedor = useUpdateFornecedor(fornecedor?.id ?? 0)
  const mutation = isEdicao ? updateFornecedor : createFornecedor

  const form = useForm<FormValues>({ resolver: zodResolver(schema), defaultValues: VALORES_VAZIOS })

  useEffect(() => {
    if (open) {
      form.reset(
        fornecedor
          ? { codigo: fornecedor.codigo, nome: fornecedor.nome, cnpj: fornecedor.cnpj ?? "" }
          : VALORES_VAZIOS
      )
    }
  }, [open, fornecedor, form])

  function onSubmit(values: FormValues) {
    mutation.mutate(values, {
      onSuccess: () => {
        toast.success(isEdicao ? "Fornecedor atualizado" : "Fornecedor cadastrado")
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
          <DialogTitle>{isEdicao ? "Editar fornecedor" : "Novo fornecedor"}</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
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
                name="cnpj"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>CNPJ</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <FormField
              control={form.control}
              name="nome"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nome</FormLabel>
                  <FormControl>
                    <Input {...field} />
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
