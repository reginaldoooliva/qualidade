# Especificação Técnica
## Sistema de Coleta de Medidas e Análise de Capabilidade (Cp/Cpk)

**Versão:** 1.1 (todas as decisões de escopo validadas — pronta para orientar o desenvolvimento)
**Contexto:** Aplicativo web interno, rodando em servidor local da empresa, para cadastro de peças, coleta manual de medidas dimensionais, cálculo automático de Cp/Cpk e tratamento de Não Conformidades.

---

## 1. Visão Geral

O sistema permite:
1. Cadastrar peças e suas características dimensionais (cotas) com tolerâncias.
2. Coletar amostras de medição digitadas manualmente (paquímetro, micrômetro, etc.).
3. Calcular automaticamente Cp e Cpk por característica.
4. Visualizar histogramas, gráficos de controle e relatórios.
5. Rodar em rede local, acessível por PC (escritório) e tablet/celular (chão de fábrica).

---

## 2. Módulos e Telas

### 2.1 Módulo: Cadastro de Peças

**Tela: Lista de Peças**
- Campos exibidos: Código, Descrição, Cliente, Nº de características cadastradas, Status (ativa/inativa)
- Ações: Buscar por código/descrição, Filtrar por cliente, Novo cadastro, Editar, Inativar

**Tela: Cadastro/Edição de Peça**

| Campo | Tipo | Obrigatório | Observações |
|---|---|---|---|
| Código da peça | Texto (único) | Sim | Ex: 025451 |
| Descrição | Texto | Sim | Nome da peça |
| Cliente | Texto/seleção | Não | Se aplicável |
| Revisão do desenho | Texto | Sim | Ex: Rev. C |
| Observações | Texto longo | Não | |
| Status | Ativo/Inativo | Sim | Default: Ativo |

**Regras:**
- Código da peça deve ser único no sistema.
- Peça inativa não aparece na tela de Coleta, mas mantém histórico visível em Relatórios.
- Cada peça possui uma ou mais **Etapas de processo** (ver seção 2.2), e é dentro da etapa que ficam as características e a frequência de medição.

---

### 2.2 Módulo: Cadastro de Etapas e Características (Cotas)

Uma peça passa por várias **etapas de processo** (ex: etapa 10, etapa 20, etapa 30...), e cada etapa tem seu próprio conjunto de características (cotas) a medir e sua própria frequência de medição. Exemplo:

```
Peça 025451
 ├── Etapa 10 → cota 50, cota 25, cota 100
 ├── Etapa 20 → cota 14, cota 4
 └── Etapa 30 → cota 99
```

**Tela: Etapas da Peça** (acessada de dentro do cadastro da peça)

Lista as etapas já cadastradas para aquela peça, com opção de adicionar/editar/remover.

**Tela: Cadastro/Edição de Etapa**

| Campo | Tipo | Obrigatório | Observações |
|---|---|---|---|
| Nº da etapa | Numérico | Sim | Ex: 10, 20, 30 (segue a numeração do processo/roteiro de fabricação) |
| Descrição da etapa | Texto | Não | Ex: "Torneamento", "Fresamento" |
| Frequência de medição | Fração/proporção | Sim | Ex: 1/10 → mede 1 peça a cada 10 produzidas nesta etapa. Usada para calcular automaticamente a quantidade de amostras da rodada de coleta (ver seção 2.3). Armazenada como numerador/denominador para facilitar o cálculo: `amostras = ceil(quantidade_ordem × (numerador / denominador))` |
| Status | Ativo/Inativo | Sim | |

**Regras:**
- Nº da etapa deve ser único dentro da mesma peça.
- Cada etapa pode ter frequência de medição diferente das demais etapas da mesma peça.
- Frequência pode ser alterada a qualquer momento no cadastro da etapa; a alteração vale para as próximas rodadas de coleta (não recalcula rodadas já finalizadas).

**Tela: Características da Etapa** (acessada de dentro do cadastro da etapa)

Lista as características já cadastradas para aquela etapa (ex: cota 50, cota 25, cota 100 na etapa 10), com opção de adicionar/editar/remover.

**Tela: Cadastro/Edição de Característica**

