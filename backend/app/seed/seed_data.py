"""Popula dados de teste idempotentes. Rodar com: python -m app.seed.seed_data"""

from datetime import date, timedelta

from app.core.permissions import Perfil
from app.core.security import hash_senha
from app.database import SessionLocal
from app.models.coleta import Medicao, MotivoEncerramento, RodadaColeta, StatusRodada
from app.models.nao_conformidade import ClassificacaoNC, OrigemNC
from app.models.peca import Caracteristica, Etapa, Peca, UnidadeMedida
from app.models.plano_acao import CategoriaIshikawa, MetodologiaCausaRaiz, ResultadoVerificacao
from app.models.producao import OrdemProducao
from app.models.usuario import Usuario
from app.repositories import (
    caracteristica_repository,
    etapa_repository,
    nao_conformidade_repository,
    peca_repository,
    producao_repository,
    tipo_instrumento_repository,
    usuario_repository,
)
from app.schemas.nao_conformidade import AbrirNCRequest, TratarNCRequest
from app.schemas.plano_acao import (
    AcaoCorretivaCreate,
    Causa5PorquesUpsert,
    CausaIshikawaCreate,
    VerificacaoEficaciaCreate,
)
from app.services import nao_conformidade_service, plano_acao_service


def seed_usuarios(db) -> None:
    usuarios = [
        ("Gestor de Qualidade", "gestor1", "senha123", Perfil.GESTOR_QUALIDADE),
        ("Analista de Qualidade", "analista1", "senha123", Perfil.ANALISTA_QUALIDADE),
        ("Inspetor Um", "inspetor1", "senha123", Perfil.INSPETOR),
        ("Operador Um", "operador1", "senha123", Perfil.OPERADOR),
    ]
    for nome, login, senha, perfil in usuarios:
        if usuario_repository.get_by_login(db, login):
            continue
        usuario_repository.create(
            db, Usuario(nome=nome, login=login, senha_hash=hash_senha(senha), perfil=perfil)
        )
        print(f"Usuário criado: {login} / senha123 ({perfil.value})")


def seed_pecas(db) -> None:
    if peca_repository.get_by_codigo(db, "025451"):
        print("Peças de exemplo já existem, pulando.")
        return

    peca1 = Peca(
        codigo="025451",
        descricao="Eixo de transmissão",
        cliente="Cliente Alfa",
        desenho="DES-025451",
        revisao="Rev. C",
        material="Aço 1045",
    )
    peca1.etapas = [
        Etapa(
            numero_etapa=10,
            descricao="Torneamento",
            freq_numerador=1,
            freq_denominador=10,
            caracteristicas=[
                Caracteristica(
                    nome="Diâmetro externo",
                    posicao_desenho="1",
                    nominal=25.000,
                    tol_superior=0.050,
                    tol_inferior=0.050,
                    unidade=UnidadeMedida.MM,
                    casas_decimais=3,
                ),
                Caracteristica(
                    nome="Comprimento total",
                    posicao_desenho="2",
                    nominal=100.00,
                    tol_superior=0.100,
                    tol_inferior=0.020,
                    unidade=UnidadeMedida.MM,
                    casas_decimais=2,
                ),
            ],
        ),
        Etapa(
            numero_etapa=20,
            descricao="Fresamento",
            freq_numerador=1,
            freq_denominador=20,
            caracteristicas=[
                Caracteristica(
                    nome="Largura do rasgo",
                    posicao_desenho="3",
                    nominal=14.000,
                    tol_superior=0.030,
                    tol_inferior=0.030,
                    unidade=UnidadeMedida.MM,
                    casas_decimais=3,
                ),
            ],
        ),
    ]

    peca2 = Peca(
        codigo="030112",
        descricao="Flange de vedação",
        cliente="Cliente Beta",
        desenho="DES-030112",
        revisao="Rev. A",
        material="Alumínio 6061",
    )
    peca2.etapas = [
        Etapa(
            numero_etapa=10,
            descricao="Usinagem CNC",
            freq_numerador=1,
            freq_denominador=5,
            caracteristicas=[
                Caracteristica(
                    nome="Diâmetro do furo central",
                    posicao_desenho="1",
                    nominal=50.000,
                    tol_superior=0.020,
                    tol_inferior=0.000,
                    unidade=UnidadeMedida.MM,
                    casas_decimais=3,
                ),
            ],
        ),
    ]

    for peca in (peca1, peca2):
        peca_repository.create(db, peca)
        print(f"Peça criada: {peca.codigo} — {peca.descricao}")


