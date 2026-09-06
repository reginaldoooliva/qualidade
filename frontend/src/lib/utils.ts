import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/** Data de hoje no fuso horário local, formatada como YYYY-MM-DD (para inputs type="date"). */
export function dataLocalHoje(): string {
  const hoje = new Date()
  const ano = hoje.getFullYear()
  const mes = String(hoje.getMonth() + 1).padStart(2, "0")
  const dia = String(hoje.getDate()).padStart(2, "0")
  return `${ano}-${mes}-${dia}`
}

/**
 * Formata uma data-apenas "YYYY-MM-DD" (sem horário) vinda da API como "DD/MM/AAAA".
 * Evita usar `new Date(str).toLocaleDateString()`: o construtor de Date interpreta
 * "YYYY-MM-DD" como UTC meia-noite, e converter para o fuso local pode exibir o dia
 * anterior. Aqui é apenas reformatação de texto, sem conversão de fuso.
 */
export function formatarDataBR(dataIso: string): string {
  const [ano, mes, dia] = dataIso.split("-")
  return `${dia}/${mes}/${ano}`
}
