import { useState } from "react"
import { Search } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { usePecas } from "@/features/pecas/api"
import type { PecaListItem } from "@/types/api"

export function PecaBuscaInput({
  value,
  onChange,
}: {
  value: PecaListItem | null
  onChange: (peca: PecaListItem | null) => void
}) {
  const [busca, setBusca] = useState("")
  const { data: resultados } = usePecas({ busca: busca || undefined })
  const ativas = resultados?.filter((p) => p.status === "ativo") ?? []

  if (value) {
    return (
      <div className="flex items-center justify-between rounded-md border bg-muted/30 px-3 py-2">
        <div>
          <div className="font-medium">{value.codigo}</div>
          <div className="text-sm text-muted-foreground">{value.descricao}</div>
        </div>
        <Button variant="ghost" size="sm" onClick={() => onChange(null)}>
          Trocar
        </Button>
      </div>
    )
  }

  return (
    <div className="relative">
      <Search className="absolute left-2.5 top-2.5 size-4 text-muted-foreground" />
      <Input
        autoFocus
        placeholder="Buscar por código ou descrição..."
        value={busca}
        onChange={(e) => setBusca(e.target.value)}
        className="pl-8"
      />
      {busca && (
        <div className="mt-1 max-h-56 overflow-auto rounded-md border bg-background shadow-sm">
          {ativas.length === 0 && (
            <div className="p-3 text-sm text-muted-foreground">Nenhuma peça ativa encontrada.</div>
          )}
          {ativas.map((p) => (
            <button
              key={p.id}
              type="button"
              className="flex w-full items-center justify-between px-3 py-2 text-left text-sm hover:bg-muted"
              onClick={() => {
                onChange(p)
                setBusca("")
              }}
            >
              <span className="font-medium">{p.codigo}</span>
              <span className="text-muted-foreground">{p.descricao}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