def seed_coletas(db) -> None:
    peca = peca_repository.get_by_codigo(db, "025451")
    etapa10 = etapa_repository.get_by_peca_e_numero(db, peca.id, 10)
    caracteristicas = caracteristica_repository.list_by_etapa(db, etapa10.id)
    diametro = next(c for c in caracteristicas if c.nome == "Diâmetro externo")
    comprimento = next(c for c in caracteristicas if c.nome == "Comprimento total")
    operador = usuario_repository.get_by_login(db, "operador1")

    if producao_repository.get_by_peca_e_numero(db, peca.id, "OP-1001"):
        print("Rodadas de coleta de exemplo já existem, pulando.")
        return

    # Rodada em andamento (10 amostras calculadas, só 4 preenchidas) — testa continuidade de rodada.
    ordem1 = producao_repository.create(db, OrdemProducao(peca_id=peca.id, numero_ordem="OP-1001", quantidade=100))
    rodada_em_andamento = RodadaColeta(
        ordem_id=ordem1.id, etapa_id=etapa10.id, amostras_calculadas=10, status=StatusRodada.EM_ANDAMENTO
    )
    db.add(rodada_em_andamento)
    db.flush()
    for amostra, (valor_d, valor_c) in enumerate([(25.01, 100.02), (24.98, 99.99), (25.02, 100.01), (25.00, 100.00)], start=1):
        db.add(Medicao(rodada_id=rodada_em_andamento.id, caracteristica_id=diametro.id, amostra_numero=amostra, valor=valor_d, operador_id=operador.id))
        db.add(Medicao(rodada_id=rodada_em_andamento.id, caracteristica_id=comprimento.id, amostra_numero=amostra, valor=valor_c, operador_id=operador.id))
    db.commit()
    print("Rodada em andamento criada (OP-1001, etapa 10, 4/10 amostras).")

    # Rodada finalizada (5 amostras) com um valor propositalmente fora de LSE — testa destaque vermelho e sugestão de RNC.
    ordem2 = producao_repository.create(db, OrdemProducao(peca_id=peca.id, numero_ordem="OP-1002", quantidade=50))
    rodada_finalizada = RodadaColeta(
        ordem_id=ordem2.id, etapa_id=etapa10.id, amostras_calculadas=5, status=StatusRodada.FINALIZADA
    )
    db.add(rodada_finalizada)
    db.flush()
    valores_diametro = [25.00, 24.99, 25.08, 25.01, 24.97]  # 25.08 > LSE 25.05
    valores_comprimento = [100.01, 99.99, 100.02, 100.00, 99.98]
    for amostra, (valor_d, valor_c) in enumerate(zip(valores_diametro, valores_comprimento), start=1):
        db.add(Medicao(rodada_id=rodada_finalizada.id, caracteristica_id=diametro.id, amostra_numero=amostra, valor=valor_d, operador_id=operador.id))
        db.add(Medicao(rodada_id=rodada_finalizada.id, caracteristica_id=comprimento.id, amostra_numero=amostra, valor=valor_c, operador_id=operador.id))
    db.commit()
    print("Rodada finalizada criada (OP-1002, etapa 10, 5/5 amostras, 1 fora de especificação).")

    # Rodada finalizada com pendência (10 calculadas, só 6 preenchidas, encerrada por interrupção).
    ordem3 = producao_repository.create(db, OrdemProducao(peca_id=peca.id, numero_ordem="OP-1003", quantidade=100))
    rodada_pendencia = RodadaColeta(
        ordem_id=ordem3.id,
        etapa_id=etapa10.id,
        amostras_calculadas=10,
        status=StatusRodada.FINALIZADA_COM_PENDENCIA,
        motivo_encerramento_antecipado=MotivoEncerramento.ORDEM_INTERROMPIDA,
    )
    db.add(rodada_pendencia)
    db.flush()
    for amostra in range(1, 7):
        db.add(Medicao(rodada_id=rodada_pendencia.id, caracteristica_id=diametro.id, amostra_numero=amostra, valor=25.0, operador_id=operador.id))
        db.add(Medicao(rodada_id=rodada_pendencia.id, caracteristica_id=comprimento.id, amostra_numero=amostra, valor=100.0, operador_id=operador.id))
    db.commit()
    print("Rodada finalizada com pendência criada (OP-1003, etapa 10, 6/10 amostras).")


