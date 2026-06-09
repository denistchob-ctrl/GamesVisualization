"""
Dashboard de Análise de Vendas de Jogos
========================================
Autor: Refatorado com boas práticas
Dados: VGChartz (via Kaggle) - valores em milhões de unidades vendidas
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================

st.set_page_config(
    page_title="VG Sales · Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# TEMA / DESIGN TOKENS
# Paleta inspirada em telas de arcade retro com acabamento moderno:
# fundo escuro azul-marinho, acento roxo neon, texto claro, destaque âmbar.
# =============================================================================

COLORS = {
    "bg":          "#0E1117",   # fundo principal (padrão dark Streamlit)
    "surface":     "#161B27",   # cards/painéis
    "border":      "#2A3044",   # bordas sutis
    "accent":      "#7C3AED",   # roxo neon (primário)
    "accent_soft": "#A78BFA",   # roxo claro (hover / linhas)
    "amber":       "#F59E0B",   # âmbar (destaque / tendência)
    "teal":        "#14B8A6",   # teal (complementar)
    "text":        "#E2E8F0",   # texto primário
    "muted":       "#64748B",   # texto secundário
}

# Paleta sequencial para gráficos com múltiplas categorias
PLOTLY_COLORSCALE = "Turbo"

# Layout padrão para todos os gráficos Plotly
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",   # fundo transparente (herda CSS)
    plot_bgcolor="rgba(22,27,39,1)", # fundo do plot ligeiramente elevado
    font=dict(family="Inter, sans-serif", color=COLORS["text"], size=12),
    title_font=dict(size=15, color=COLORS["text"], family="Inter, sans-serif"),
    margin=dict(l=16, r=16, t=48, b=16),
    hoverlabel=dict(
        bgcolor=COLORS["surface"],
        bordercolor=COLORS["accent"],
        font_color=COLORS["text"],
        font_size=13,
    ),
    xaxis=dict(
        gridcolor=COLORS["border"],
        linecolor=COLORS["border"],
        tickcolor=COLORS["border"],
    ),
    yaxis=dict(
        gridcolor=COLORS["border"],
        linecolor=COLORS["border"],
        tickcolor=COLORS["border"],
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor=COLORS["border"],
    ),
)

# CSS injetado globalmente no Streamlit
CUSTOM_CSS = f"""
<style>
/* Importar fonte Inter do Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

/* Cabeçalho principal */
.dash-header {{
    background: linear-gradient(135deg, {COLORS["surface"]} 0%, #1E1B4B 100%);
    border: 1px solid {COLORS["border"]};
    border-radius: 12px;
    padding: 28px 32px 20px;
    margin-bottom: 24px;
}}
.dash-header h1 {{
    color: {COLORS["text"]};
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
}}
.dash-header p {{
    color: {COLORS["muted"]};
    font-size: 0.95rem;
    margin: 0;
}}

/* Cards de KPI */
.kpi-card {{
    background: {COLORS["surface"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 10px;
    padding: 18px 20px;
    text-align: center;
    transition: border-color 0.2s;
}}
.kpi-card:hover {{
    border-color: {COLORS["accent_soft"]};
}}
.kpi-value {{
    font-size: 1.9rem;
    font-weight: 700;
    color: {COLORS["accent_soft"]};
    line-height: 1.1;
    display: block;
}}
.kpi-label {{
    font-size: 0.78rem;
    color: {COLORS["muted"]};
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 4px;
    display: block;
}}
.kpi-sub {{
    font-size: 0.82rem;
    color: {COLORS["teal"]};
    margin-top: 2px;
    display: block;
}}

/* Wrapper de gráficos com borda e fundo */
.chart-card {{
    background: {COLORS["surface"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 10px;
    padding: 4px 8px 8px;
    margin-bottom: 8px;
}}

/* Subtítulo de seção */
.section-label {{
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {COLORS["muted"]};
    margin-bottom: 4px;
}}

/* Filtro ativo na sidebar */
.filter-tag {{
    background: {COLORS["accent"]};
    color: white;
    border-radius: 4px;
    padding: 1px 7px;
    font-size: 0.75rem;
}}

/* Aviso de dados filtrados */
.filter-notice {{
    background: rgba(124,58,237,0.12);
    border-left: 3px solid {COLORS["accent"]};
    border-radius: 0 6px 6px 0;
    padding: 8px 12px;
    font-size: 0.85rem;
    color: {COLORS["accent_soft"]};
    margin-bottom: 16px;
}}

/* Remove fundo branco padrão dos charts do Streamlit */
[data-testid="stPlotlyChart"] {{
    border-radius: 8px;
    overflow: hidden;
}}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# =============================================================================
# CARREGAMENTO E PRÉ-PROCESSAMENTO DOS DADOS
# =============================================================================

@st.cache_data(show_spinner="Carregando dados...")
def load_data() -> pd.DataFrame:
    """Carrega e normaliza o CSV de vendas de jogos."""
    df = pd.read_csv("vgsales.csv")

    # Renomear colunas para português
    df = df.rename(columns={
        "NA_Sales":     "América do Norte",
        "EU_Sales":     "Europa",
        "JP_Sales":     "Japão",
        "Other_Sales":  "Outros Países",
        "Global_Sales": "Vendas Globais",
    })

    # Tratar valores inválidos e converter tipos
    df.replace(["N/A", "Unknown"], np.nan, inplace=True)
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    for col in ["América do Norte", "Europa", "Japão", "Outros Países", "Vendas Globais"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


REGIONS = ["América do Norte", "Europa", "Japão", "Outros Países"]


# =============================================================================
# FILTROS
# =============================================================================

def build_sidebar_filters(df: pd.DataFrame) -> tuple:
    """
    Renderiza todos os filtros na barra lateral e retorna as seleções.
    Retorna: (option, selected_genre, selected_year, selected_platform,
              selected_publisher, simplify_data)
    """
    st.sidebar.markdown("## 🎮 VG Sales")
    st.sidebar.markdown("---")

    option = st.sidebar.radio(
        "Navegação",
        [
            "📊 Resumo Integrado",
            "📈 Tendências Temporais",
            "🗺️ Produção por Ano/Gênero",
            "ℹ️ Sobre a Base de Dados",
        ],
        label_visibility="collapsed",
    )

    st.sidebar.markdown("### Filtros")

    def sorted_with_all(series):
        vals = series.dropna().unique().tolist()
        vals.sort()
        return ["Todos"] + vals

    selected_genre     = st.sidebar.selectbox("Gênero",       sorted_with_all(df["Genre"]))
    selected_year      = st.sidebar.selectbox("Ano",          sorted_with_all(df["Year"]))
    selected_platform  = st.sidebar.selectbox("Plataforma",   sorted_with_all(df["Platform"]))
    selected_publisher = st.sidebar.selectbox("Desenvolvedora", sorted_with_all(df["Publisher"]))

    st.sidebar.markdown("---")
    simplify_data = st.sidebar.checkbox(
        "Resumir dados",
        help="Remove plataformas com < 100 M em vendas, anos com < 100 títulos e registros nulos."
    )
    if simplify_data:
        st.sidebar.caption("✂️ Plataformas < 100 M, anos < 100 títulos e nulos serão removidos.")

    return option, selected_genre, selected_year, selected_platform, selected_publisher, simplify_data


def apply_filters(
    df: pd.DataFrame,
    genre: str,
    year,
    platform: str,
    publisher: str,
    simplify: bool,
) -> pd.DataFrame:
    """Aplica todos os filtros selecionados e retorna o DataFrame filtrado."""
    dff = df.copy()

    if genre    != "Todos": dff = dff[dff["Genre"]     == genre]
    if year     != "Todos": dff = dff[dff["Year"]      == year]
    if platform != "Todos": dff = dff[dff["Platform"]  == platform]
    if publisher!= "Todos": dff = dff[dff["Publisher"] == publisher]

    if simplify:
        dff = dff.dropna()

        valid_platforms = (
            df.groupby("Platform")["Vendas Globais"].sum()
            .loc[lambda s: s > 100].index
        )
        dff = dff[dff["Platform"].isin(valid_platforms)]

        valid_years = (
            dff.groupby("Year")["Name"].count()
            .loc[lambda s: s >= 100].index
        )
        dff = dff[dff["Year"].isin(valid_years)]

    return dff


def active_filters_notice(genre, year, platform, publisher, simplify) -> str:
    """Retorna uma string com os filtros ativos para exibir no topo da página."""
    active = []
    if genre     != "Todos": active.append(f"Gênero: <b>{genre}</b>")
    if year      != "Todos": active.append(f"Ano: <b>{year}</b>")
    if platform  != "Todos": active.append(f"Plataforma: <b>{platform}</b>")
    if publisher != "Todos": active.append(f"Desenvolvedora: <b>{publisher}</b>")
    if simplify:              active.append("<b>Dados resumidos</b>")
    return " · ".join(active) if active else ""


# =============================================================================
# HELPERS DE GRÁFICOS
# =============================================================================

def apply_theme(fig: go.Figure, height: int = 420) -> go.Figure:
    """Aplica o layout padrão de tema a qualquer figura Plotly."""
    fig.update_layout(**CHART_LAYOUT, height=height)
    return fig


def turbo_colors(n: int) -> list:
    """Gera n cores da paleta Turbo (evita divisão por zero)."""
    if n <= 1:
        return ["#7C3AED"]
    return px.colors.sample_colorscale("Turbo", [i / (n - 1) for i in range(n)])


def chart_container(fig: go.Figure, key: str, height: int = 420):
    """Exibe um gráfico Plotly envolto num card estilizado."""
    fig = apply_theme(fig, height=height)
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, key=key)
    st.markdown("</div>", unsafe_allow_html=True)


# =============================================================================
# KPI CARDS
# =============================================================================

def render_kpis(dff: pd.DataFrame):
    """Renderiza a linha de KPIs no topo do Resumo Integrado."""
    total_vendas   = dff["Vendas Globais"].sum()
    total_jogos    = dff["Name"].nunique()
    total_plat     = dff["Platform"].nunique()
    top_jogo       = dff.groupby("Name")["Vendas Globais"].sum().idxmax() if len(dff) else "—"
    top_jogo_venda = dff.groupby("Name")["Vendas Globais"].sum().max() if len(dff) else 0
    top_pub        = dff.groupby("Publisher")["Vendas Globais"].sum().idxmax() if len(dff) else "—"

    kpis = [
        ("💰", f"{total_vendas:,.1f} M", "Vendas Globais", None),
        ("🎮", f"{total_jogos:,}",        "Títulos únicos",  None),
        ("🕹️", f"{total_plat}",            "Plataformas",     None),
        ("🏆", top_jogo[:22] + ("…" if len(str(top_jogo)) > 22 else ""),
               "Jogo mais vendido",   f"{top_jogo_venda:.1f} M"),
        ("🏢", top_pub[:22] + ("…" if len(str(top_pub)) > 22 else ""),
               "Top desenvolvedora",  None),
    ]

    cols = st.columns(len(kpis))
    for col, (icon, value, label, sub) in zip(cols, kpis):
        sub_html = f'<span class="kpi-sub">{sub}</span>' if sub else ""
        col.markdown(
            f"""
            <div class="kpi-card">
                <span style="font-size:1.4rem">{icon}</span>
                <span class="kpi-value">{value}</span>
                <span class="kpi-label">{label}</span>
                {sub_html}
            </div>
            """,
            unsafe_allow_html=True,
        )


# =============================================================================
# PÁGINAS
# =============================================================================

def page_resumo(dff: pd.DataFrame, selected_year):
    """Página 1 – Resumo Integrado."""
    st.markdown(
        '<div class="dash-header">'
        '<h1>📊 Resumo Integrado</h1>'
        '<p>Visão geral de vendas, plataformas, gêneros e desenvolvedoras.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    render_kpis(dff)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Linha 1: Vendas por Ano  +  Pizza de Gêneros ──────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        vendas_por_ano = dff.groupby("Year")["Vendas Globais"].sum().reset_index()
        fig = px.area(
            vendas_por_ano, x="Year", y="Vendas Globais",
            labels={"Year": "Ano", "Vendas Globais": "Vendas (M)"},
            title="Vendas Globais por Ano",
            color_discrete_sequence=[COLORS["accent_soft"]],
        )
        fig.update_traces(
            fill="tozeroy",
            fillcolor="rgba(124,58,237,0.18)",
            line=dict(color=COLORS["accent_soft"], width=2),
            hovertemplate="<b>%{x}</b><br>Vendas: %{y:.1f} M<extra></extra>",
        )
        # Linha de tendência linear quando sem filtro de ano
        if selected_year == "Todos" and len(vendas_por_ano) > 2:
            x_vals = vendas_por_ano["Year"].astype(float)
            y_vals = vendas_por_ano["Vendas Globais"]
            coef   = np.polyfit(x_vals, y_vals, 1)
            trend  = np.poly1d(coef)
            fig.add_scatter(
                x=vendas_por_ano["Year"],
                y=trend(x_vals),
                mode="lines",
                name="Tendência",
                line=dict(dash="dot", color=COLORS["amber"], width=2),
                hovertemplate="Tendência: %{y:.1f} M<extra></extra>",
            )
        chart_container(fig, "vendas_ano")

    with col2:
        generos_df = dff.groupby("Genre")["Vendas Globais"].sum().reset_index()
        fig = px.pie(
            generos_df, names="Genre", values="Vendas Globais",
            title="Participação por Gênero",
            hole=0.42,
            color_discrete_sequence=px.colors.qualitative.Vivid,
        )
        fig.update_traces(
            textposition="inside",
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>%{value:.1f} M (%{percent})<extra></extra>",
        )
        fig.update_layout(
            legend=dict(orientation="v", x=1.02, y=0.5, font_size=11)
        )
        chart_container(fig, "pizza_genero")

    # ── Linha 2: Plataformas  +  Top 10 Jogos ─────────────────────────────────
    col3, col4 = st.columns(2)

    with col3:
        plat_df = (
            dff.groupby("Platform")["Vendas Globais"].sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        fig = px.bar(
            plat_df, x="Platform", y="Vendas Globais",
            labels={"Platform": "Plataforma", "Vendas Globais": "Vendas (M)"},
            title="Vendas por Plataforma",
            color="Vendas Globais",
            color_continuous_scale="Turbo",
        )
        fig.update_traces(
            hovertemplate="<b>%{x}</b><br>%{y:.1f} M<extra></extra>"
        )
        fig.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            xaxis_tickangle=-45,
        )
        chart_container(fig, "vendas_plat")

    with col4:
        top_jogos = (
            dff.groupby("Name")["Vendas Globais"].sum()
            .nlargest(10)
            .reset_index()
            .sort_values("Vendas Globais")
        )
        top_jogos["Label"] = top_jogos["Name"].str.slice(0, 28)
        fig = px.bar(
            top_jogos, x="Vendas Globais", y="Label",
            orientation="h",
            labels={"Label": "", "Vendas Globais": "Vendas (M)"},
            title="Top 10 Jogos Mais Vendidos",
            color="Vendas Globais",
            color_continuous_scale="Turbo",
        )
        fig.update_traces(
            hovertemplate="<b>%{y}</b><br>%{x:.1f} M<extra></extra>"
        )
        fig.update_layout(showlegend=False, coloraxis_showscale=False)
        chart_container(fig, "top10_jogos")

    # ── Linha 3: Vendas por Gênero/Região (stacked) ───────────────────────────
    genre_sales   = dff.groupby("Genre")["Vendas Globais"].sum().sort_values(ascending=False)
    genre_region  = dff.groupby("Genre")[REGIONS].sum().loc[genre_sales.index].reset_index()
    region_colors = [COLORS["accent"], COLORS["teal"], COLORS["amber"], "#F43F5E"]

    fig = px.bar(
        genre_region, x="Genre", y=REGIONS,
        title="Distribuição Regional por Gênero",
        labels={"Genre": "Gênero", "value": "Vendas (M)", "variable": "Região"},
        barmode="stack",
        color_discrete_sequence=region_colors,
    )
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y:.1f} M<extra></extra>"
    )
    chart_container(fig, "genero_regiao", height=380)

    # ── Linha 4: Top 20 Desenvolvedoras ───────────────────────────────────────
    pub_df = (
        dff.groupby("Publisher")["Vendas Globais"]
        .sum()
        .sort_values(ascending=True)
        .tail(20)
        .reset_index()
    )
    n = len(pub_df)
    fig = px.bar(
        pub_df, x="Vendas Globais", y="Publisher",
        orientation="h",
        labels={"Publisher": "", "Vendas Globais": "Vendas Globais (M)"},
        title="Top 20 Desenvolvedoras por Vendas Globais",
        color="Vendas Globais",
        color_continuous_scale="Turbo",
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>%{x:.1f} M<extra></extra>"
    )
    fig.update_layout(showlegend=False, coloraxis_showscale=False)
    chart_container(fig, "top20_pub", height=560)


def page_tendencias(dff: pd.DataFrame):
    """Página 2 – Tendências Temporais."""
    st.markdown(
        '<div class="dash-header">'
        '<h1>📈 Tendências Temporais</h1>'
        '<p>Evolução das vendas ao longo dos anos por gênero — 2D e 3D interativo.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    tendencias = dff.groupby(["Year", "Genre"])["Vendas Globais"].sum().reset_index()

    # ── Gráfico de linhas 2D ───────────────────────────────────────────────────
    fig = px.line(
        tendencias, x="Year", y="Vendas Globais", color="Genre",
        labels={"Year": "Ano", "Genre": "Gênero", "Vendas Globais": "Vendas (M)"},
        title="Evolução das Vendas por Gênero (Linha)",
        color_discrete_sequence=px.colors.qualitative.Vivid,
    )
    fig.update_traces(
        line_width=2,
        hovertemplate="<b>%{fullData.name}</b><br>%{x}: %{y:.1f} M<extra></extra>",
    )
    chart_container(fig, "tendencia_linha", height=460)

    # ── Superfície 3D ─────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🧊 Superfície 3D Interativa")
    st.caption("Arraste para rotacionar · Scroll para zoom · Hover para detalhes")

    pivot = (
        tendencias
        .pivot(index="Genre", columns="Year", values="Vendas Globais")
        .fillna(0)
    )
    X, Y = np.meshgrid(pivot.columns.astype(float), range(len(pivot.index)))
    Z    = pivot.values

    fig3d = go.Figure(data=[
        go.Surface(
            z=Z, x=X, y=Y,
            colorscale="Turbo",
            opacity=0.92,
            contours=dict(
                z=dict(show=True, usecolormap=True, highlightcolor=COLORS["amber"], project_z=True)
            ),
        )
    ])
    fig3d.update_layout(
        title="Vendas por Gênero/Ano — Superfície 3D",
        scene=dict(
            xaxis=dict(title="Ano",    tickvals=list(pivot.columns[::4]),
                       gridcolor=COLORS["border"], backgroundcolor=COLORS["surface"]),
            yaxis=dict(title="Gênero", tickvals=list(range(len(pivot.index))),
                       ticktext=list(pivot.index),
                       gridcolor=COLORS["border"], backgroundcolor=COLORS["surface"]),
            zaxis=dict(title="Vendas (M)",
                       gridcolor=COLORS["border"], backgroundcolor=COLORS["surface"]),
            bgcolor=COLORS["surface"],
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLORS["text"], family="Inter, sans-serif"),
        margin=dict(l=0, r=0, t=50, b=0),
        height=620,
    )
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(fig3d, use_container_width=True, key="3d_surface")
    st.markdown("</div>", unsafe_allow_html=True)


def page_producao(dff: pd.DataFrame):
    """Página 3 – Produção de Jogos por Ano/Gênero."""
    st.markdown(
        '<div class="dash-header">'
        '<h1>🗺️ Produção por Ano/Gênero</h1>'
        '<p>Heatmap dos 5 anos com maior produção × 6 gêneros mais prolíficos.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    top_years  = sorted(dff["Year"].value_counts().nlargest(5).index.tolist())
    top_genres = sorted(dff["Genre"].value_counts().nlargest(6).index.tolist())

    matrix = dff[dff["Year"].isin(top_years) & dff["Genre"].isin(top_genres)]
    pivot  = matrix.pivot_table(
        index="Genre", columns="Year", values="Name", aggfunc="count"
    ).reindex(index=top_genres, columns=top_years, fill_value=0)

    # ── Heatmap ───────────────────────────────────────────────────────────────
    fig = px.imshow(
        pivot.values,
        labels=dict(x="Ano", y="Gênero", color="Qtd. Jogos"),
        x=pivot.columns.astype(str),
        y=pivot.index,
        color_continuous_scale="Reds",
        text_auto=True,
        title="Número de Jogos Lançados — Top Anos × Gêneros",
        aspect="auto",
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b> · %{x}<br>%{z} jogos<extra></extra>",
        textfont=dict(size=14, color="white"),
    )
    fig.update_xaxes(side="top")
    chart_container(fig, "heatmap_producao", height=480)

    # ── Bar chart: produção anual total ──────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    prod_anual = (
        dff.groupby("Year")["Name"].count().reset_index()
        .rename(columns={"Name": "Quantidade"})
    )
    fig2 = px.bar(
        prod_anual, x="Year", y="Quantidade",
        labels={"Year": "Ano", "Quantidade": "Títulos lançados"},
        title="Total de Títulos Lançados por Ano",
        color="Quantidade",
        color_continuous_scale="Blues",
    )
    fig2.update_traces(
        hovertemplate="<b>%{x}</b><br>%{y:,} títulos<extra></extra>"
    )
    fig2.update_layout(coloraxis_showscale=False)
    chart_container(fig2, "prod_anual", height=360)


def page_sobre(df: pd.DataFrame):
    """Página 0 – Informações sobre a base de dados."""
    st.markdown(
        '<div class="dash-header">'
        '<h1>ℹ️ Sobre a Base de Dados</h1>'
        '<p>Origem, cobertura e estatísticas da base VGChartz.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.info(
        "**Fonte:** [VGChartz via Kaggle](https://www.kaggle.com/datasets/gregorut/videogamesales) · "
        "[Script de extração](https://github.com/GregorUT/vgchartzScrape) (BeautifulSoup/Python)  \n"
        "Base extraída ~meados de 2016. Anos 2017+ têm poucos registros e podem estar incompletos.  \n"
        "**Todos os valores de venda estão em milhões de unidades.**",
        icon="ℹ️",
    )

    # ── KPIs da base completa ─────────────────────────────────────────────────
    kpis = {
        "Registros totais":          len(df),
        "Títulos únicos":             df["Name"].nunique(),
        "Gêneros":                   df["Genre"].nunique(),
        "Plataformas":               df["Platform"].nunique(),
        "Desenvolvedoras":           df["Publisher"].nunique(),
        "Jogos multi-plataforma":    df[df.duplicated("Name", keep=False)]["Name"].nunique(),
    }
    cols = st.columns(3)
    for i, (label, val) in enumerate(kpis.items()):
        cols[i % 3].markdown(
            f'<div class="kpi-card"><span class="kpi-value">{val:,}</span>'
            f'<span class="kpi-label">{label}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabelas lado a lado ───────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Mínimos e Máximos")
        stats = [
            ("Ano",              int(df["Year"].min()),              int(df["Year"].max())),
            ("Vendas América N.", df["América do Norte"].min(),      df["América do Norte"].max()),
            ("Vendas Europa",     df["Europa"].min(),                df["Europa"].max()),
            ("Vendas Japão",      df["Japão"].min(),                 df["Japão"].max()),
            ("Vendas Outros",     df["Outros Países"].min(),         df["Outros Países"].max()),
            ("Vendas Globais",    df["Vendas Globais"].min(),        df["Vendas Globais"].max()),
        ]
        st.dataframe(
            pd.DataFrame(stats, columns=["Indicador", "Mínimo", "Máximo"]),
            use_container_width=True, hide_index=True,
        )

    with col2:
        st.subheader("Completude por Coluna")
        null_df = pd.DataFrame({
            "Coluna":    df.columns,
            "Nulos":     df.isnull().sum().values,
            "Não Nulos": df.notnull().sum().values,
        })
        st.dataframe(null_df, use_container_width=True, hide_index=True)

    # ── Gráfico de nulos ──────────────────────────────────────────────────────
    fig = px.bar(
        null_df.melt(id_vars="Coluna", value_vars=["Nulos", "Não Nulos"],
                     var_name="Tipo", value_name="Quantidade"),
        x="Coluna", y="Quantidade", color="Tipo",
        barmode="group",
        title="Valores Nulos vs Não Nulos por Coluna",
        color_discrete_map={"Nulos": "#F43F5E", "Não Nulos": COLORS["teal"]},
    )
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y:,}<extra></extra>"
    )
    chart_container(fig, "nulos_chart", height=360)


# =============================================================================
# MAIN
# =============================================================================

def main():
    df = load_data()

    # Sidebar com filtros
    option, genre, year, platform, publisher, simplify = build_sidebar_filters(df)

    # Aplicar filtros
    dff = apply_filters(df, genre, year, platform, publisher, simplify)

    # Banner de filtros ativos
    notice = active_filters_notice(genre, year, platform, publisher, simplify)
    if notice:
        st.markdown(
            f'<div class="filter-notice">🔍 Filtros ativos: {notice}</div>',
            unsafe_allow_html=True,
        )

    # Roteamento de páginas
    if   option.startswith("📊"): page_resumo(dff, year)
    elif option.startswith("📈"): page_tendencias(dff)
    elif option.startswith("🗺️"): page_producao(dff)
    elif option.startswith("ℹ️"): page_sobre(df)


if __name__ == "__main__":
    main()
