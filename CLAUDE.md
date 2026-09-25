# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Sobre o projeto

Sistema web interno de **Coleta de Medidas e Análise de Capabilidade (Cp/Cpk)**, com módulo de
**Não Conformidade (RNC) e Plano de Ação (CAPA)**, alinhado à ISO 9001.

Roda em servidor local da empresa (rede interna), acessado por PC (escritório) e tablet/celular
(chão de fábrica). **Desde a migração do banco para o Neon, o sistema passou a depender de
internet** para acessar o banco de dados (trade-off aceito conscientemente em troca de não
precisar manter Postgres via Docker no servidor da fábrica) — isso substitui o requisito original
de funcionar totalmente offline.

A especificação completa e autoritativa está em [especificacao_sistema.md](especificacao_sistema.md).
Este arquivo é um resumo operacional — em caso de dúvida ou conflito, a especificação prevalece.

## Status do desenvolvimento

- **Fase 0 (bootstrap), Fase 1 (Cadastro de Peça/Etapa/Característica + autenticação + shell),
  Fase 2 (Coleta de Dados: grade Tab/Enter, cálculo de amostras, continuidade de rodada, finalização
  com motivo/pendência), Fase 3 (Cálculo de Cp/Cpk + histograma, com filtros por rodada/período/
  operador), Fase 4 (Não Conformidade/RNC + Plano de Ação/CAPA: máquina de estados completa,
  Ishikawa/5 Porquês/análise livre, ações corretivas com ciclos de reabertura, verificação de
  eficácia, numeração sequencial de RNC, indicadores), Fase 5 (Carta de Controle X-barra e R,
  integrada à tela de Análise: cada rodada finalizada é um subgrupo, limites de controle via
  constantes A2/D3/D4, pontos fora de controle destacados) e Fase 6 (Relatórios: Cp/Cpk por peça
  em PDF com histogramas, dados brutos de coleta em Excel, RNC individual em PDF com histórico
  completo, consolidado de peças e consolidado de Não Conformidades — os dois últimos restritos
  ao Gestor de Qualidade) — concluídas. MVP completo conforme a especificação original.**
- **Fase 7 (RNC estendida — pós-MVP): a abertura de RNC agora tem um campo `tipo` (Processo
  interno / Recebimento de fornecedor / Devolução de cliente) que muda os campos exibidos —
  Processo ganha Máquina, Operador(es) envolvido(s), Setup e Detecção editável; Fornecedor exige
  vincular um Fornecedor cadastrado + Nº da NF de entrada; Cliente exige Cliente + Vendedor + Nº
  NF + Data de emissão. `Detecção` (onde a NC foi pega: interno/cliente/fornecedor) é um campo
  novo, separado de `Origem` (por que o defeito aconteceu) — calculado automaticamente pelo
  backend para os tipos Fornecedor/Cliente, editável só no tipo Processo. RNC também aceita fotos
  anexadas (guardadas como bytea no Postgres/Neon — sem infraestrutura de disco/volume nova, já
  que não há volume persistente no `docker-compose.yml`; limite de 5 MB e 8 fotos por RNC,
  jpeg/png/webp). Isso exigiu 3 cadastros novos — **Fornecedor**, **Máquina**, **Departamento**
  (mesmo padrão de Peça: código único, status ativo/inativo) — todos com tela própria.**
- **Fase 8 (Tratativas por Departamento, pós-MVP): a RNC pode ter uma ou mais "tratativas
  departamentais" (conceito novo, separado do Plano de Ação — ex: "Sucata → PCP dar baixa na
  ordem"), atribuídas só na etapa de tratamento. Cada tratativa tem status pendente/concluída;
  concluir exige uma observação/referência obrigatória. O encerramento da RNC fica **bloqueado**
  enquanto houver tratativa pendente (erro `ACOES_DEPARTAMENTAIS_PENDENTES`), mas Analista/Gestor
  podem remover uma tratativa pendente ou forçar o encerramento mesmo assim
  (`ignorar_pendencias=true`, fica registrado em auditoria). Quem pode concluir uma tratativa:
  **qualquer usuário do departamento atribuído** (independente do perfil Operador/Analista/
  Gestor) **ou** Analista/Gestor — por isso `Usuario` ganhou um campo opcional `departamento_id`.
  Tela nova "Tratativas" no menu lateral lista as pendências (auto-filtradas pelo departamento de
  quem está logado; Qualidade vê/filtra todos os departamentos).**
