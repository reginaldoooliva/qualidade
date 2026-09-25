import { zodResolver } from "@hookform/resolvers/zod"
import { useEffect } from "react"
import { useForm, useWatch } from "react-hook-form"
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  useCreateCaracteristica,
  useUpdateCaracteristica,
} from "@/features/caracteristicas/api"
import { useTiposInstrumento } from "@/features/tipos_instrumento/api"
import { getApiError } from "@/lib/api-client"
import type { Caracteristica } from "@/types/api"

const UNIDADE_LABEL: Record<string, string> = {
  mm: "mm",
  cm: "cm",
  polegada: "polegada",
}

const schema = z
  .object({
    nome: z.string().min(1, "Informe o nome da característica"),
    posicao_desenho: z.string().optional(),
    nominal: z.coerce.number(),
    tol_superior: z.coerce.number().min(0, "Não pode ser negativa"),
    tol_inferior: z.coerce.number().min(0, "Não pode ser negativa"),
    unidade: z.enum(["mm", "cm", "polegada"]),
    tipo_instrumento_id: z.coerce.number().optional(),
    casas_decimais: z.coerce.number().int().min(0).max(6),
  })
  .refine((v) => v.tol_superior > 0 || v.tol_inferior > 0, {
    message: "Informe ao menos uma tolerância (superior ou inferior)",
    path: ["tol_superior"],
  })

type FormValues = z.infer<typeof schema>

const VALORES_VAZIOS: FormValues = {
  nome: "",
  posicao_desenho: "",
  nominal: 0,
  tol_superior: 0,
  tol_inferior: 0,
  unidade: "mm",
  tipo_instrumento_id: undefined,
  casas_decimais: 3,
}

export function CaracteristicaFormDialog({
  open,
  onOpenChange,
  etapaId,
  caracteristica,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  etapaId: number
  caracteristica?: Caracteristica
}) {
  const isEdicao = !!caracteristica
  const createCaracteristica = useCreateCaracteristica(etapaId)
  const updateCaracteristica = useUpdateCaracteristica(caracteristica?.id ?? 0, etapaId)
  const mutation = isEdicao ? updateCaracteristica : createCaracteristica
  const { data: tiposInstrumento } = useTiposInstrumento({ status: "ativo" })

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: VALORES_VAZIOS,
  })

  useEffect(() => {
    if (open) {
      form.reset(
        caracteristica
          ? {
              nome: caracteristica.nome,
              posicao_desenho: caracteristica.posicao_desenho ?? "",
              nominal: caracteristica.nominal,
              tol_superior: caracteristica.tol_superior,
              tol_inferior: caracteristica.tol_inferior,
              unidade: caracteristica.unidade,
              tipo_instrumento_id: caracteristica.tipo_instrumento_id ?? undefined,
              casas_decimais: caracteristica.casas_decimais,
            }
          : VALORES_VAZIOS
      )
    }
  }, [open, caracteristica, form])

  const nominal = useWatch({ control: form.control, name: "nominal" })
  const tolSuperior = useWatch({ control: form.control, name: "tol_superior" })
  const tolInferior = useWatch({ control: form.control, name: "tol_inferior" })
  const casasDecimais = useWatch({ control: form.control, name: "casas_decimais" }) ?? 3

  const lse = (Number(nominal) || 0) + (Number(tolSuperior) || 0)
  const lie = (Number(nominal) || 0) - (Number(tolInferior) || 0)
  const toleranciaValida = lse > lie

  function onSubmit(values: FormValues) {
    mutation.mutate(values, {
      onSuccess: () => {
        toast.success(isEdicao ? "Característica atualizada" : "Característica cadastrada")
        onOpenChange(false)
      },
      onError: (error) => {
        toast.error(getApiError(error).detail)
      },
    })
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{isEdicao ? "Editar característica" : "Nova característica"}</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <FormField
                control={form.control}
                name="nome"
                render={({ field }) => (
                  <FormItem className="col-span-2">
                    <FormLabel>Nome da característica</FormLabel>
                    <FormControl>
                      <Input autoFocus placeholder="Ex: Diâmetro externo" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="posicao_desenho"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Item no desenho</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <FormField
                control={form.control}
                name="nominal"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Nominal</FormLabel>
                    <FormControl>
                      <Input type="number" step="any" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="tol_superior"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Tolerância (+)</FormLabel>
                    <FormControl>
                      <Input type="number" step="any" min={0} {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="tol_inferior"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Tolerância (−)</FormLabel>
                    <FormControl>
                      <Input type="number" step="any" min={0} {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div
              className={
                "flex items-center justify-between rounded-md border px-3 py-2 text-sm " +
                (toleranciaValida
                  ? "border-border bg-muted/50"
                  : "border-destructive/50 bg-destructive/10 text-destructive")
              }
            >
              <span>
                LIE calculado: <strong>{lie.toFixed(casasDecimais)}</strong>
              </span>
              <span>
                LSE calculado: <strong>{lse.toFixed(casasDecimais)}</strong>
              </span>
            </div>
            {!toleranciaValida && (
              <p className="text-sm text-destructive">
                O LSE deve ser maior que o LIE — revise as tolerâncias.
              </p>
            )}

            <div className="grid grid-cols-3 gap-4">
              <FormField
                control={form.control}
                name="unidade"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Unidade</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value} items={UNIDADE_LABEL}>
                      <FormControl>
                        <SelectTrigger className="w-full">
                          <SelectValue />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="mm">mm</SelectItem>
                        <SelectItem value="cm">cm</SelectItem>
                        <SelectItem value="polegada">polegada</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="tipo_instrumento_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Instrumento</FormLabel>
                    <Select
                      onValueChange={(value) => field.onChange(Number(value))}
                      value={field.value !== undefined ? String(field.value) : undefined}
                      items={Object.fromEntries(
                        (tiposInstrumento ?? []).map((tipo) => [String(tipo.id), tipo.nome])
                      )}
                    >
                      <FormControl>
                        <SelectTrigger className="w-full">
                          <SelectValue placeholder="Selecione" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {tiposInstrumento?.map((tipo) => (
                          <SelectItem key={tipo.id} value={String(tipo.id)}>
                            {tipo.nome}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="casas_decimais"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Casas decimais</FormLabel>
                    <FormControl>
                      <Input type="number" min={0} max={6} {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancelar
              </Button>
              <Button type="submit" disabled={mutation.isPending || !toleranciaValida}>
                {mutation.isPending ? "Salvando..." : "Salvar"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
