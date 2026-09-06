import { useMemo } from "react"
import {
  Bar,
  CartesianGrid,
  ComposedChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

import { CHART_COLORS } from "@/features/analise/chartColors"

interface Bin {
  centro: number
  contagem: number
  faixaLabel: string
}

function construirBins(valores: number[], lie: number, lse: number, casasDecimais: number, numBins = 10): Bin[] {
  const min = Math.min(...valores, lie)
  const max = Math.max(...valores, lse)
  const largura = (max - min) / numBins || 1

  const bins = Array.from({ length: numBins }, (_, i) => {
    const inicio = min + i * largura
    const fim = inicio + largura
    return { inicio, fim, centro: (inicio + fim) / 2, contagem: 0 }
  })

  for (const valor of valores) {
    let idx = Math.floor((valor - min) / largura)
    if (idx >= numBins) idx = numBins - 1
    if (idx < 0) idx = 0
    bins[idx].contagem += 1
  }

  return bins.map((b) => ({
    centro: b.centro,
    contagem: b.contagem,
    faixaLabel: `${b.inicio.toFixed(casasDecimais)} – ${b.fim.toFixed(casasDecimais)}`,
  }))
}

function TooltipHistograma({ active, payload }: { active?: boolean; payload?: { payload: Bin }[] }) {
  if (!active || !payload?.length) return null
  const bin = payload[0].payload
  return (
    <div className="rounded-md border bg-popover px-3 py-2 text-xs shadow-md">
      <div className="text-muted-foreground">Faixa {bin.faixaLabel}</div>
      <div className="font-medium text-popover-foreground">{bin.contagem} amostra(s)</div>
    </div>
  )
}

export function HistogramaChart({
  valores,
  lie,
  lse,
  nominal,
  casasDecimais,
  unidade,
}: {
  valores: number[]
  lie: number
  lse: number
  nominal: number
  casasDecimais: number
  unidade: string
}) {
  const bins = useMemo(
    () => construirBins(valores, lie, lse, casasDecimais),
    [valores, lie, lse, casasDecimais]
  )

  if (valores.length < 2) {
    return (
      <div className="flex h-48 items-center justify-center text-sm text-muted-foreground">
        Amostras insuficientes para histograma (mínimo 2).
      </div>
    )
  }

  const min = Math.min(...valores, lie)
  const max = Math.max(...valores, lse)
  const margem = (max - min) * 0.05 || 1

  return (
    <ResponsiveContainer width="100%" height={220}>
      <ComposedChart data={bins} margin={{ top: 16, right: 16, bottom: 8, left: 8 }}>
        <CartesianGrid vertical={false} stroke={CHART_COLORS.grid} />
        <XAxis
          type="number"
          dataKey="centro"
          domain={[min - margem, max + margem]}
          tickFormatter={(v: number) => v.toFixed(casasDecimais)}
          stroke="var(--muted-foreground)"
          fontSize={11}
          label={{ value: unidade, position: "insideBottom", offset: -4, fontSize: 11, fill: "var(--muted-foreground)" }}
        />
        <YAxis allowDecimals={false} stroke="var(--muted-foreground)" fontSize={11} width={28} />
        <Tooltip content={<TooltipHistograma />} cursor={{ fill: "var(--muted)", opacity: 0.4 }} />
        <Bar dataKey="contagem" fill={CHART_COLORS.bar} radius={[4, 4, 0, 0]} barSize={22} isAnimationActive={false} />
        <ReferenceLine
          x={lie}
          stroke={CHART_COLORS.limite}
          strokeDasharray="4 4"
          strokeWidth={1.5}
          label={{ value: "LIE", position: "top", fontSize: 11, fill: CHART_COLORS.limite }}
        />
        <ReferenceLine
          x={lse}
          stroke={CHART_COLORS.limite}
          strokeDasharray="4 4"
          strokeWidth={1.5}
          label={{ value: "LSE", position: "top", fontSize: 11, fill: CHART_COLORS.limite }}
        />
        <ReferenceLine
          x={nominal}
          stroke={CHART_COLORS.nominal}
          strokeWidth={1.5}
          label={{ value: "Nominal", position: "top", fontSize: 11, fill: CHART_COLORS.nominal }}
        />
      </ComposedChart>
    </ResponsiveContainer>
  )
}
