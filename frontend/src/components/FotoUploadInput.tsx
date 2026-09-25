import { useEffect, useRef, useState } from "react"
import { Camera, X } from "lucide-react"

import { Button } from "@/components/ui/button"

export function FotoUploadInput({
  arquivos,
  onChange,
}: {
  arquivos: File[]
  onChange: (arquivos: File[]) => void
}) {
  const inputRef = useRef<HTMLInputElement>(null)

  function handleSelecionar(e: React.ChangeEvent<HTMLInputElement>) {
    const novos = Array.from(e.target.files ?? [])
    if (novos.length > 0) onChange([...arquivos, ...novos])
    e.target.value = ""
  }

  function handleRemover(index: number) {
    onChange(arquivos.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-2">
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        capture="environment"
        multiple
        className="hidden"
        onChange={handleSelecionar}
      />
      <Button type="button" variant="outline" onClick={() => inputRef.current?.click()}>
        <Camera className="size-4" />
        Adicionar foto
      </Button>
      {arquivos.length > 0 && (
        <div className="flex flex-wrap gap-3">
          {arquivos.map((arquivo, index) => (
            <FotoThumb key={`${arquivo.name}-${index}`} arquivo={arquivo} onRemover={() => handleRemover(index)} />
          ))}
        </div>
      )}
    </div>
  )
}

function FotoThumb({ arquivo, onRemover }: { arquivo: File; onRemover: () => void }) {
  const url = useObjectUrl(arquivo)
  return (
    <div className="group relative size-20 overflow-hidden rounded-md border bg-muted">
      {url && <img src={url} alt={arquivo.name} className="size-full object-cover" />}
      <button
        type="button"
        onClick={onRemover}
        className="absolute right-1 top-1 flex size-5 items-center justify-center rounded-full bg-black/60 text-white opacity-0 transition-opacity group-hover:opacity-100"
        aria-label={`Remover ${arquivo.name}`}
      >
        <X className="size-3" />
      </button>
    </div>
  )
}

function useObjectUrl(file: File): string | null {
  const [url, setUrl] = useState<string | null>(null)

  useEffect(() => {
    const objectUrl = URL.createObjectURL(file)
    setUrl(objectUrl)
    return () => URL.revokeObjectURL(objectUrl)
  }, [file])

  return url
}