| Campo | Tipo | Obrigatório | Observações |
|---|---|---|---|
| Nome da característica | Texto | Sim | Ex: "Diâmetro externo", "Comprimento total" |
| Nº do item no desenho (posição) | Texto/número | Não | Facilita rastreabilidade com o desenho |
| Valor nominal | Numérico (decimal) | Sim | |
| Tolerância superior (+) | Numérico (decimal) | Sim* | |
| Tolerância inferior (−) | Numérico (decimal) | Sim* | |
| LSE (limite superior calculado) | Numérico | Auto | nominal + tol. superior |
| LIE (limite inferior calculado) | Numérico | Auto | nominal − tol. inferior |
| Unidade de medida | Seleção | Sim | mm, cm, polegada |
| Instrumento recomendado | Seleção | Não | Paquímetro, Micrômetro, Relógio comparador, outro |
| Casas decimais de exibição | Número | Não | Default: 3 |
| Status | Ativo/Inativo | Sim | |

*Regra de tolerância: usuário pode informar tolerância simétrica (ex: ±0,05) ou assimétrica (ex: +0,10 / −0,02). Sistema calcula LSE/LIE automaticamente.

**Regras:**
- Não permitir LSE ≤ LIE.
- Não permitir cadastrar característica sem nominal e ao menos uma tolerância.
- Cada etapa pode ter N características (sem limite fixo).

---

### 2.3 Módulo: Coleta de Dados

**Tela: Nova Coleta**

Fluxo:
1. Operador informa o **código da peça** (busca por código).
2. Operador informa o **nº da Ordem de Produção**:
   - Se a ordem já existe no sistema (por já ter sido usada em outra etapa dessa peça), o sistema recupera automaticamente a quantidade cadastrada.
   - Se é uma ordem nova, o sistema pede a **quantidade de peças a produzir** (numérico, obrigatório) e salva essa informação vinculada ao nº da ordem.
3. Operador seleciona a **etapa** (ex: 10, 20, 30...) dentre as etapas cadastradas para aquela peça.
4. Sistema exibe automaticamente:
   - As características (cotas) daquela etapa (ex: etapa 10 → cota 50, cota 25, cota 100)
   - A frequência de medição definida para aquela etapa
5. Sistema **calcula automaticamente o número de amostras a coletar**:
   - Fórmula: `amostras = máximo(1, arredondar para cima(quantidade da ordem × frequência da etapa))`
   - Exemplo: ordem de 100 peças, etapa 10 com frequência 1/10 → **10 amostras**
   - Exemplo: mesma ordem de 100 peças, etapa 20 com frequência 1/20 → **5 amostras**
   - Exemplo: ordem pequena de 8 peças com frequência 1/10 → **1 amostra** (mínimo garantido; o sistema aceita rodadas com poucas amostras, mesmo sabendo que o Cp/Cpk não será estatisticamente robusto nesses casos)
   - O valor calculado é exibido para o operador antes de iniciar a coleta (ex: "Esta etapa terá 10 medições"), mas pode ser ajustado manualmente se necessário (com justificativa opcional em campo texto).
6. Operador informa: seu nome/login (registrado por amostra, ver regras abaixo) e data/hora (automático, mas editável).
7. Sistema apresenta grade de digitação, já com o número de linhas (amostras) definido pelo cálculo acima, e uma coluna para cada característica daquela etapa:

| Amostra nº | Cota 50 | Cota 25 | Cota 100 |
|---|---|---|---|
| 1 | ___ | ___ | ___ |
| 2 | ___ | ___ | ___ |
| ... | | | |

**Requisitos de UX (importante para digitação rápida em chão de fábrica):**
- Navegação entre campos via **Tab** ou **Enter** (sem precisar clicar no mouse/tocar na tela toda hora).
- Campo numérico com teclado numérico automático em tablets.
- Validação em tempo real: se o valor digitado estiver fora de LIE/LSE, destacar em vermelho (mas permitir salvar — é um dado real de medição, não deve ser bloqueado).
- Botão "Salvar rascunho" para continuar depois, e "Finalizar coleta" para fechar a rodada.
- Opção de excluir/corrigir uma amostra antes de finalizar.
- Se o operador tentar finalizar a rodada com menos amostras do que o número calculado, o sistema exibe um alerta e exige a seleção de um **motivo de encerramento antecipado** antes de permitir salvar (ex: "Ordem interrompida", "Ordem cancelada", "Quantidade produzida menor que o previsto", "**Não conformidade identificada no processo**", "Outro" com campo de texto livre).
- Quando o motivo selecionado for "Não conformidade identificada no processo" (ou quando uma medição individual ficar fora de LIE/LSE), o sistema exibe um botão **"Abrir RNC"** que leva à tela de abertura de Não Conformidade (seção 2.7), já pré-preenchida com peça, ordem, etapa e característica envolvida. A abertura da RNC continua sendo uma ação manual do usuário — o sistema apenas facilita o preenchimento, não cria a RNC sozinho.

