import { apiClient } from "@/lib/api-client"

export async function baixarArquivo(
  url: string,
  params: Record<string, string | number | undefined>,
  nomeArquivoFallback: string
): Promise<void> {
  const resposta = await apiClient.get(url, { params, responseType: "blob" })
  const contentDisposition = resposta.headers["content-disposition"] as string | undefined
  const match = contentDisposition?.match(/filename="?([^"]+)"?/)
  const nomeArquivo = match?.[1] ?? nomeArquivoFallback

  const blobUrl = URL.createObjectURL(resposta.data as Blob)
  const link = document.createElement("a")
  link.href = blobUrl
  link.download = nomeArquivo
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(blobUrl)
}