def seed_nao_conformidades(db) -> None:
    if nao_conformidade_repository.get_ultimo_numero_do_ano(db, f"RNC-{date.today().year}-"):
        print("RNCs de exemplo já existem, pulando.")
        return

    peca1 = peca_repository.get_by_codigo(db, "025451")
    peca2 = peca_repository.get_by_codigo(db, "030112")
    etapa10_peca1 = etapa_repository.get_by_peca_e_numero(db, peca1.id, 10)
    diametro = next(
        c for c in caracteristica_repository.list_by_etapa(db, etapa10_peca1.id) if c.nome == "Diâmetro externo"
    )
    ordem_op1002 = producao_repository.get_by_peca_e_numero(db, peca1.id, "OP-1002")
    operador = usuario_repository.get_by_login(db, "operador1")
    analista = usuario_repository.get_by_login(db, "analista1")
    gestor = usuario_repository.get_by_login(db, "gestor1")

    # RNC 1 — recém-aberta pelo operador a partir da medição fora de LSE da OP-1002, ainda sem tratamento.
    nc1 = nao_conformidade_service.abrir(
        db,
        AbrirNCRequest(
            peca_id=peca1.id,
            ordem_id=ordem_op1002.id,
            etapa_id=etapa10_peca1.id,
            caracteristica_id=diametro.id,
            descricao_problema="Diâmetro externo medido em 25.08mm, acima do LSE (25.05mm).",
            quantidade_afetada=1,
            classificacao=ClassificacaoNC.MENOR,
            origem=OrigemNC.PROCESSO,
        ),
        operador,
    )
    print(f"RNC criada: {nc1.numero_rnc} (aberta)")

    # RNC 2 — em tratamento, com Plano de Ação (Ishikawa) já aguardando verificação de eficácia,
    # e a própria RNC encerrada — demonstra o indicador "RNC encerrada com plano ainda em aberto".
    nc2 = nao_conformidade_service.abrir(
        db,
        AbrirNCRequest(
            peca_id=peca2.id,
            descricao_problema="Furo central com rebarba excessiva identificada na inspeção final.",
            quantidade_afetada=8,
            classificacao=ClassificacaoNC.MAIOR,
            origem=OrigemNC.PROCESSO,
        ),
        operador,
    )
    nc2 = nao_conformidade_service.tratar(
        db,
        nc2.id,
        TratarNCRequest(
            causa_raiz_preliminar="Possível desgaste de ferramenta de corte.",
            disposicao="retrabalho",
            responsavel_analise_id=analista.id,
            necessita_plano_acao=True,
        ),
        analista,
    )
    plano2 = nc2.plano_acao_ativo
    plano_acao_service.trocar_metodologia(db, plano2.id, MetodologiaCausaRaiz.ISHIKAWA, analista)
    causa2 = plano_acao_service.adicionar_causa_ishikawa(
        db,
        plano2.id,
        CausaIshikawaCreate(categoria=CategoriaIshikawa.MAQUINA, descricao_causa="Ferramenta de corte desgastada"),
        analista,
    )
    plano_acao_service.adicionar_causa_ishikawa(
        db,
        plano2.id,
        CausaIshikawaCreate(categoria=CategoriaIshikawa.METODO, descricao_causa="Frequência de troca não definida"),
        analista,
    )
    plano_acao_service.marcar_causa_ishikawa(db, plano2.id, causa2.id, True, analista)
    plano_acao_service.adicionar_acao(
        db,
        plano2.id,
        AcaoCorretivaCreate(
            descricao="Definir plano de troca preventiva da ferramenta de corte",
            responsavel_id=analista.id,
            prazo=date.today() + timedelta(days=15),
        ),
        analista,
    )
    plano2 = plano_acao_service.obter(db, plano2.id)
    plano_acao_service.concluir_acao(db, plano2.id, plano2.acoes_corretivas[0].id, analista)
    plano_acao_service.avancar_verificacao(db, plano2.id, analista)
    nao_conformidade_service.encerrar(db, nc2.id, analista)
    print(f"RNC criada: {nc2.numero_rnc} (encerrada, plano de ação ainda aguardando verificação)")

    # RNC 3 — ciclo completo: 5 Porquês, ação concluída, verificação eficaz, plano e RNC encerrados.
    nc3 = nao_conformidade_service.abrir(
        db,
        AbrirNCRequest(
            peca_id=peca1.id,
            descricao_problema="Lote com variação dimensional acima do esperado na etapa de torneamento.",
            quantidade_afetada=3,
            classificacao=ClassificacaoNC.MAIOR,
            origem=OrigemNC.PROCESSO,
        ),
        operador,
    )
    nc3 = nao_conformidade_service.tratar(
        db,
        nc3.id,
        TratarNCRequest(
            disposicao="uso_como_esta",
            responsavel_analise_id=gestor.id,
            necessita_plano_acao=True,
        ),
        gestor,
    )
    plano3 = nc3.plano_acao_ativo
    plano_acao_service.trocar_metodologia(db, plano3.id, MetodologiaCausaRaiz.CINCO_PORQUES, gestor)
    causa3 = plano_acao_service.upsert_causa_5porques(
        db,
        plano3.id,
        Causa5PorquesUpsert(
            nivel=1, pergunta="Por que houve variação dimensional?", resposta="O torno estava descalibrado"
        ),
        gestor,
    )
    plano_acao_service.marcar_causa_5porques(db, plano3.id, causa3.id, True, gestor)
    plano_acao_service.adicionar_acao(
        db,
        plano3.id,
        AcaoCorretivaCreate(
            descricao="Recalibrar torno e incluir na rotina semanal de calibração",
            responsavel_id=gestor.id,
            prazo=date.today() + timedelta(days=7),
        ),
        gestor,
    )
    plano3 = plano_acao_service.obter(db, plano3.id)
    plano_acao_service.concluir_acao(db, plano3.id, plano3.acoes_corretivas[0].id, gestor)
    plano_acao_service.avancar_verificacao(db, plano3.id, gestor)
    plano_acao_service.registrar_verificacao(
        db,
        plano3.id,
        VerificacaoEficaciaCreate(
            data_verificacao=date.today(), responsavel_id=gestor.id, resultado=ResultadoVerificacao.EFICAZ
        ),
        gestor,
    )
    nao_conformidade_service.encerrar(db, nc3.id, gestor)
    print(f"RNC criada: {nc3.numero_rnc} (encerrada, plano de ação encerrado — eficaz)")