**Regras:**
- Uma "rodada de coleta" agrupa todas as amostras medidas em um mesmo evento (peça + ordem + etapa), podendo ter **mais de um operador** contribuindo (ex: troca de turno).
- Status da rodada: **Em andamento** (ainda não atingiu o nº de amostras calculado) → **Finalizada** (atingiu o nº de amostras) → **Finalizada com pendência** (encerrada manualmente com menos amostras que o calculado, com motivo registrado).
- **Continuidade entre turnos/operadores:** se um operador iniciar uma coleta para uma combinação peça + ordem + etapa que já possui uma rodada "Em andamento" (aberta por outro operador), o sistema **não cria uma nova rodada** — ele entra na rodada existente, vê quantas amostras já foram medidas e quantas ainda faltam, e continua a digitação.
- Cada amostra registra individualmente **qual operador a mediu** (campo operador fica na Medição, não fixo na Rodada), preservando a rastreabilidade mesmo com múltiplos operadores na mesma rodada.
- Não é permitido duplicar rodada para a mesma combinação peça + ordem + etapa enquanto uma rodada estiver "Em andamento" ou já "Finalizada"/"Finalizada com pendência"; para refazer, é preciso reabri-la (permissão de Qualidade/Admin).
- Após finalizada, a rodada pode ser reaberta apenas por um usuário com permissão de "Qualidade/Admin" (rastreabilidade de alterações).
- Sistema deve manter histórico de todas as rodadas (por peça, ordem e etapa) ao longo do tempo, incluindo quais operadores participaram de cada uma e o motivo de encerramento antecipado, quando houver.
- Rodadas "Finalizada com pendência" ficam sinalizadas visualmente (ex: ícone de alerta) na tela de Análise Cp/Cpk (seção 2.4), já que possuem menos amostras que o planejado e o cálculo estatístico pode ficar menos confiável.

---

### 2.4 Módulo: Análise Cp/Cpk

**Tela: Análise por Peça**

1. Operador/analista seleciona a peça.
2. Seleciona a etapa (as características variam por etapa).
3. Seleciona a rodada de coleta (ou "todas as rodadas" / período de datas).
4. Sistema exibe, para cada característica daquela etapa:

| Característica | Nº amostras | Média (x̄) | Desvio padrão (σ) | LIE | LSE | Cp | Cpk | Status |
|---|---|---|---|---|---|---|---|---|
| Diâmetro externo | 30 | 25,012 | 0,015 | 24,95 | 25,05 | 1,55 | 1,42 | ✅ Capaz |

**Cálculos:**
- Cp = (LSE − LIE) / (6σ)
- Cpk = mín[ (LSE − x̄) / (3σ) ; (x̄ − LIE) / (3σ) ]
- σ: desvio padrão amostral (n−1)

**Classificação sugerida (parametrizável):**
| Cpk | Status |
|---|---|
| < 1,00 | 🔴 Não capaz |
| 1,00 – 1,33 | 🟡 Aceitável / atenção |
| > 1,33 | 🟢 Capaz |

**Visualizações:**
- Histograma da distribuição das amostras com curva normal sobreposta e linhas de LIE/LSE.
- **Carta de Controle X-barra e R** (confirmada para a V1):
  - Cada rodada de coleta finalizada é tratada como um subgrupo.
  - Gráfico X-barra: plota a média das amostras de cada rodada, ao longo do tempo (rodada a rodada), com Limite Superior de Controle (LSC) e Limite Inferior de Controle (LIC) calculados estatisticamente a partir do histórico de rodadas (não confundir com LSE/LIE, que são limites de especificação do desenho).
  - Gráfico R: plota a amplitude (máximo − mínimo) das amostras de cada rodada, com seus próprios limites de controle.
  - Útil para identificar tendências e causas especiais de variação ao longo do tempo, além da capabilidade pontual (Cp/Cpk).
