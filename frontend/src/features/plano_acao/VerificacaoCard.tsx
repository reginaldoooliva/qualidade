import { useState } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { useRegistrarVerificacao } from "@/features/plano_acao/api"
import { useUsuarios } from "@/features/usuarios/api"
import { getApiError } from "@/lib/api-client"
import { dataLocalHoje, formatarDataBR } from "@/lib/utils"
import type { PlanoDeAcaoDetalhe, ResultadoVerificacao } from "@/types/api"

const RESULTADO_LABEL: Record<ResultadoVerificacao, string> = { eficaz: "Eficaz", nao_eficaz: "Não eficaz" }

export function VerificacaoCard({ plano, podeEditar }: { plano: PlanoDeAcaoDetalhe; podeEditar: boolean }) {
  const { data: usuarios } = useUsuarios()
  const usuarioItems = Object.fromEntries((usuarios ?? []).map((u) => [String(u.id), u.nome]))
  const registrarVerificacao = useRegistrarVerificacao(plano.id)

  const [data, setData] = useState(dataLocalHoje())
  const [responsavelId, setResponsavelId] = useState("")
  const [resultado, setResultado] = useState<ResultadoVerificacao | "">("")
  const [observacoes, setObservacoes] = useState("")

  const mostrarFormulario = podeEditar && plano.status === "aguardando_verificacao"

  function handleSubmit() {
    if (!responsavelId || !resultado) return
    registrarVerificacao.mutate(
      {
        data_verificacao: data,
        responsavel_id: Number(responsavelId),
        resultado,
        observacoes: observacoes || undefined,
      },
      {
        onSuccess: () => {
          toast.success(resultado === "eficaz" ? "Plano encerrado — verificação eficaz" : "Plano reaberto — verificação não eficaz")
          setResponsavelId("")
          setResultado("")
          setObservacoes("")
        },
        onError: (error) => toast.error(getApiError(error).detail),
      }
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Verificação de eficácia</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {mostrarFormulario && (
          <div className="space-y-3 rounded-md border bg-muted/30 p-3">
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
              <div className="space-y-1.5">
                <Label>Data da verificação</Label>
                <Input type="date" value={data} onChange={(e) => setData(e.target.value)} />
              </div>
              <div className="space-y-1.5">
                <Label>Responsável</Label>
                <Select value={responsavelId} onValueChange={(v) => setResponsavelId(v ?? "")} items={usuarioItems}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Selecione" />
                  </SelectTrigger>
                  <SelectContent>
                    {(usuarios ?? []).map((u) => (
                      <SelectItem key={u.id} value={String(u.id)}>
                        {u.nome}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1.5">
                <Label>Resultado</Label>
                <Select
                  value={resultado}
                  onValueChange={(v) => setResultado((v as ResultadoVerificacao) ?? "")}
                  items={RESULTADO_LABEL}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Selecione" />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(RESULTADO_LABEL).map(([value, label]) => (
                      <SelectItem key={value} value={value}>
                        {label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-1.5">
              <Label>Observações (opcional)</Label>
              <Textarea rows={2} value={observacoes} onChange={(e) => setObservacoes(e.target.value)} />
            </div>
            <Button
              onClick={handleSubmit}
              disabled={!responsavelId || !resultado || registrarVerificacao.isPending}
            >
              {registrarVerificacao.isPending ? "Registrando..." : "Registrar verificação"}
            </Button>
          </div>
        )}

        {plano.verificacoes.length === 0 ? (
          !mostrarFormulario && <p className="text-sm text-muted-foreground">Nenhuma verificação registrada ainda.</p>
        ) : (
          <ul className="space-y-2 text-sm">
            {[...plano.verificacoes].reverse().map((v) => (
              <li key={v.id} className="flex items-start justify-between gap-3 border-b pb-2 last:border-0">
                <div>
                  <span className={v.resultado === "eficaz" ? "text-[var(--status-good)]" : "text-[var(--status-critical)]"}>
                    {RESULTADO_LABEL[v.resultado]}
                  </span>{" "}
                  · ciclo {v.ciclo} — {v.responsavel_nome} em {formatarDataBR(v.data_verificacao)}
                  {v.observacoes && <div className="text-muted-foreground">{v.observacoes}</div>}
                </div>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  )
}