def seed_pecas_extra(db) -> None:
    if peca_repository.get_by_codigo(db, "041233"):
        print("Peças extras já existem, pulando.")
        return

    def tipo_instrumento_id(nome: str) -> int | None:
        tipo = tipo_instrumento_repository.get_by_nome(db, nome)
        return tipo.id if tipo else None

    peca3 = Peca(
        codigo="041233",
        descricao="Suporte de motor",
        cliente="Cliente Gamma",
        desenho="DES-041233",
        revisao="Rev. B",
        material="Ferro fundido GG25",
    )
    peca3.etapas = [
        Etapa(
            numero_etapa=10,
            descricao="Fresamento CNC",
            freq_numerador=1,
            freq_denominador=8,
            caracteristicas=[
                Caracteristica(
                    nome="Diâmetro do rasgo",
                    posicao_desenho="1",
                    nominal=1.250,
                    tol_superior=0.005,
                    tol_inferior=0.005,
                    unidade=UnidadeMedida.POLEGADA,
                    tipo_instrumento_id=tipo_instrumento_id("Micrômetro"),
                    casas_decimais=3,
                ),
                Caracteristica(
                    nome="Furo de fixação",
                    posicao_desenho="2",
                    nominal=8.000,
                    tol_superior=0.020,
                    tol_inferior=0.000,
                    unidade=UnidadeMedida.MM,
                    tipo_instrumento_id=tipo_instrumento_id("Relógio comparador"),
                    casas_decimais=3,
                ),
            ],
        ),
    ]

    peca4 = Peca(
        codigo="052890",
        descricao="Bucha de bronze",
        cliente="Cliente Alfa",
        desenho="DES-052890",
        revisao="Rev. A",
        material="Bronze SAE 40",
    )
    peca4.etapas = [
        Etapa(
            numero_etapa=10,
            descricao="Torneamento de acabamento",
            freq_numerador=1,
            freq_denominador=4,
            caracteristicas=[
                Caracteristica(
                    nome="Diâmetro interno",
                    posicao_desenho="1",
                    nominal=30.000,
                    tol_superior=0.010,
                    tol_inferior=0.010,
                    unidade=UnidadeMedida.MM,
                    tipo_instrumento_id=tipo_instrumento_id("Micrômetro"),
                    casas_decimais=3,
                ),
            ],
        ),
    ]

    peca5 = Peca(
        codigo="060144",
        descricao="Tampa de válvula",
        cliente="Cliente Delta",
        desenho="DES-060144",
        revisao="Rev. D",
        material="Aço inox 304",
    )
    peca5.etapas = [
        Etapa(
            numero_etapa=10,
            descricao="Estampagem",
            freq_numerador=1,
            freq_denominador=6,
            caracteristicas=[
                Caracteristica(
                    nome="Espessura",
                    posicao_desenho="1",
                    nominal=2.000,
                    tol_superior=0.050,
                    tol_inferior=0.050,
                    unidade=UnidadeMedida.MM,
                    tipo_instrumento_id=tipo_instrumento_id("Paquímetro"),
                    casas_decimais=3,
                ),
            ],
        ),
    ]

    for peca in (peca3, peca4, peca5):
        peca_repository.create(db, peca)
        print(f"Peça criada: {peca.codigo} — {peca.descricao}")