- Indicador visual (semáforo) por característica.

**Regras:**
- O sistema **sempre calcula e exibe** o Cp/Cpk, mesmo com poucas amostras (conforme decidido na coleta — mínimo de 1 amostra é aceito).
- Quando o número de amostras estiver abaixo de um limiar configurável (sugestão: 20, ideal 30+), o sistema exibe um **aviso visual** (ex: "⚠ Baixo número de amostras — resultado pode não ser estatisticamente robusto"), mas não bloqueia a visualização do resultado.
- A Carta de Controle X-barra/R só é exibida quando houver pelo menos 2 rodadas de coleta finalizadas para a combinação peça+etapa+característica (para haver variação entre subgrupos a plotar).
- Deve ser possível filtrar análise por período, por operador, ou por rodada específica.

---

### 2.5 Módulo: Relatórios

- Exportar relatório de Cp/Cpk por peça (PDF), incluindo tabela + histogramas.
- Exportar dados brutos de coleta (Excel/CSV) por peça/período.
- Relatório consolidado: lista de todas as peças com seu Cpk mais recente (visão gerencial).
- Exportar RNC individual (PDF) com todo o histórico: abertura, análise, ação corretiva, verificação de eficácia.
- Relatório consolidado de Não Conformidades: quantidade por peça, por origem, por classificação, tempo médio de tratamento, taxa de reincidência (NCs reabertas).
- **Indicador de atenção**: lista de RNCs encerradas cujo Plano de Ação vinculado ainda está em aberto (ex: "peças com NC resolvida, mas causa raiz ainda em investigação") — exibido em destaque no painel de Não Conformidade.

---

### 2.6 Módulo: Usuários

**Equipe inicial prevista:** 3 Operadores, 1 Analista de Qualidade, 1 Gestor de Qualidade (número de usuários deve crescer — o cadastro de usuários não pode ter limite fixo).

| Perfil | Permissões |
|---|---|
| Operador | Realizar coletas, abrir RNC (sinalizar problema) |
| Analista de Qualidade | Cadastrar peças/etapas/características, ver análises (Cp/Cpk e Carta de Controle), reabrir rodadas, analisar e tratar RNC, conduzir investigação de causa raiz (Ishikawa/5 Porquês), cadastrar ações corretivas, **encerrar Plano de Ação** (verificação de eficácia) |
| Gestor de Qualidade | Tudo que o Analista de Qualidade faz, **+ encerrar Plano de Ação**, gestão de usuários, acesso a relatórios e indicadores consolidados |

**Regra:** a verificação de eficácia e o encerramento de um Plano de Ação podem ser feitos tanto pelo Analista de Qualidade quanto pelo Gestor de Qualidade.

---

### 2.7 Módulo: Não Conformidade (RNC)

Sistema de tratamento de peças/processos não conformes, seguindo um fluxo completo de investigação e ação corretiva (modelo CAPA, alinhado a ISO 9001). Abertura é sempre manual — feita pelo operador (ao identificar um problema) ou pela Qualidade.

**Fluxo de status da RNC:**

```
Aberta → Em análise → Em tratamento → Encerrada
```

A RNC em si trata do registro do problema e da **disposição da peça** (o que fazer com o material não conforme). A investigação de causa raiz e ação corretiva viram um **Plano de Ação separado**, aberto apenas quando necessário (ver abaixo).

**Tela: Abrir RNC** (operador ou Qualidade)

| Campo | Tipo | Obrigatório | Observações |
|---|---|---|---|
| Nº da RNC | Auto-gerado | Auto | Sequencial e **único para toda a empresa** (não reinicia por peça/setor), ex: RNC-2026-0001, RNC-2026-0002... |
| Peça | Seleção (busca por código) | **Sim** | |
| Ordem de produção | Seleção | Não | Se aplicável |
| Etapa | Seleção | Não | Se aplicável |
| Característica envolvida | Seleção | Não | Preenchido se a NC veio de uma medição fora de LIE/LSE |
| Rodada de coleta vinculada | Referência | Não | Preenchido automaticamente se aberta a partir de uma rodada (ver seção 2.3) |
| Descrição do problema | Texto longo | Sim | O que foi observado |
| Quantidade de peças afetadas | Numérico | Sim | |
| Classificação | Seleção | Sim | Crítica / Maior / Menor |
| Origem | Seleção | Sim | Processo, Matéria-prima, Projeto/Desenho, Instrumento de medição, Mão de obra, Outro |
| Evidência (foto/anexo) | Arquivo | Não | |
| Aberto por | Auto (usuário logado) | Auto | |
| Data de abertura | Auto | Auto | |

