from datetime import datetime
from io import BytesIO

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

COR_PRIMARIA = colors.HexColor("#2a78d6")
COR_LIMITE = colors.HexColor("#d03b3b")
COR_NOMINAL = colors.HexColor("#898781")
COR_HEADER_TABELA = colors.HexColor("#1f2937")

_stylesheet = getSampleStyleSheet()
ESTILO_TITULO = ParagraphStyle("TituloRelatorio", parent=_stylesheet["Title"], fontSize=16, spaceAfter=4)
ESTILO_SUBTITULO = ParagraphStyle("Subtitulo", parent=_stylesheet["Heading2"], fontSize=12, spaceBefore=10, spaceAfter=4)
ESTILO_SECAO = ParagraphStyle("Secao", parent=_stylesheet["Heading3"], fontSize=10.5, spaceBefore=8, spaceAfter=2)
ESTILO_CORPO = ParagraphStyle("Corpo", parent=_stylesheet["Normal"], fontSize=9)
ESTILO_MUTED = ParagraphStyle("Muted", parent=_stylesheet["Normal"], fontSize=8, textColor=colors.grey)


def _cabecalho_documento() -> list:
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    return [Paragraph(f"Gerado em {agora} — Sistema de Qualidade", ESTILO_MUTED), Spacer(1, 6)]


def _novo_documento(buffer: BytesIO) -> SimpleDocTemplate:
    return SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
    )


def _tabela(dados: list[list[str]], larguras: list[float] | None = None) -> Table:
    tabela = Table(dados, colWidths=larguras, repeatRows=1)
    tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), COR_HEADER_TABELA),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f7f5")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return tabela


def gerar_histograma_png(
    valores: list[float], lie: float, lse: float, nominal: float, titulo: str
) -> bytes | None:
    if len(valores) < 2:
        return None

    fig = Figure(figsize=(5.2, 2.4), dpi=130)
    ax = fig.add_subplot(111)

    minimo = min(min(valores), lie)
    maximo = max(max(valores), lse)
    largura = (maximo - minimo) / 10 or 1
    bins = [minimo + i * largura for i in range(11)]
    ax.hist(valores, bins=bins, color="#2a78d6", edgecolor="white", linewidth=0.5)

    ax.axvline(lie, color="#d03b3b", linestyle="--", linewidth=1)
    ax.axvline(lse, color="#d03b3b", linestyle="--", linewidth=1)
    ax.axvline(nominal, color="#898781", linestyle="-", linewidth=1)
    ax.set_title(titulo, fontsize=9)
    ax.tick_params(labelsize=7)
    ax.ticklabel_format(useOffset=False, style="plain", axis="x")
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()

    buffer = BytesIO()
    FigureCanvasAgg(fig).print_png(buffer)
    return buffer.getvalue()


def gerar_pdf_cpk_peca(peca: dict, etapas: list[dict], filtro_texto: str | None) -> bytes:
    buffer = BytesIO()
    doc = _novo_documento(buffer)
    elementos: list = [
        Paragraph("Relatório de Capabilidade (Cp/Cpk)", ESTILO_TITULO),
        Paragraph(f"{peca['codigo']} — {peca['descricao']}", ESTILO_SUBTITULO),
    ]
    if filtro_texto:
        elementos.append(Paragraph(filtro_texto, ESTILO_MUTED))
    elementos += _cabecalho_documento()

    for etapa in etapas:
        elementos.append(Paragraph(f"Etapa {etapa['numero_etapa']} — {etapa['descricao'] or ''}", ESTILO_SECAO))
        if not etapa["caracteristicas"]:
            elementos.append(Paragraph("Nenhuma característica cadastrada.", ESTILO_CORPO))
            continue

        for c in etapa["caracteristicas"]:
            cabecalho = [["N", "Média", "Desvio", "LIE", "LSE", "Cp", "Cpk", "Status"]]
            linha = [
                str(c["n_amostras"]),
                _fmt(c["media"], c["casas_decimais"]),
                _fmt(c["desvio_padrao"], c["casas_decimais"]),
                _fmt(c["lie"], c["casas_decimais"]),
                _fmt(c["lse"], c["casas_decimais"]),
                _fmt(c["cp"], 2),
                _fmt(c["cpk"], 2),
                _CLASSIFICACAO_LABEL.get(c["classificacao"], "—"),
            ]
            elementos.append(Paragraph(c["nome"], ESTILO_CORPO))
            elementos.append(_tabela(cabecalho + [linha]))
            if c["baixa_robustez"]:
                elementos.append(Paragraph("⚠ Baixo número de amostras — resultado pode não ser robusto.", ESTILO_MUTED))

            png = gerar_histograma_png(c["valores"], c["lie"], c["lse"], c["nominal"], "Distribuição das amostras")
            if png:
                elementos.append(Image(BytesIO(png), width=13 * cm, height=6 * cm))
            elementos.append(Spacer(1, 8))

    doc.build(elementos)
    return buffer.getvalue()


_CLASSIFICACAO_LABEL = {"capaz": "Capaz", "atencao": "Atenção", "nao_capaz": "Não capaz", None: "—"}


