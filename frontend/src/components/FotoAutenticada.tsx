import { useEffect, useState } from "react"

import { apiClient } from "@/lib/api-client"

export function FotoAutenticada({ url, alt, className }: { url: string; alt: string; className?: string }) {
  const [objectUrl, setObjectUrl] = useState<string | null>(null)

  useEffect(() => {
    let cancelado = false
    let urlAtual: string | null = null

    apiClient.get(url, { responseType: "blob" }).then(({ data }) => {
      if (cancelado) return
      urlAtual = URL.createObjectURL(data as Blob)
      setObjectUrl(urlAtual)
    })

    return () => {
      cancelado = true
      if (urlAtual) URL.revokeObjectURL(urlAtual)
    }
  }, [url])

  if (!objectUrl) {
    return <div className={`animate-pulse bg-muted ${className ?? ""}`} />
  }

  return <img src={objectUrl} alt={alt} className={className} />
}
