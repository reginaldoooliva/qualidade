import {
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

import { CHART_COLORS } from "@/features/analise/chartColors"

interface PontoCarta {
  label: string
  valor: number
  foraControle: boolean
}

function DotCarta({ cx, cy, payload }: { cx?: number; cy?: number; payload?: PontoCarta }) {
  if (cx === undefined || cy === undefined || !payload) return null
  const foraControle = payload.foraControle
  return (
    <circle
      cx={cx}
      cy={cy}
      r={foraControle ? 5 : 3}
      fill={foraControle ? "var(--status-critical)" : CHART_COLORS.bar}
      stroke="var(--card)"
      strokeWidth={foraControle ? 2 : 1}
    />
  )
}

function TooltipCarta({
  active,
  payload,
  casasDecimais,
  unidade,
}: {
  active?: boolean
  payload?: { payload: PontoCarta }[]
  casasDecimais: number
  unidade: string
}) {
  if (!active || !payload?.length) return null
  const ponto = payload[0].payload
  return (
    <div className="rounded-md border bg-popover px-3 py-2 text-xs shadow-md">
      <div className="text-muted-foreground">{ponto.label}</div>
      <div className="font-medium text-popover-foreground">
        {ponto.valor.toFixed(casasDecimais)} {unidade}
      </div>
      {ponto.foraControle && <div className="font-medium text-[var(--status-critical)]">Fora de controle</div>}
    </div>
  )
}

export function CartaControleChart({
  titulo,
  pontos,
  linhaCentral,
  lsc,
  lic,
  casasDecimais,
  unidade,
}: {
  titulo: string
  pontos: PontoCarta[]
  linhaCentral: number
  lsc: number
  lic: number
  casasDecimais: number
  unidade: string
}) {
  const valores = pontos.map((p) => p.valor)
  const min = Math.min(...valores, lic)
  const max = Math.max(...valores, lsc)
  const margem = (max - min) * 0.1 || 1

  return (
    <div>
      <div className="mb-1 text-xs font-medium text-muted-foreground">{titulo}</div>
      <ResponsiveContainer width="100%" height={180}>
        <ComposedChart data={pontos} margin={{ top: 8, right: 36, bottom: 4, left: 4 }}>
          <CartesianGrid vertical={false} stroke={CHART_COLORS.grid} />
          <XAxis dataKey="label" stroke="var(--muted-foreground)" fontSize={10} tickLine={false} />
          <YAxis
            domain={[min - margem, max + margem]}
            tickFormatter={(v: number) => v.toFixed(casasDecimais)}
            stroke="var(--muted-foreground)"
            fontSize={10}
            width={44}
          />
          <Tooltip content={<TooltipCarta casasDecimais={casasDecimais} unidade={unidade} />} />
          <ReferenceLine
            y={linhaCentral}
            stroke={CHART_COLORS.nominal}
            strokeWidth={1.5}
            label={{ value: "LC", position: "right", fontSize: 10, fill: CHART_COLORS.nominal }}
          />
          <ReferenceLine
            y={lsc}
            stroke={CHART_COLORS.limite}
            strokeDasharray="4 4"
            strokeWidth={1.5}
            label={{ value: "LSC", position: "right", fontSize: 10, fill: CHART_COLORS.limite }}
          />
          <ReferenceLine
            y={lic}
            stroke={CHART_COLORS.limite}
            strokeDasharray="4 4"
            strokeWidth={1.5}
            label={{ value: "LIC", position: "right", fontSize: 10, fill: CHART_COLORS.limite }}
          />
          <Line
            type="linear"
            dataKey="valor"
            stroke={CHART_COLORS.bar}
            strokeWidth={2}
            dot={<DotCarta />}
            isAnimationActive={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