- **Fase 9 (Depósito da Qualidade, pós-MVP): cadastro de bloqueios de peças que ficam paradas no
  depósito da qualidade — Analista/Gestor registram um bloqueio (peça já cadastrada + motivo +
  característica de desenho a que se atentar + cliente, opcionais + vínculo opcional com uma RNC
  já aberta + 1 foto opcional), qualquer perfil autenticado pode consultar buscando pelo código da
  peça (histórico completo — uma peça pode ter vários bloqueios ao longo do tempo). Cada bloqueio
  tem status `bloqueado`/`liberado`; liberar exige uma observação obrigatória. Isso exigiu um
  perfil novo, **Inspetor** (só consulta, não cadastra nem libera) — hierarquia de perfis: Gestor
  > Analista > Inspetor > Operador.**
- Próximos passos possíveis (fora do escopo original do MVP): tela de gestão de usuários completa
  (hoje só placeholder na Sidebar — atribuir departamento a um usuário já funciona via
  `PATCH /usuarios/{id}/departamento`, mas não há CRUD completo de usuário), roteamento de
  ações departamentais integrado ao Plano de Ação (hoje são conceitos deliberadamente separados),
  páginas de erro/offline, segredos de produção (os atuais são de desenvolvimento — ver
  `.env`/`.env.example`).
- Plano de arquitetura completo (todas as fases) em `C:\Users\ramos\.claude\plans\compressed-wandering-biscuit.md`.

## Stack (decidida e implementada)

