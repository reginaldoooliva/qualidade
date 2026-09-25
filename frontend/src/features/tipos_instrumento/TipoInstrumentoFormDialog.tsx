import { zodResolver } from "@hookform/resolvers/zod"
import { useEffect, useState } from "react"
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
import { FotoAutenticada } from "@/components/FotoAutenticada"
import { FotoUploadInput } from "@/components/FotoUploadInput"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  useCreateTipoInstrumento,
  useUpdateTipoInstrumento,
  useUploadImagemTipoInstrumento,
} from "@/features/tipos_instrumento/api"
import { getApiError } from "@/lib/api-client"
import type { TipoInstrumento } from "@/types/api"

const schema = z.object({
  nome: z.string().min(1, "Informe o nome do instrumento"),
  descricao_funcao: z.string().optional(),
})

type FormValues = z.infer<typeof schema>

const VALORES_VAZIOS: FormValues = { nome: "", descricao_funcao: "" }

export function TipoInstrumentoFormDialog({
  open,
  onOpenChange,
  tipo,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  tipo?: TipoInstrumento
}) {
  const isEdicao = !!tipo
  const createTipo = useCreateTipoInstrumento()
  const updateTipo = useUpdateTipoInstrumento(tipo?.id ?? 0)
  const uploadImagem = useUploadImagemTipoInstrumento()
  const mutation = isEdicao ? updateTipo : createTipo

  const [foto, setFoto] = useState<File | null>(null)

  const form = useForm<FormValues>({ resolver: zodResolver(schema), defaultValues: VALORES_VAZIOS })

  useEffect(() => {
    if (open) {
      form.reset(
        tipo ? { nome: tipo.nome, descricao_funcao: tipo.descricao_funcao ?? "" } : VALORES_VAZIOS
      )
      setFoto(null)
    }
  }, [open, tipo, form])

  function onSubmit(values: FormValues) {
    mutation.mutate(values, {
      onSuccess: async (resultado) => {
        if (foto) {
          try {
            await uploadImagem.mutateAsync({ tipoId: resultado.id, arquivo: foto })
          } catch {
            toast.error("Tipo de instrumento salvo, mas houve falha ao enviar a imagem.")
          }
        }
        toast.success(isEdicao ? "Tipo de instrumento atualizado" : "Tipo de instrumento cadastrado")
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

  const salvando = mutation.isPending || uploadImagem.isPending

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{isEdicao ? "Editar tipo de instrumento" : "Novo tipo de instrumento"}</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="nome"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Instrumento</FormLabel>
                  <FormControl>
                    <Input autoFocus placeholder="Ex: Micrômetro de canal" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="descricao_funcao"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Descrição da função do instrumento</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Ex: usado para medir o diâmetro do canal interno."
                      rows={3}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="space-y-2">
              <Label>Imagem (opcional)</Label>
              {isEdicao && tipo.tem_imagem && !foto && (
                <FotoAutenticada
                  url={`/tipos-instrumento/${tipo.id}/imagem`}
                  alt={tipo.nome}
                  className="size-20 rounded-md border object-cover"
                />
              )}
              <FotoUploadInput
                arquivos={foto ? [foto] : []}
                onChange={(arquivos) => setFoto(arquivos[arquivos.length - 1] ?? null)}
              />
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancelar
              </Button>
              <Button type="submit" disabled={salvando}>
                {salvando ? "Salvando..." : "Salvar"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
