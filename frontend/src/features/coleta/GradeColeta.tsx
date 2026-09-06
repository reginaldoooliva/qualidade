import { useEffect, useMemo, useRef, useState } from "react"

import { useExcluirMedicao, useSalvarMedicao } from "@/features/coleta/api"
import { cn } from "@/lib/utils"
import type { Caracteristica, RodadaColetaDetalhe } from "@/types/api"

function cellKey(caracteristicaId: number, amostraNumero: number) {
  return `${caracteristicaId}-${amostraNumero}`
}

function foraDeEspecificacao(caracteristica: Caracteristica, valorTexto: string): boolean {
  if (valorTexto.trim() === "") return false
  const valor = Number(valorTexto)
  if (Number.isNaN(valor)) return false
  return valor < caracteristica.lie || valor > caracteristica.lse
}

export function GradeColeta({
  rodada,
  somenteLeitura,
}: {
  rodada: RodadaColetaDetalhe
  somenteLeitura?: boolean
}) {
  const caracteristicas = rodada.caracteristicas
  const amostras = useMemo(
    () => Array.from({ length: rodada.amostras_alvo }, (_, i) => i + 1),
    [rodada.amostras_alvo]
  )

  const [valores, setValores] = useState<Record<string, string>>({})
  const savedRef = useRef<Record<string, string>>({})
  const inputRefs = useRef<Map<string, HTMLInputElement>>(new Map())

  useEffect(() => {
    const iniciais: Record<string, string> = {}
    for (const medicao of rodada.medicoes) {
      iniciais[cellKey(medicao.caracteristica_id, medicao.amostra_numero)] = String(medicao.valor)
    }
    setValores(iniciais)
    savedRef.current = { ...iniciais }
  }, [rodada.id]) // eslint-disable-line react-hooks/exhaustive-deps

  const salvarMedicao = useSalvarMedicao(rodada.id)
  const excluirMedicao = useExcluirMedicao(rodada.id)

  function handleChange(caracteristicaId: number, amostraNumero: number, valor: string) {
    setValores((prev) => ({ ...prev, [cellKey(caracteristicaId, amostraNumero)]: valor }))
  }

  function handleBlur(caracteristicaId: number, amostraNumero: number) {
    if (somenteLeitura) return
    const key = cellKey(caracteristicaId, amostraNumero)
    const valorAtual = (valores[key] ?? "").trim()
    const valorSalvo = savedRef.current[key]

    if (valorAtual === (valorSalvo ?? "")) return

    if (valorAtual === "") {
      if (valorSalvo !== undefined) {
        excluirMedicao.mutate(
          { caracteristicaId, amostraNumero },
          {
            onSuccess: () => {
              delete savedRef.current[key]
            },
          }
        )
      }
      return
    }

    const numero = Number(valorAtual)
    if (Number.isNaN(numero)) return

    salvarMedicao.mutate(
      { caracteristicaId, amostraNumero, valor: numero },
      {
        onSuccess: () => {
          savedRef.current[key] = valorAtual
        },
      }
    )
  }

  function focusCell(caracteristicaId: number, amostraNumero: number) {
    const el = inputRefs.current.get(cellKey(caracteristicaId, amostraNumero))
    el?.focus()
    el?.select()
  }

  function handleKeyDown(
    e: React.KeyboardEvent<HTMLInputElement>,
    caracteristicaId: number,
    amostraNumero: number
  ) {
    if (e.key === "Enter") {
      e.preventDefault()
      const proximaAmostra = amostraNumero + 1
      if (proximaAmostra <= rodada.amostras_alvo) {
        focusCell(caracteristicaId, proximaAmostra)
      } else {
        ;(e.target as HTMLInputElement).blur()
      }
    }
  }

  return (
    <div className="overflow-auto rounded-md border bg-background">
      <table className="w-full min-w-max border-collapse text-sm">
        <thead className="sticky top-0 z-10 bg-muted/60 backdrop-blur">
          <tr>
            <th className="border-b px-3 py-2 text-left font-medium text-muted-foreground">Amostra</th>
            {caracteristicas.map((c) => (
              <th key={c.id} className="border-b px-3 py-2 text-left font-medium text-muted-foreground">
                {c.nome}
                <div className="text-xs font-normal text-muted-foreground/70">
                  {c.lie.toFixed(c.casas_decimais)} – {c.lse.toFixed(c.casas_decimais)} {c.unidade}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {amostras.map((amostraNumero) => (
            <tr key={amostraNumero} className="odd:bg-muted/10">
              <td className="border-b px-3 py-1.5 font-medium text-muted-foreground">{amostraNumero}</td>
              {caracteristicas.map((c) => {
                const key = cellKey(c.id, amostraNumero)
                const valor = valores[key] ?? ""
                const fora = foraDeEspecificacao(c, valor)
                return (
                  <td key={c.id} className="border-b px-1.5 py-1">
                    <input
                      ref={(el) => {
                        if (el) inputRefs.current.set(key, el)
                        else inputRefs.current.delete(key)
                      }}
                      type="number"
                      inputMode="decimal"
                      enterKeyHint="next"
                      step="any"
                      disabled={somenteLeitura}
                      value={valor}
                      onChange={(e) => handleChange(c.id, amostraNumero, e.target.value)}
                      onBlur={() => handleBlur(c.id, amostraNumero)}
                      onKeyDown={(e) => handleKeyDown(e, c.id, amostraNumero)}
                      className={cn(
                        "h-10 w-28 rounded-md border px-2 text-right text-sm outline-none transition-colors",
                        "focus:ring-2 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-60",
                        fora
                          ? "border-destructive bg-destructive/10 text-destructive"
                          : "border-input bg-transparent"
                      )}
                    />
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