**Tela: Analisar e Tratar RNC** (Qualidade)

| Campo | Tipo | Obrigatório | Observações |
|---|---|---|---|
| Causa raiz (preliminar) | Texto longo | Não | Campo opcional — análise mais profunda fica a cargo do Plano de Ação, se aberto |
| Disposição da peça | Seleção | Sim | Retrabalho / Sucata / Uso como está (concessão) / Devolução ao fornecedor / Reclassificação |
| Responsável pela análise | Seleção (usuário) | Sim | |
| ☐ Necessário Plano de Ação | Checkbox | Sim | Se marcado, o sistema abre automaticamente um Plano de Ação vinculado a esta RNC (ver abaixo) |

**Regras da RNC:**
- Uma RNC **não pode existir** sem estar vinculada a uma peça específica (ordem e etapa são opcionais).
- É possível avançar do status "Em análise" para "Em tratamento" e até **encerrar a RNC** sem que haja causa raiz e ação corretiva preenchidas — desde que a disposição da peça esteja definida.
- Se o analista marcar o checkbox "Necessário Plano de Ação", o sistema cria um Plano de Ação vinculado, pré-preenchido com os dados da RNC (peça, ordem, etapa, descrição do problema).
- O encerramento da RNC é independente do andamento do Plano de Ação vinculado — a RNC trata da disposição imediata da peça, enquanto o Plano de Ação trata da causa raiz no seu próprio ritmo.
- Uma RNC pode ser aberta a partir da tela de Coleta (quando a rodada é encerrada por não conformidade ou uma medição fica fora de especificação) ou diretamente pelo menu de Não Conformidade, sem depender de uma coleta.
- Todo o histórico de mudança de status da RNC fica registrado (quem, quando, o quê), para auditoria.

**Tela: Lista de RNCs**
- Filtros: status, peça, período, classificação, origem, responsável, com/sem Plano de Ação vinculado.
- Indicadores no topo: RNCs abertas, em tratamento, encerradas no mês, RNCs com Plano de Ação ainda aberto, Planos de Ação com prazo de ação corretiva vencido.

---

### 2.8 Módulo: Plano de Ação (vinculado à RNC)

Aberto automaticamente quando o analista marca o checkbox "Necessário Plano de Ação" durante o tratamento de uma RNC. Concentra a investigação de causa raiz e a ação corretiva propriamente dita.

**Fluxo de status do Plano de Ação:**

```
Aberto → Em andamento → Aguardando verificação de eficácia → Encerrado
                                        │
                                        └──(se ação não foi eficaz)──→ Reaberto → volta para Em andamento
```

**Tela: Plano de Ação — Cabeçalho**

| Campo | Tipo | Obrigatório | Observações |
|---|---|---|---|
| RNC de origem | Referência | Auto | Pré-preenchido |
| Metodologia de investigação | Seleção | Sim | Ishikawa (Espinha de Peixe) / 5 Porquês / Nenhuma (análise livre em texto) |
| Conclusão da causa raiz | Texto longo | Sim (para avançar de status) | Resumo da causa raiz identificada, preenchido após a investigação pela metodologia escolhida |

Ao escolher a metodologia, o sistema abre um **formulário interativo específico** para conduzir a investigação:

**Formulário: Diagrama de Ishikawa (Espinha de Peixe)**
- Estrutura fixa dos 6M: **Método, Mão de obra, Máquina, Material, Meio Ambiente, Medição**.
- Para cada categoria (6M), o usuário pode adicionar uma ou mais causas possíveis (campo texto, lista dinâmica — "+ adicionar causa").
- Ao final, o usuário marca qual(is) causa(s) levantada(s) foi(ram) identificada(s) como a causa raiz real, e essa seleção alimenta o campo "Conclusão da causa raiz" do cabeçalho.

**Formulário: Técnica dos 5 Porquês**
- Sequência guiada: **Por quê (1)?** → resposta → **Por quê (2)?** (baseado na resposta anterior) → resposta → ... até o 5º "Por quê" (ou menos, se a causa raiz for identificada antes).
- Cada nível fica registrado (pergunta + resposta), formando a cadeia de raciocínio.
- Ao final, o usuário confirma qual resposta representa a causa raiz, preenchendo o campo "Conclusão da causa raiz" do cabeçalho.

