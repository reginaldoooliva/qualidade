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
import { useCreatePeca, useUpdatePeca } from "@/features/pecas/api"
import { getApiError } from "@/lib/api-client"
import type { Peca } from "@/types/api"

const schema = z.object({
  codigo: z.string().min(1, "Informe o código"),
  descricao: z.string().min(1, "Informe a descrição"),
  cliente: z.string().optional(),
  desenho: z.string().optional(),
  revisao: z.string().min(1, "Informe a revisão"),
  material: z.string().optional(),
  observacoes: z.string().optional(),
})

type FormValues = z.infer<typeof schema>

const VALORES_VAZIOS: FormValues = {
  codigo: "",
  descricao: "",
  cliente: "",
  desenho: "",
  revisao: "",
  material: "",
  observacoes: "",
}

export function PecaFormDialog({
  open,
  onOpenChange,
  peca,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  peca?: Peca
}) {
  const isEdicao = !!peca
  const createPeca = useCreatePeca()
  const updatePeca = useUpdatePeca(peca?.id ?? 0)
  const mutation = isEdicao ? updatePeca : createPeca

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: VALORES_VAZIOS,
  })

  useEffect(() => {
    if (open) {
      form.reset(
        peca
          ? {
              codigo: peca.codigo,
              descricao: peca.descricao,
              cliente: peca.cliente ?? "",
              desenho: peca.desenho ?? "",
              revisao: peca.revisao,
              material: peca.material ?? "",
              observacoes: peca.observacoes ?? "",
            }
          : VALORES_VAZIOS
      )
    }
  }, [open, peca, form])

  function onSubmit(values: FormValues) {
    mutation.mutate(values, {
      onSuccess: () => {
        toast.success(isEdicao ? "Peça atualizada" : "Peça cadastrada")
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
          <DialogTitle>{isEdicao ? "Editar peça" : "Nova peça"}</DialogTitle>
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
                name="revisao"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Revisão do desenho</FormLabel>
                    <FormControl>
                      <Input placeholder="Rev. A" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <FormField
              control={form.control}
              name="descricao"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Descrição</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="cliente"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Cliente</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="material"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Material</FormLabel>
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
              name="desenho"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Desenho</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="observacoes"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Observações</FormLabel>
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
