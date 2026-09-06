export type Perfil = "operador" | "analista_qualidade" | "gestor_qualidade"
export type StatusCadastro = "ativo" | "inativo"
export type UnidadeMedida = "mm" | "cm" | "polegada"
export type InstrumentoMedicao = "paquimetro" | "micrometro" | "relogio_comparador" | "outro"

export interface Usuario {
  id: number
  nome: string
  login: string
  perfil: Perfil
  status: StatusCadastro
}

export interface Peca {
  id: number
  codigo: string
  descricao: string
  cliente: string | null
  desenho: string | null
  revisao: string
  material: string | null
  observacoes: string | null
  status: StatusCadastro
}

export interface PecaListItem extends Peca {
  numero_caracteristicas: number
}

export interface PecaFormValues {
  codigo: string
  descricao: string
  cliente?: string | null
  desenho?: string | null
  revisao: string
  material?: string | null
  observacoes?: string | null
}

export interface Etapa {
  id: number
  peca_id: number
  numero_etapa: number
  descricao: string | null
  freq_numerador: number
  freq_denominador: number
  status: StatusCadastro
}

export interface EtapaFormValues {
  numero_etapa: number
  descricao?: string | null
  freq_numerador: number
  freq_denominador: number
}

export interface Caracteristica {
  id: number
  etapa_id: number
  nome: string
  posicao_desenho: string | null
  nominal: number
  tol_superior: number
  tol_inferior: number
  unidade: UnidadeMedida
  instrumento: InstrumentoMedicao | null
  casas_decimais: number
  status: StatusCadastro
  lse: number
  lie: number
}

export interface CaracteristicaFormValues {
  nome: string
  posicao_desenho?: string | null
  nominal: number
  tol_superior: number
  tol_inferior: number
  unidade: UnidadeMedida
  instrumento?: InstrumentoMedicao | null
  casas_decimais: number
}

export type StatusRodada = "em_andamento" | "finalizada" | "finalizada_com_pendencia"
export type MotivoEncerramento =
  | "ordem_interrompida"
  | "ordem_cancelada"
  | "quantidade_menor_que_previsto"
  | "nao_conformidade_processo"
  | "outro"

export interface OrdemProducao {
  id: number
  peca_id: number
  numero_ordem: string
  quantidade: number
}

export interface Medicao {
  id: number
  caracteristica_id: number
  amostra_numero: number
  valor: number
  operador_id: number
  operador_nome: string
  data_hora: string
}

export interface RodadaColeta {
  id: number
  ordem_id: number
  etapa_id: number
  amostras_calculadas: number
  amostras_ajustadas: number | null
  amostras_alvo: number
  justificativa_ajuste: string | null
  status: StatusRodada
  motivo_encerramento_antecipado: MotivoEncerramento | null
  motivo_detalhe: string | null
  data_hora_inicio: string
}

export interface RodadaColetaDetalhe extends RodadaColeta {
  peca: Peca
  etapa: Etapa
  ordem: OrdemProducao
  caracteristicas: Caracteristica[]
  medicoes: Medicao[]
}

export interface IniciarColetaPayload {
  peca_id: number
  numero_ordem: string
  quantidade_ordem?: number
  etapa_id: number
  amostras_ajustadas?: number
  justificativa_ajuste?: string
}

export interface FinalizarColetaPayload {
  motivo_encerramento_antecipado?: MotivoEncerramento
  motivo_detalhe?: string
}

export interface FinalizarColetaResponse extends RodadaColeta {
  sugestao_abrir_rnc: boolean
}

export type ClassificacaoCpk = "nao_capaz" | "atencao" | "capaz"

export interface RodadaResumo {
  id: number
  numero_ordem: string
  status: StatusRodada
  data_hora_inicio: string
}

export interface OperadorResumo {
  id: number
  nome: string
}

export interface CaracteristicaCapabilidade {
  caracteristica_id: number
  nome: string
  unidade: UnidadeMedida
  instrumento: InstrumentoMedicao | null
  casas_decimais: number
  nominal: number
  lie: number
  lse: number
  n_amostras: number
  media: number | null
  desvio_padrao: number | null
  cp: number | null
  cpk: number | null
  classificacao: ClassificacaoCpk | null
  baixa_robustez: boolean
  valores: number[]
}

export interface AnaliseCapabilidadeResponse {
  peca_id: number
  peca_codigo: string
  etapa_id: number
  etapa_numero: number
  rodadas_incluidas: RodadaResumo[]
  operadores_disponiveis: OperadorResumo[]
  limiar_baixa_robustez: number
  caracteristicas: CaracteristicaCapabilidade[]
}

export interface SubgrupoCarta {
  rodada_id: number
  numero_ordem: string
  data_hora_inicio: string
  n: number
  media: number
  amplitude: number
  fora_controle_x: boolean
  fora_controle_r: boolean
}

export interface CartaControleCaracteristica {
  caracteristica_id: number
  nome: string
  unidade: UnidadeMedida
  casas_decimais: number
  subgrupos: SubgrupoCarta[]
  exibir: boolean
  tamanho_amostra_medio: number | null
  linha_central_x: number | null
  lsc_x: number | null
  lic_x: number | null
  linha_central_r: number | null
  lsc_r: number | null
  lic_r: number | null
}

export interface CartaControleResponse {
  peca_id: number
  peca_codigo: string
  etapa_id: number
  etapa_numero: number
  rodadas_incluidas: RodadaResumo[]
  operadores_disponiveis: OperadorResumo[]
  caracteristicas: CartaControleCaracteristica[]
}

// ---- Não Conformidade (RNC) / Plano de Ação (CAPA) ----