def seed_coletas_extra(db) -> None:
    operador = usuario_repository.get_by_login(db, "operador1")

    def _criar_rodadas_finalizadas(codigo_peca: str, ordem_prefixo: str, quantidade: int, grupos_valores: list[list[float]]) -> None:
        peca = peca_repository.get_by_codigo(db, codigo_peca)
        etapa = etapa_repository.get_by_peca_e_numero(db, peca.id, 10)
        caracteristica = caracteristica_repository.list_by_etapa(db, etapa.id)[0]
        for i, valores in enumerate(grupos_valores, start=1):
            numero_ordem = f"{ordem_prefixo}-{1000 + i}"
            if producao_repository.get_by_peca_e_numero(db, peca.id, numero_ordem):
                continue
            ordem = producao_repository.create(
                db, OrdemProducao(peca_id=peca.id, numero_ordem=numero_ordem, quantidade=quantidade)
            )
            rodada = RodadaColeta(
                ordem_id=ordem.id, etapa_id=etapa.id, amostras_calculadas=len(valores), status=StatusRodada.FINALIZADA
            )
            db.add(rodada)
            db.flush()
            for amostra, valor in enumerate(valores, start=1):
                db.add(
                    Medicao(
                        rodada_id=rodada.id,
                        caracteristica_id=caracteristica.id,
                        amostra_numero=amostra,
                        valor=valor,
                        operador_id=operador.id,
                    )
                )
            db.commit()
        print(f"Rodadas finalizadas criadas para {codigo_peca} ({len(grupos_valores)} subgrupos).")

    if not producao_repository.get_by_peca_e_numero(
        db, peca_repository.get_by_codigo(db, "052890").id, "BRONZE-1001"
    ):
        _criar_rodadas_finalizadas(
            "052890",
            "BRONZE",
            25,
            [
                [30.000, 29.999, 30.001, 30.000],
                [30.001, 29.999, 30.000, 29.998],
                [30.002, 30.000, 29.999, 30.001],
            ],
        )

    if not producao_repository.get_by_peca_e_numero(
        db, peca_repository.get_by_codigo(db, "060144").id, "TAMPA-1001"
    ):
        _criar_rodadas_finalizadas(
            "060144",
            "TAMPA",
            60,
            [
                [2.000, 1.978, 2.022, 1.988],
                [2.012, 1.982, 2.018, 1.998],
                [1.985, 2.015, 1.995, 2.005],
            ],
        )