def _fmt(valor: float | None, casas: int) -> str:
    return f"{valor:.{casas}f}" if valor is not None else "—"


def gerar_pdf_rnc(nc: dict, planos: list[dict]) -> bytes:
    buffer = BytesIO()
    doc = _novo_documento(buffer)
    elementos: list = [
        Paragraph(f"RNC {nc['numero_rnc']}", ESTILO_TITULO),
        Paragraph(f"{nc['peca_codigo']} — {nc['peca_descricao']}", ESTILO_SUBTITULO),
    ]
    elementos += _cabecalho_documento()

    elementos.append(Paragraph("Abertura", ESTILO_SECAO))
    elementos.append(Paragraph(nc["descricao_problema"], ESTILO_CORPO))
    elementos.append(
        _tabela(
            [
                ["Quantidade afetada", "Classificação", "Origem", "Status", "Aberta por", "Data de abertura"],
                [
                    str(nc["quantidade_afetada"]),
                    nc["classificacao"],
                    nc["origem"],
                    nc["status"],
                    nc["aberto_por_nome"],
                    nc["data_abertura"],
                ],
            ]
        )
    )

    elementos.append(Paragraph("Análise e tratamento", ESTILO_SECAO))
    elementos.append(
        Paragraph(
            f"Causa raiz preliminar: {nc['causa_raiz_preliminar'] or '—'}<br/>"
            f"Disposição da peça: {nc['disposicao'] or '—'}",
            ESTILO_CORPO,
        )
    )

    for plano in planos:
        elementos.append(Paragraph(f"Plano de Ação #{plano['id']} (ciclo {plano['ciclo']}) — {plano['status']}", ESTILO_SECAO))
        elementos.append(
            Paragraph(
                f"Metodologia: {plano['metodologia_causa_raiz']}<br/>"
                f"Conclusão da causa raiz: {plano['conclusao_causa_raiz'] or '—'}",
                ESTILO_CORPO,
            )
        )
        if plano["acoes_corretivas"]:
            linhas = [["Descrição", "Responsável", "Prazo", "Status"]]
            for a in plano["acoes_corretivas"]:
                linhas.append([a["descricao"], a["responsavel_nome"], a["prazo"], a["status"]])
            elementos.append(_tabela(linhas))
        if plano["verificacoes"]:
            linhas = [["Data", "Responsável", "Resultado", "Observações"]]
            for v in plano["verificacoes"]:
                linhas.append([v["data_verificacao"], v["responsavel_nome"], v["resultado"], v["observacoes"] or "—"])
            elementos.append(_tabela(linhas))
        elementos.append(Spacer(1, 6))

    elementos.append(Paragraph("Histórico", ESTILO_SECAO))
    linhas = [["Data/hora", "Usuário", "Evento"]]
    for evento in nc["historico"]:
        linhas.append([evento["criado_em"], evento["usuario_nome"], evento["detalhe"] or evento["acao"]])
    elementos.append(_tabela(linhas, larguras=[3.5 * cm, 3.5 * cm, 10 * cm]))

    doc.build(elementos)
    return buffer.getvalue()


def gerar_pdf_consolidado_pecas(itens: list[dict]) -> bytes:
    buffer = BytesIO()
    doc = _novo_documento(buffer)
    elementos: list = [Paragraph("Relatório Consolidado de Peças", ESTILO_TITULO)]
    elementos += _cabecalho_documento()

    linhas = [["Código", "Descrição", "Característica crítica", "Cpk", "Status", "Nº amostras"]]
    for item in itens:
        linhas.append(
            [
                item["codigo"],
                item["descricao"],
                item["caracteristica_critica"] or "—",
                _fmt(item["cpk_critico"], 2),
                _CLASSIFICACAO_LABEL.get(item["classificacao"], "—"),
                str(item["n_amostras"]),
            ]
        )
    elementos.append(_tabela(linhas))
    doc.build(elementos)
    return buffer.getvalue()


def gerar_pdf_consolidado_nc(dados: dict) -> bytes:
    buffer = BytesIO()
    doc = _novo_documento(buffer)
    elementos: list = [Paragraph("Relatório Consolidado de Não Conformidades", ESTILO_TITULO)]
    elementos += _cabecalho_documento()

    elementos.append(Paragraph("Indicadores gerais", ESTILO_SECAO))
    elementos.append(
        _tabela(
            [
                ["Total de RNCs", "Encerradas", "Tempo médio de tratamento (dias)", "Taxa de reincidência"],
                [
                    str(dados["total_rnc"]),
                    str(dados["total_encerradas"]),
                    _fmt(dados["tempo_medio_tratamento_dias"], 1),
                    f"{dados['taxa_reincidencia'] * 100:.1f}%",
                ],
            ]
        )
    )

    for titulo, chave in [("Por peça", "por_peca"), ("Por classificação", "por_classificacao"), ("Por origem", "por_origem")]:
        elementos.append(Paragraph(titulo, ESTILO_SECAO))
        linhas = [["Categoria", "Quantidade"]] + [[k, str(v)] for k, v in dados[chave].items()]
        elementos.append(_tabela(linhas, larguras=[10 * cm, 4 * cm]))

    doc.build(elementos)
    return buffer.getvalue()
