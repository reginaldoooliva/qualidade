import { useState } from "react"
import { Plus, Target, Trash2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  useAdicionarCausaIshikawa,
  useMarcarCausaIshikawa,
  useRemoverCausaIshikawa,
} from "@/features/plano_acao/api"
import { cn } from "@/lib/utils"
import type { CategoriaIshikawa, PlanoDeAcaoDetalhe } from "@/types/api"

const CATEGORIAS: { valor: CategoriaIshikawa; label: string }[] = [
  { valor: "metodo", label: "Método" },
  { valor: "mao_de_obra", label: "Mão de obra" },
  { valor: "maquina", label: "Máquina" },
  { valor: "material", label: "Material" },
  { valor: "meio_ambiente", label: "Meio Ambiente" },
  { valor: "medicao", label: "Medição" },
]

function Coluna({
  planoId,
  categoria,
  label,
  causas,
  disabled,
}: {
  planoId: number
  categoria: CategoriaIshikawa
  label: string
  causas: PlanoDeAcaoDetalhe["causas_ishikawa"]
  disabled: boolean
}) {
  const [novaCausa, setNovaCausa] = useState("")
  const adicionar = useAdicionarCausaIshikawa(planoId)
  const marcar = useMarcarCausaIshikawa(planoId)
  const remover = useRemoverCausaIshikawa(planoId)

  function handleAdicionar() {
    if (!novaCausa.trim()) return
    adicionar.mutate(
      { categoria, descricao_causa: novaCausa.trim() },
      { onSuccess: () => setNovaCausa("") }
    )
  }

  return (
    <div className="space-y-2 rounded-md border p-3">
      <div className="text-sm font-semibold">{label}</div>
      <ul className="space-y-1.5">
        {causas.map((causa) => (
          <li
            key={causa.id}
            className={cn(
              "flex items-start gap-2 rounded-md border px-2 py-1.5 text-sm",
              causa.marcada_como_raiz && "border-primary bg-primary/5"
            )}
          >
            <button
              type="button"
              title="Marcar como causa raiz"
              disabled={disabled}
              onClick={() => marcar.mutate({ causaId: causa.id, marcada: !causa.marcada_como_raiz })}
              className={cn(
                "mt-0.5 shrink-0",
                causa.marcada_como_raiz ? "text-primary" : "text-muted-foreground/40 hover:text-muted-foreground"
              )}
            >
              <Target className="size-4" />
            </button>
            <span className="flex-1">{causa.descricao_causa}</span>
            {!disabled && (
              <button
                type="button"
                onClick={() => remover.mutate(causa.id)}
                className="shrink-0 text-muted-foreground/50 hover:text-destructive"
              >
                <Trash2 className="size-3.5" />
              </button>
            )}
          </li>
        ))}
        {causas.length === 0 && <li className="text-xs text-muted-foreground">Nenhuma causa listada.</li>}
      </ul>
      {!disabled && (
        <div className="flex gap-1.5">
          <Input
            value={novaCausa}
            onChange={(e) => setNovaCausa(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault()
                handleAdicionar()
              }
            }}
            placeholder="+ adicionar causa"
            className="h-8 text-sm"
          />
          <Button size="icon" className="size-8 shrink-0" onClick={handleAdicionar} disabled={!novaCausa.trim()}>
            <Plus className="size-4" />
          </Button>
        </div>
      )}
    </div>
  )
}

export function IshikawaBoard({ plano, disabled }: { plano: PlanoDeAcaoDetalhe; disabled: boolean }) {
  return (
    <div className="space-y-2">
      <p className="text-xs text-muted-foreground">
        Marque com <Target className="inline size-3" /> a(s) causa(s) identificada(s) como raiz real do problema.
      </p>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {CATEGORIAS.map(({ valor, label }) => (
          <Coluna
            key={valor}
            planoId={plano.id}
            categoria={valor}
            label={label}
            causas={plano.causas_ishikawa.filter((c) => c.categoria === valor)}
            disabled={disabled}
          />
        ))}
      </div>
    </div>
  )
}