**Formulário: Análise livre**
- Apenas um campo de texto longo para descrever a causa raiz, sem estrutura guiada (usado quando o problema é simples e não justifica uma investigação formal).

**Tela: Ações Corretivas** (lista dentro do Plano de Ação — pode haver várias)

| Campo | Tipo | Obrigatório | Observações |
|---|---|---|---|
| Descrição da ação | Texto longo | Sim | O que será feito |
| Responsável pela ação | Seleção (usuário) | Sim | Cada ação pode ter um responsável diferente |
| Prazo da ação | Data | Sim | |
| Data de execução | Data | Preenchido ao concluir | |
| Status da ação | Seleção | Auto | Pendente / Concluída / Atrasada (calculado automaticamente se prazo vencido e não concluída) |

Botão **"+ Adicionar ação"** permite incluir quantas ações forem necessárias no mesmo Plano de Ação.

**Tela: Verificar Eficácia do Plano de Ação** (Qualidade, após o prazo das ações corretivas)

| Campo | Tipo | Obrigatório | Observações |
|---|---|---|---|
| Data da verificação | Data | Sim | |
| Responsável | Seleção (usuário) | Sim | |
| Resultado | Seleção | Sim | Eficaz / Não eficaz |
| Observações | Texto longo | Não | |

**Regras do Plano de Ação:**
- Um Plano de Ação pode ter **uma ou mais ações corretivas**, cada uma com seu próprio responsável e prazo.
- Só é possível avançar o Plano de Ação para "Aguardando verificação de eficácia" quando **todas** as ações corretivas cadastradas estiverem com status "Concluída".
- Não há prazo padrão fixo definido pelo sistema para a verificação de eficácia — **quem está tratando o plano define o prazo** ao cadastrar cada ação corretiva, e a verificação ocorre quando esse prazo se aproxima ou vence.
- Não é possível encerrar um Plano de Ação sem verificação de eficácia com resultado "Eficaz".
- A verificação de eficácia e o encerramento do Plano de Ação podem ser feitos pelo **Analista de Qualidade ou pelo Gestor de Qualidade**.
- Se o resultado da verificação for "Não eficaz", o plano volta automaticamente para "Em andamento" (fica marcado como reaberto, mantendo histórico da tentativa anterior); as ações corretivas anteriores ficam no histórico, e podem ser adicionadas novas ações.
- **Troca de metodologia:** o usuário pode trocar a metodologia de investigação (Ishikawa ↔ 5 Porquês ↔ Análise livre) a qualquer momento, mesmo após já ter preenchido dados. Ao trocar, o sistema exibe um aviso de confirmação informando que os dados já preenchidos na metodologia anterior serão descartados da investigação ativa (ficam preservados apenas no histórico/auditoria, não na tela atual).
- Todo o histórico de mudança de status do Plano de Ação fica registrado (quem, quando, o quê), para auditoria.
- Uma RNC pode ter no máximo um Plano de Ação ativo por vez, mas pode acumular histórico de planos anteriores (se reaberto e depois encerrado novamente).

---

## 3. Modelo de Dados (resumo)