- Backend: FastAPI + SQLAlchemy 2.0 + Alembic (`backend/`)
- Banco de dados: **PostgreSQL hospedado no Neon** (https://neon.tech) — banco único do projeto,
  usado tanto em produção (via Docker Compose) quanto em dev local sem Docker (`backend/.env.local`,
  ver `backend/.env.local.example`). Não há mais suporte a SQLite nem a Postgres local via Docker
  (o serviço `db` foi removido do `docker-compose.yml`); driver `psycopg2-binary` (pin em
  `requirements.txt` — precisa ser >= 2.9.12 para ter wheel no Python 3.14 usado pelo `.venv`).
- Frontend: React + TypeScript + Vite + Tailwind CSS + shadcn/ui + React Query + React Router +
  react-hook-form/zod + Recharts (`frontend/`)

### Rodando localmente sem Docker (dev)

```
# backend
cd backend && .venv/Scripts/python.exe -m uvicorn app.main:app --reload --env-file .env.local
cd backend && .venv/Scripts/python.exe -m app.seed.seed_data   # popula usuários/peças de teste

# frontend
cd frontend && npm run dev
```

Usuários de teste (seed): `gestor1` / `analista1` / `inspetor1` / `operador1`, todos com senha
`senha123`.

### Rodando via Docker Compose (produção / servidor da empresa)

```
docker compose up --build
```

## Ordem sugerida de desenvolvimento do MVP

1. Cadastro de Peça → Etapa → Característica
2. Coleta de Dados
3. Cálculo de Cp/Cpk
4. Módulo de Não Conformidade (RNC + Plano de Ação)
5. Carta de Controle (X-barra e R)
6. Relatórios

## Modelo de domínio (hierarquia principal)

```
Peça
 └── Etapa (numero_etapa único por peça, tem sua própria frequência de medição)
      └── Característica (cota, com nominal + tolerâncias → LSE/LIE calculados)

OrdemProducao (numero_ordem, quantidade — mesma quantidade vale para todas as etapas da peça)

RodadaColeta (peça + ordem + etapa; status: em_andamento / finalizada / finalizada_com_pendencia)
 └── Medicao (uma por amostra x característica; registra o operador individualmente)

Fornecedor / Maquina / Departamento (cadastros auxiliares, mesmo padrão de Peça: código único,
status ativo/inativo — ver Fase 7/8 em "Status do desenvolvimento")

Usuario (perfil: gestor_qualidade/analista_qualidade/inspetor/operador; departamento_id opcional,
FK pra Departamento — usado só pra roteamento de tratativas, não é um perfil de permissão novo)

BloqueioDeposito (peça bloqueada no depósito da qualidade — ver Fase 9; status
bloqueado/liberado, motivo, caracteristica_atencao e cliente opcionais, nao_conformidade_id
opcional, 1 foto opcional; uma peça pode ter vários bloqueios — histórico)

NaoConformidade / RNC (numero_rnc sequencial único para toda a empresa, não reinicia por peça)
 - tipo: processo / fornecedor / cliente — muda quais campos abaixo se aplicam
 - deteccao: interno/cliente/fornecedor (separado de origem; auto-calculado fora do tipo=processo)
 - maquina_id, operadores (N:N com Usuario), setup — só tipo=processo
 - fornecedor_id, numero_nf_entrada — só tipo=fornecedor
 - cliente, vendedor, numero_nf, data_emissao_nf — só tipo=cliente
 - fotos (NaoConformidadeFoto, bytea no Postgres)
 ├── PlanoDeAcao (0 ou 1 ativo por RNC; aberto só se "Necessário Plano de Ação" for marcado)
 │    ├── CausaRaizIshikawa (6M: Método, Mão de obra, Máquina, Material, Meio Ambiente, Medição)
 │    ├── CausaRaiz5Porques (níveis 1-5)
 │    ├── AcaoCorretiva (uma ou mais, cada uma com responsável e prazo próprios)
 │    └── VerificacaoEficaciaPlano
 └── AcaoDepartamental (0 ou mais; conceito separado do PlanoDeAcao — ver Fase 8; status
      pendente/concluida, departamento_id, observacao_conclusao obrigatória ao concluir)
```

Entidades e campos completos: ver seção 3 da especificação (inclui as extensões de Fase 7/8).

## Regras de negócio críticas

**Cálculo de amostras da coleta:**
`amostras = max(1, ceil(quantidade_ordem × (freq_numerador / freq_denominador)))`
O valor calculado é editável manualmente (com justificativa opcional).

**Continuidade de rodada:** se já existe uma rodada "em_andamento" para a mesma combinação
peça + ordem + etapa, o operador entra nela (não cria uma nova). Cada medição registra o
operador que a fez, não a rodada.

**Encerramento antecipado:** finalizar uma rodada com menos amostras que o calculado exige
motivo obrigatório. Se o motivo for "Não conformidade identificada no processo", ou se uma
medição individual ficar fora de LIE/LSE, o sistema oferece (mas não cria automaticamente)
a abertura de uma RNC pré-preenchida.

**Cp/Cpk:**
- `Cp = (LSE − LIE) / (6σ)`
- `Cpk = min[(LSE − x̄) / (3σ), (x̄ − LIE) / (3σ)]`
- σ = desvio padrão amostral (n−1)
- Sempre calculado e exibido, mesmo com poucas amostras (mínimo 1); abaixo de um limiar
  configurável (sugestão: 20, ideal 30+) exibir aviso de baixa robustez estatística, sem bloquear.
- Classificação: Cpk < 1,00 🔴 não capaz · 1,00–1,33 🟡 atenção · > 1,33 🟢 capaz (parametrizável).

**Carta de Controle X-barra/R:** cada rodada finalizada é um subgrupo; só é exibida com pelo
menos 2 rodadas finalizadas para a combinação peça+etapa+característica.

**RNC:**
- Não pode existir sem peça vinculada (ordem e etapa são opcionais).
- Pode ser encerrada sem causa raiz/ação corretiva preenchidas, desde que a disposição da
  peça esteja definida.
- Encerramento da RNC é independente do andamento do Plano de Ação vinculado.
- **Tipo da RNC** (Fase 7): `processo` (default) / `fornecedor` / `cliente`, escolhido na
  abertura — condiciona quais campos aparecem (ver "Modelo de domínio" acima). `fornecedor_id`
  é obrigatório no tipo fornecedor, `cliente` é obrigatório no tipo cliente (validado no schema).
- **Detecção** é calculada pelo backend, não confiável vinda do cliente: sempre `interno` no tipo
  fornecedor, sempre `cliente` no tipo cliente; só é livremente editável no tipo processo.
- **Fotos**: upload multipart após a abertura (`POST /nao-conformidades/{id}/fotos`), guardadas
  como bytea; máx. 5 MB por arquivo, 8 fotos por RNC, apenas jpeg/png/webp.

**Tratativas por Departamento (Fase 8, separado do Plano de Ação):**
- Atribuídas só na etapa de tratamento (Analista/Gestor), nunca na abertura.
- Concluir exige observação/referência obrigatória; quem pode concluir é o usuário do
  departamento atribuído (`usuario.departamento_id == acao.departamento_id`, qualquer perfil)
  ou Analista/Gestor.
- `POST /nao-conformidades/{id}/encerrar` é **bloqueado** (409 `ACOES_DEPARTAMENTAIS_PENDENTES`)
  enquanto houver tratativa `pendente`; Analista/Gestor podem remover a tratativa pendente ou
  passar `ignorar_pendencias=true` pra forçar o encerramento mesmo assim (fica auditado).
- Uma tratativa `concluida` não pode ser removida (preserva rastro de auditoria).

**Depósito da Qualidade (Fase 9):**
- Um bloqueio sempre referencia uma Peça já cadastrada (não aceita código livre).
- Motivo é obrigatório; característica de desenho a que se atentar, cliente e vínculo com uma
  RNC existente são opcionais.
- Uma peça pode ter múltiplos bloqueios ao longo do tempo (histórico completo, não só o mais
  recente).
- Liberar um bloqueio exige observação obrigatória; um bloqueio já liberado não pode ser liberado
  de novo (`BLOQUEIO_JA_LIBERADO`).
- Cadastrar, anexar foto e liberar são ações de Analista/Gestor; consultar (buscar por código,
  listar) é liberado a qualquer perfil autenticado, incluindo Inspetor.

**Plano de Ação:**
- Só avança para "aguardando_verificacao" quando **todas** as ações corretivas estiverem
  "Concluída".
- Não pode ser encerrado sem verificação de eficácia com resultado "Eficaz".
- Resultado "Não eficaz" → volta automaticamente para "em_andamento" (fica marcado como
  reaberto, histórico da tentativa anterior preservado).
- Troca de metodologia de causa raiz (Ishikawa ↔ 5 Porquês ↔ Livre) é permitida a qualquer
  momento; deve exibir aviso de que os dados da metodologia anterior serão descartados da
  tela ativa (mas preservados em histórico/auditoria).
- No máximo um Plano de Ação **ativo** por RNC (pode haver histórico de planos anteriores).

## Perfis de usuário e permissões

| Perfil | Pode fazer |
|---|---|
| Gestor de Qualidade | Tudo do Analista + gestão de usuários, relatórios e indicadores consolidados |
| Analista de Qualidade | Cadastrar peças/etapas/características, ver análises, reabrir rodadas, tratar RNC, investigar causa raiz, cadastrar ações corretivas, encerrar Plano de Ação, cadastrar/liberar bloqueios no Depósito da Qualidade |
| Inspetor | Só consultar (ver Depósito da Qualidade, análises, RNCs) — não cadastra nem altera nada |
| Operador | Realizar coletas, abrir RNC |

Hierarquia (ver Fase 9): Gestor > Analista > Inspetor > Operador. Sem limite fixo de número de
usuários cadastrados.

**Departamento não é um perfil novo** — é um campo opcional (`departamento_id`) que qualquer
usuário, de qualquer perfil, pode ter. Ele só habilita concluir as tratativas departamentais
atribuídas ao departamento da pessoa (ver Fase 8) e filtra a tela "Tratativas" por padrão; não
muda nada mais do que esses dois perfis já podiam ou não fazer.

## Requisitos não funcionais

- Ambiente: servidor local na rede da empresa; banco de dados (Neon) exige conexão de internet —
  ver observação em "Sobre o projeto".
- Interface responsiva (desktop e tablet/celular).
- Backup diário automático do banco de dados.
- Log de auditoria (quem, quando) em cadastros, reabertura de coletas, e mudanças de status
  de RNC/Plano de Ação.
- Telas de coleta devem responder rápido mesmo em Wi-Fi de fábrica; navegação por
  Tab/Enter na grade de digitação (evitar depender de mouse/toque).

## Fora de escopo (V1)

- Integração com instrumentos digitais (USB/Bluetooth).
- Multi-tenant (múltiplas empresas/plantas).
- App mobile nativo (web responsivo cobre esse caso por enquanto).
