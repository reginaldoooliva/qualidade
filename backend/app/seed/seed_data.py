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
        ("Operador Um", "operador1", "senha123", Perfil.OPERADOR),
        ("Analista de Qualidade", "analista1", "senha123", Perfil.ANALISTA_QUALIDADE),
        ("Gestor de Qualidade", "gestor1", "senha123", Perfil.GESTOR_QUALIDADE),
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


def main() -> None:
    db = SessionLocal()
    try:
        seed_usuarios(db)
        seed_pecas(db)
        seed_coletas(db)
        seed_nao_conformidades(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