```
Peca
 - id, codigo (unico), descricao, cliente, desenho, revisao, material, status

Etapa
 - id, peca_id (FK), numero_etapa, descricao, freq_numerador, freq_denominador, status

Caracteristica
 - id, etapa_id (FK), nome, nominal, tol_superior, tol_inferior, 
   lse (calc), lie (calc), unidade, instrumento, casas_decimais, status

OrdemProducao
 - id, peca_id (FK), numero_ordem, quantidade

RodadaColeta
 - id, ordem_id (FK), etapa_id (FK), amostras_calculadas, 
   amostras_ajustadas (nullable), status (em_andamento/finalizada/finalizada_com_pendencia), 
   motivo_encerramento_antecipado (nullable), data_hora_inicio

Medicao
 - id, rodada_id (FK), caracteristica_id (FK), amostra_numero, valor, operador, data_hora

NaoConformidade
 - id, numero_rnc (auto, único), peca_id (FK), ordem_id (FK, nullable), 
   etapa_id (FK, nullable), caracteristica_id (FK, nullable), rodada_id (FK, nullable),
   descricao_problema, quantidade_afetada, classificacao (critica/maior/menor), 
   origem (processo/materia_prima/projeto/instrumento/mao_de_obra/outro),
   causa_raiz_preliminar (nullable), disposicao (retrabalho/sucata/uso_como_esta/devolucao_fornecedor/reclassificacao),
   responsavel_analise, necessita_plano_acao (boolean),
   aberto_por, data_abertura, status (aberta/em_analise/em_tratamento/encerrada)

PlanoDeAcao
 - id, nc_id (FK), metodologia_causa_raiz (ishikawa/cinco_porques/livre), 
   conclusao_causa_raiz, status (aberto/em_andamento/aguardando_verificacao/encerrado/reaberto)

AcaoCorretiva
 - id, plano_id (FK), descricao, responsavel, prazo, data_execucao, 
   status (pendente/concluida/atrasada)

CausaRaizIshikawa
 - id, plano_id (FK), categoria (metodo/mao_de_obra/maquina/material/meio_ambiente/medicao), 
   descricao_causa, marcada_como_raiz (boolean)

CausaRaiz5Porques
 - id, plano_id (FK), nivel (1 a 5), pergunta, resposta, marcada_como_raiz (boolean)

VerificacaoEficaciaPlano
 - id, plano_id (FK), data_verificacao, responsavel, resultado (eficaz/nao_eficaz), observacoes

HistoricoStatusNC
 - id, nc_id (FK, nullable), plano_id (FK, nullable), status_anterior, status_novo, usuario, data_hora
```

---

## 4. Requisitos Não Funcionais

- **Ambiente:** servidor local na rede da empresa (ex: `http://192.168.x.x`), acessível via navegador em PCs e tablets, sem depender de internet.
- **Responsivo:** interface adaptada para tela de tablet/celular (chão de fábrica) e desktop (escritório).
- **Backup:** rotina de backup do banco de dados (diário, automático).
- **Rastreabilidade:** log de alterações em cadastros e reabertura de coletas (quem, quando).
- **Performance:** telas de coleta devem responder rápido mesmo em rede Wi-Fi de fábrica.

---

## 5. Fora de escopo (V1)

- Integração com instrumentos digitais (USB/Bluetooth) — possível evolução futura.
- Múltiplas empresas/plantas (multi-tenant).
- App mobile nativo (fica web responsivo por enquanto).

---

## 6. Decisões Validadas

Todas as questões de escopo levantadas durante o planejamento foram validadas:

| # | Tema | Decisão |
|---|---|---|
| 1 | Quantidade da ordem entre etapas | Mesma quantidade para todas as etapas da ordem |
| 2 | Amostras mínimas | Mínimo de 1 amostra; sistema aceita rodadas com poucas amostras |
| 3 | Aprovação da rodada de coleta | Não é necessária aprovação/assinatura |
| 4 | Usuários iniciais | 3 Operadores, 1 Analista de Qualidade, 1 Gestor de Qualidade (crescendo) |
| 5 | Gráfico de controle | Incluído na V1: Carta de Controle X-barra e R |
| 6 | Numeração da RNC | Sequencial única para toda a empresa |
| 7 | Quem encerra o Plano de Ação | Analista de Qualidade e Gestor de Qualidade |
| 8 | Prazo de verificação de eficácia | Sem prazo padrão do sistema; definido por quem trata o plano |
| 9 | RNC encerrada com plano em aberto | Sim, deve haver indicador visual de atenção |
| 10 | Troca de metodologia de causa raiz | Permitida a qualquer momento, com aviso de que os dados da metodologia anterior serão descartados da tela ativa |

Com o escopo validado, o documento está pronto para orientar a fase de desenvolvimento do MVP.

## 7. Próximos Passos Sugeridos

1. Validar este documento uma última vez na íntegra (pode haver pequenos ajustes ao ver as telas funcionando).
2. Priorizar o MVP: sugestão de ordem — Cadastro de Peça/Etapa/Característica → Coleta de Dados → Cálculo Cp/Cpk → Módulo de Não Conformidade (RNC + Plano de Ação) → Carta de Controle → Relatórios.
3. Iniciar a modelagem do banco de dados e o desenvolvimento do backend (FastAPI + PostgreSQL, conforme sugerido).