export type StatusNC = "aberta" | "em_analise" | "em_tratamento" | "encerrada"
export type ClassificacaoNC = "critica" | "maior" | "menor"
export type OrigemNC = "processo" | "materia_prima" | "projeto" | "instrumento" | "mao_de_obra" | "outro"
export type DisposicaoNC =
  | "retrabalho"
  | "sucata"
  | "uso_como_esta"
  | "devolucao_fornecedor"
  | "reclassificacao"

export interface AbrirNCPayload {
  peca_id: number
  ordem_id?: number
  etapa_id?: number
  caracteristica_id?: number
  rodada_id?: number
  descricao_problema: string
  quantidade_afetada: number
  classificacao: ClassificacaoNC
  origem: OrigemNC
}

export interface TratarNCPayload {
  causa_raiz_preliminar?: string | null
  disposicao?: DisposicaoNC | null
  responsavel_analise_id?: number | null
  necessita_plano_acao: boolean
}

export interface NaoConformidade {
  id: number
  numero_rnc: string
  peca_id: number
  ordem_id: number | null
  etapa_id: number | null
  caracteristica_id: number | null
  rodada_id: number | null
  descricao_problema: string
  quantidade_afetada: number
  classificacao: ClassificacaoNC
  origem: OrigemNC
  causa_raiz_preliminar: string | null
  disposicao: DisposicaoNC | null
  responsavel_analise_id: number | null
  necessita_plano_acao: boolean
  aberto_por_id: number
  aberto_por_nome: string
  data_abertura: string
  data_encerramento: string | null
  status: StatusNC
}

export interface NaoConformidadeListItem extends NaoConformidade {
  peca_codigo: string
  peca_descricao: string
  plano_acao_id: number | null
  plano_acao_status: string | null
  tem_plano_aberto: boolean
}

export interface EventoHistorico {
  acao: string
  usuario_nome: string
  detalhe: string | null
  criado_em: string
}

export interface PlanoAcaoResumo {
  id: number
  status: string
  ciclo: number
}

export interface NaoConformidadeDetalhe extends NaoConformidade {
  peca: Peca
  etapa: Etapa | null
  caracteristica: Caracteristica | null
  responsavel_analise: { id: number; nome: string } | null
  plano_acao_ativo_id: number | null
  tem_plano_aberto: boolean
  planos_acao: PlanoAcaoResumo[]
  historico: EventoHistorico[]
}

export interface IndicadoresNC {
  abertas: number
  em_analise: number
  em_tratamento: number
  encerradas_no_mes: number
  com_plano_aberto: number
  acoes_atrasadas: number
}

export type MetodologiaCausaRaiz = "ishikawa" | "cinco_porques" | "livre"
export type StatusPlanoAcao = "aberto" | "em_andamento" | "aguardando_verificacao" | "encerrado" | "reaberto"
export type StatusAcaoCorretivaCalculado = "pendente" | "concluida" | "atrasada"
export type CategoriaIshikawa = "metodo" | "mao_de_obra" | "maquina" | "material" | "meio_ambiente" | "medicao"
export type ResultadoVerificacao = "eficaz" | "nao_eficaz"

export interface CausaIshikawa {
  id: number
  categoria: CategoriaIshikawa
  descricao_causa: string
  marcada_como_raiz: boolean
}

export interface Causa5Porques {
  id: number
  nivel: number
  pergunta: string
  resposta: string
  marcada_como_raiz: boolean
}

export interface AcaoCorretiva {
  id: number
  ciclo: number
  descricao: string
  responsavel_id: number
  responsavel_nome: string
  prazo: string
  data_execucao: string | null
  status: StatusAcaoCorretivaCalculado
}

export interface VerificacaoEficacia {
  id: number
  ciclo: number
  data_verificacao: string
  responsavel_id: number
  responsavel_nome: string
  resultado: ResultadoVerificacao
  observacoes: string | null
  criado_em: string
}

export interface ItemConsolidadoPeca {
  peca_id: number
  codigo: string
  descricao: string
  caracteristica_critica: string | null
  etapa_numero: number | null
  cpk_critico: number | null
  classificacao: ClassificacaoCpk | null
  n_amostras: number
}

export interface ConsolidadoNaoConformidade {
  total_rnc: number
  total_encerradas: number
  tempo_medio_tratamento_dias: number | null
  taxa_reincidencia: number
  por_peca: Record<string, number>
  por_classificacao: Record<string, number>
  por_origem: Record<string, number>
}

export interface PlanoDeAcaoDetalhe {
  id: number
  nc_id: number
  numero_rnc: string
  metodologia_causa_raiz: MetodologiaCausaRaiz
  conclusao_causa_raiz: string | null
  status: StatusPlanoAcao
  ciclo: number
  acoes_corretivas: AcaoCorretiva[]
  causas_ishikawa: CausaIshikawa[]
  causas_5porques: Causa5Porques[]
  verificacoes: VerificacaoEficacia[]
  historico: EventoHistorico[]
}

export interface PlanoDeAcaoListItem {
  id: number
  nc_id: number
  numero_rnc: string
  peca_codigo: string
  peca_descricao: string
  metodologia_causa_raiz: MetodologiaCausaRaiz
  status: StatusPlanoAcao
  ciclo: number
  acoes: AcaoCorretiva[]
  total_acoes: number
  acoes_concluidas: number
  acoes_atrasadas: number
  proximo_prazo: string | null
}

export interface IndicadoresPlanoAcao {
  total_ativos: number
  aguardando_verificacao: number
  planos_atrasados: number
  acoes_atrasadas: number
  encerrados_no_mes: number
}
