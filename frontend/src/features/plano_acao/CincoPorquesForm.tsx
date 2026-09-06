import { useEffect, useState } from "react"
import { Target } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useMarcarCausa5Porques, useUpsertCausa5Porques } from "@/features/plano_acao/api"
import { cn } from "@/lib/utils"
import type { PlanoDeAcaoDetalhe } from "@/types/api"

function NivelForm({
  planoId,
  nivel,
  perguntaInicial,
  respostaInicial,
  marcada,
  causaId,
  disabled,
}: {
  planoId: number
  nivel: number
  perguntaInicial: string
  respostaInicial: string
  marcada: boolean
  causaId: number | null
  disabled: boolean
}) {
  const [pergunta, setPergunta] = useState(perguntaInicial)
  const [resposta, setResposta] = useState(respostaInicial)
  const upsert = useUpsertCausa5Porques(planoId)
  const marcar = useMarcarCausa5Porques(planoId)

  useEffect(() => {
    setPergunta(perguntaInicial)
    setResposta(respostaInicial)
  }, [perguntaInicial, respostaInicial])

  return (
    <div className={cn("space-y-2 rounded-md border p-3", marcada && "border-primary bg-primary/5")}>
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold">Por quê ({nivel})?</span>
        {causaId !== null && (
          <button
            type="button"
            title="Marcar como causa raiz"
            disabled={disabled}
            onClick={() => marcar.mutate({ causaId, marcada: !marcada })}
            className={cn(
              "flex items-center gap-1 text-xs",
              marcada ? "text-primary" : "text-muted-foreground/50 hover:text-muted-foreground"
            )}
          >
            <Target className="size-3.5" />
            {marcada ? "Causa raiz" : "Marcar como causa raiz"}
          </button>
        )}
      </div>
      <div className="space-y-1.5">
        <Label className="text-xs">Pergunta</Label>
        <Input value={pergunta} onChange={(e) => setPergunta(e.target.value)} disabled={disabled} />
      </div>
      <div className="space-y-1.5">
        <Label className="text-xs">Resposta</Label>
        <Input value={resposta} onChange={(e) => setResposta(e.target.value)} disabled={disabled} />
      </div>
      {!disabled && (pergunta !== perguntaInicial || resposta !== respostaInicial) && (
        <Button
          size="sm"
          variant="outline"
          disabled={!pergunta.trim() || !resposta.trim() || upsert.isPending}
          onClick={() => upsert.mutate({ nivel, pergunta, resposta })}
        >
          Salvar nível {nivel}
        </Button>
      )}
    </div>
  )
}

export function CincoPorquesForm({ plano, disabled }: { plano: PlanoDeAcaoDetalhe; disabled: boolean }) {
  const causas = [...plano.causas_5porques].sort((a, b) => a.nivel - b.nivel)
  const proximoNivel = causas.length + 1
  const podeAdicionarProximo = !disabled && proximoNivel <= 5

  return (
    <div className="space-y-3">
      {causas.map((causa) => (
        <NivelForm
          key={causa.nivel}
          planoId={plano.id}
          nivel={causa.nivel}
          perguntaInicial={causa.pergunta}
          respostaInicial={causa.resposta}
          marcada={causa.marcada_como_raiz}
          causaId={causa.id}
          disabled={disabled}
        />
      ))}
      {podeAdicionarProximo && (
        <NivelForm
          key={`novo-${proximoNivel}`}
          planoId={plano.id}
          nivel={proximoNivel}
          perguntaInicial=""
          respostaInicial=""
          marcada={false}
          causaId={null}
          disabled={disabled}
        />
      )}
    </div>
  )
}
