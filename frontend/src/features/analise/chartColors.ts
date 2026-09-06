// Paleta validada (dataviz skill): status é fixo — nunca "themed" — e a barra de
// histograma usa o slot categórico 1 (azul) por ser série única.
export const CHART_COLORS = {
  bar: "var(--analise-bar)",
  limite: "var(--analise-limite)",
  nominal: "var(--analise-nominal)",
  grid: "var(--analise-grid)",
} as const

export const STATUS_CPK = {
  capaz: { cor: "var(--status-good)", label: "Capaz" },
  atencao: { cor: "var(--status-warning)", label: "Atenção" },
  nao_capaz: { cor: "var(--status-critical)", label: "Não capaz" },
} as const