def seed_nao_conformidades_extra(db) -> None:
    peca_suporte = peca_repository.get_by_codigo(db, "041233")
    if nao_conformidade_repository.list_nc(db, peca_id=peca_suporte.id):
        print("RNCs extras já existem, pulando.")
        return

    peca_tampa = peca_repository.get_by_codigo(db, "060144")
    peca_bucha = peca_repository.get_by_codigo(db, "052890")
    peca_eixo = peca_repository.get_by_codigo(db, "025451")
    operador = usuario_repository.get_by_login(db, "operador1")
    analista = usuario_repository.get_by_login(db, "analista1")
    gestor = usuario_repository.get_by_login(db, "gestor1")

    # RNC 4 — crítica, tratada só com causa preliminar (sem disposição ainda) -> fica em_analise.
    nc4 = nao_conformidade_service.abrir(
        db,
        AbrirNCRequest(
            peca_id=peca_tampa.id,
            descricao_problema="Lote de matéria-prima com certificado de composição química divergente.",
            quantidade_afetada=60,
            classificacao=ClassificacaoNC.CRITICA,
            origem=OrigemNC.MATERIA_PRIMA,
        ),
        operador,
    )
    nao_conformidade_service.tratar(
        db,
        nc4.id,
        TratarNCRequest(
            causa_raiz_preliminar="Aguardando laudo do fornecedor de matéria-prima.",
            responsavel_analise_id=analista.id,
            necessita_plano_acao=False,
        ),
        analista,
    )
    print(f"RNC criada: {nc4.numero_rnc} (em análise, aguardando laudo)")

    # RNC 5 — plano de ação com ciclo de reabertura: 1ª verificação não eficaz, 2ª eficaz.
    nc5 = nao_conformidade_service.abrir(
        db,
        AbrirNCRequest(
            peca_id=peca_suporte.id,
            descricao_problema="Furo de fixação fora de posição em lote de suportes de motor.",
            quantidade_afetada=12,
            classificacao=ClassificacaoNC.MAIOR,
            origem=OrigemNC.MAO_DE_OBRA,
        ),
        operador,
    )
    nc5 = nao_conformidade_service.tratar(
        db,
        nc5.id,
        TratarNCRequest(
            disposicao="sucata",
            responsavel_analise_id=analista.id,
            necessita_plano_acao=True,
        ),
        analista,
    )
    plano5 = nc5.plano_acao_ativo
    plano_acao_service.atualizar_conclusao(
        db, plano5.id, "Operador não seguiu o gabarito de fixação durante a furação manual.", analista
    )
    plano_acao_service.adicionar_acao(
        db,
        plano5.id,
        AcaoCorretivaCreate(
            descricao="Reforçar treinamento de uso do gabarito de furação",
            responsavel_id=analista.id,
            prazo=date.today() + timedelta(days=10),
        ),
        analista,
    )
    plano5 = plano_acao_service.obter(db, plano5.id)
    plano_acao_service.concluir_acao(db, plano5.id, plano5.acoes_corretivas[0].id, analista)
    plano_acao_service.avancar_verificacao(db, plano5.id, analista)
    plano_acao_service.registrar_verificacao(
        db,
        plano5.id,
        VerificacaoEficaciaCreate(
            data_verificacao=date.today(), responsavel_id=analista.id, resultado=ResultadoVerificacao.NAO_EFICAZ
        ),
        analista,
    )
    # Não eficaz -> plano reabre automaticamente (ciclo 2); adiciona nova ação e fecha com sucesso.
    plano_acao_service.adicionar_acao(
        db,
        plano5.id,
        AcaoCorretivaCreate(
            descricao="Instalar gabarito fixo na máquina, eliminando dependência do operador",
            responsavel_id=analista.id,
            prazo=date.today() + timedelta(days=20),
        ),
        analista,
    )
    plano5 = plano_acao_service.obter(db, plano5.id)
    plano_acao_service.concluir_acao(db, plano5.id, plano5.acoes_corretivas[1].id, analista)
    plano_acao_service.avancar_verificacao(db, plano5.id, analista)
    plano_acao_service.registrar_verificacao(
        db,
        plano5.id,
        VerificacaoEficaciaCreate(
            data_verificacao=date.today() + timedelta(days=25),
            responsavel_id=analista.id,
            resultado=ResultadoVerificacao.EFICAZ,
        ),
        analista,
    )
    nao_conformidade_service.encerrar(db, nc5.id, analista)
    print(f"RNC criada: {nc5.numero_rnc} (encerrada, plano com ciclo de reabertura — 1ª não eficaz, 2ª eficaz)")

    # RNC 6 — encerrada direto, sem plano de ação (só disposição definida).
    nc6 = nao_conformidade_service.abrir(
        db,
        AbrirNCRequest(
            peca_id=peca_bucha.id,
            descricao_problema="Instrumento de medição fora da calibração identificado na auditoria interna.",
            quantidade_afetada=25,
            classificacao=ClassificacaoNC.MENOR,
            origem=OrigemNC.INSTRUMENTO,
        ),
        operador,
    )
    nao_conformidade_service.tratar(
        db,
        nc6.id,
        TratarNCRequest(disposicao="devolucao_fornecedor", responsavel_analise_id=analista.id, necessita_plano_acao=False),
        analista,
    )
    nao_conformidade_service.encerrar(db, nc6.id, analista)
    print(f"RNC criada: {nc6.numero_rnc} (encerrada sem plano de ação)")

    # RNC 7 — recém-aberta, ainda sem nenhum tratamento.
    nc7 = nao_conformidade_service.abrir(
        db,
        AbrirNCRequest(
            peca_id=peca_eixo.id,
            descricao_problema="Desenho revisado pelo cliente após início da produção do lote.",
            quantidade_afetada=40,
            classificacao=ClassificacaoNC.CRITICA,
            origem=OrigemNC.PROJETO,
        ),
        gestor,
    )
    print(f"RNC criada: {nc7.numero_rnc} (aberta, sem tratamento)")


def main() -> None:
    db = SessionLocal()
    try:
        seed_usuarios(db)
        seed_pecas(db)
        seed_coletas(db)
        seed_nao_conformidades(db)
        seed_pecas_extra(db)
        seed_coletas_extra(db)
        seed_nao_conformidades_extra(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
