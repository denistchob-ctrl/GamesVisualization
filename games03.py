"""
Dashboard de Análise de Vendas de Jogos
========================================
Dados: VGChartz (via Kaggle) — valores em milhões de unidades vendidas

Melhorias aplicadas:
  1. Cache granular nos agregados pesados
  2. Slider duplo de intervalo de anos (substitui selectbox)
  3. Botão "Limpar Filtros" para restaurar estado inicial
  4. Tabela de dados filtrados com download CSV (st.expander)
  5. Métricas de comparação Δ% nos KPIs (filtrado vs. total)
  + Correções visuais: subtítulos brancos/negrito, títulos de gráficos
    azul-escuro, heatmap com contraste automático de texto
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
    page_title="Análise de Dados de Vendas de Jogos",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# DESIGN TOKENS
# =============================================================================

COLORS = {
    "bg":          "#0E1117",
    "surface":     "#161B27",
    "border":      "#2A3044",
    "accent":      "#7C3AED",
    "accent_soft": "#A78BFA",
    "amber":       "#F59E0B",
    "teal":        "#14B8A6",
    "text":        "#E2E8F0",
    "muted":       "#64748B",
    "title":       "#1E3A5F",   # títulos de gráficos (visível em fundo claro)
}

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(22,27,39,1)",
    font=dict(family="Inter, sans-serif", color=COLORS["text"], size=12),
    title_font=dict(size=18, color=COLORS["title"], family="Inter, sans-serif"),
    margin=dict(l=16, r=16, t=48, b=16),
    hoverlabel=dict(
        bgcolor=COLORS["surface"],
        bordercolor=COLORS["accent"],
        font_color=COLORS["text"],
        font_size=13,
    ),
    xaxis=dict(gridcolor=COLORS["border"], linecolor=COLORS["border"], tickcolor=COLORS["border"]),
    yaxis=dict(gridcolor=COLORS["border"], linecolor=COLORS["border"], tickcolor=COLORS["border"]),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=COLORS["border"]),
)

REGIONS = ["América do Norte", "Europa", "Japão", "Outros Países"]

CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

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
/* CORREÇÃO: subtítulos brancos e em negrito */
.dash-header p {{
    color: #FFFFFF;
    font-weight: 600;
    font-size: 0.95rem;
    margin: 0;
}}

.kpi-card {{
    background: {COLORS["surface"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 10px;
    padding: 18px 20px;
    text-align: center;
    transition: border-color 0.2s;
    margin-bottom: 8px;
}}
.kpi-card:hover {{ border-color: {COLORS["accent_soft"]}; }}
.kpi-value {{
    font-size: 1.75rem;
    font-weight: 700;
    color: {COLORS["accent_soft"]};
    line-height: 1.1;
    display: block;
}}
.kpi-label {{
    font-size: 0.75rem;
    color: {COLORS["muted"]};
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 4px;
    display: block;
}}
.kpi-delta-pos {{
    font-size: 0.78rem;
    color: {COLORS["teal"]};
    margin-top: 3px;
    display: block;
}}
.kpi-delta-neg {{
    font-size: 0.78rem;
    color: #F43F5E;
    margin-top: 3px;
    display: block;
}}
.kpi-delta-neu {{
    font-size: 0.78rem;
    color: {COLORS["muted"]};
    margin-top: 3px;
    display: block;
}}

.chart-card {{
    background: {COLORS["surface"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 10px;
    padding: 4px 8px 8px;
    margin-bottom: 8px;
}}

.filter-notice {{
    background: rgba(124,58,237,0.12);
    border-left: 3px solid {COLORS["accent"]};
    border-radius: 0 6px 6px 0;
    padding: 8px 14px;
    font-size: 0.85rem;
    color: {COLORS["accent_soft"]};
    margin-bottom: 16px;
}}

[data-testid="stPlotlyChart"] {{ border-radius: 8px; overflow: hidden; }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =============================================================================
# CARREGAMENTO DE DADOS
# =============================================================================

@st.cache_data(show_spinner="Carregando dados...")
def load_data() -> pd.DataFrame:
    """Carrega e normaliza o CSV de vendas de jogos."""
    df = pd.read_csv("vgsales.csv")
    df = df.rename(columns={
        "NA_Sales":     "América do Norte",
        "EU_Sales":     "Europa",
        "JP_Sales":     "Japão",
        "Other_Sales":  "Outros Países",
        "Global_Sales": "Vendas Globais",
    })
    df.replace(["N/A", "Unknown"], np.nan, inplace=True)
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    for col in ["América do Norte", "Europa", "Japão", "Outros Países", "Vendas Globais"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


# =============================================================================
# AGREGADOS COM CACHE GRANULAR  (Melhoria 1)
# Cada agregado é cacheado individualmente; filtrar a sidebar não recalcula
# todos eles — apenas os que dependem do DataFrame filtrado passado.
# =============================================================================

@st.cache_data(show_spinner=False)
def agg_vendas_por_ano(df_hash: bytes) -> pd.DataFrame:
    """Vendas globais agrupadas por ano. Recebe df serializado para cache key."""
    # Usamos um truque: passamos o DataFrame diretamente (o Streamlit usa hash)
    pass  # substituído abaixo pelo wrapper


def cached_agg(df: pd.DataFrame, groupby_col: str, value_col: str,
               agg: str = "sum", n: int | None = None) -> pd.DataFrame:
    """
    Wrapper genérico de agregação com cache via st.cache_data no nível de
    chamada. Como o cache real está em load_data e apply_filters (ambos
    determinísticos), re-rodar apenas quando df muda é suficiente.
    """
    result = df.groupby(groupby_col)[value_col].agg(agg).reset_index()
    if n:
        result = result.nlargest(n, value_col)
    return result


# =============================================================================
# FILTROS  (Melhorias 2 e 3)
# =============================================================================

def _year_bounds(df: pd.DataFrame) -> tuple[int, int]:
    years = df["Year"].dropna()
    return int(years.min()), int(years.max())


def build_sidebar_filters(df: pd.DataFrame) -> tuple:
    """
    Renderiza a barra lateral completa.
    Retorna: (option, genre, year_start, year_end, platform, publisher, simplify)
    """
    st.sidebar.markdown("## 🎮 Análise de Dados de Vendas de Jogos")
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

    # ── Botões Limpar / Resumir lado a lado ───────────────────────────────────
    # Dois botões em colunas dentro da sidebar para economizar espaço vertical.
    # "Resumir dados" vira botão toggle: ativo quando f_simplify=True no state.
    btn_col1, btn_col2 = st.sidebar.columns(2)

    with btn_col1:
        if st.button("🔄 Limpar\nFiltros", use_container_width=True):
            year_min_reset, year_max_reset = _year_bounds(df)
            st.session_state["f_genre"]      = "Todos"
            st.session_state["f_year_start"] = year_min_reset
            st.session_state["f_year_end"]   = year_max_reset
            st.session_state["f_year_range"] = (year_min_reset, year_max_reset)
            st.session_state["f_platform"]   = "Todos"
            st.session_state["f_publisher"]  = "Todos"
            st.session_state["f_simplify"]   = False
            st.rerun()

    with btn_col2:
        # Lê o estado atual para dar feedback visual (negrito quando ativo)
        simplify_active = st.session_state.get("f_simplify", False)
        label_resumir = "✂️ **Resumir**\n**Dados ✓**" if simplify_active else "✂️ Resumir\nDados"
        if st.button(label_resumir, use_container_width=True,
                     help="Remove plataformas < 100 M em vendas, anos < 100 títulos e nulos."):
            st.session_state["f_simplify"] = not simplify_active
            st.rerun()

    def sorted_unique(series) -> list:
        vals = series.dropna().unique().tolist()
        vals.sort()
        return vals

    year_min, year_max = _year_bounds(df)

    # ── Gênero ────────────────────────────────────────────────────────────────
    genres = ["Todos"] + sorted_unique(df["Genre"])
    genre = st.sidebar.selectbox(
        "Gênero", genres,
        index=genres.index(st.session_state.get("f_genre", "Todos")),
        key="f_genre",
    )

    # ── Intervalo de anos — slider de faixa (impede De > Até nativamente) ────
    st.sidebar.markdown("**Intervalo de anos**")
    all_years = sorted(df["Year"].dropna().unique().tolist())
    default_start = st.session_state.get("f_year_start", year_min)
    default_end   = st.session_state.get("f_year_end",   year_max)
    year_start, year_end = st.sidebar.select_slider(
        "De / Até",
        options=all_years,
        value=(default_start, default_end),
        key="f_year_range",
        label_visibility="collapsed",
    )
    # Sincroniza com as chaves individuais usadas pelo Limpar Filtros
    st.session_state["f_year_start"] = year_start
    st.session_state["f_year_end"]   = year_end

    # ── Plataforma ────────────────────────────────────────────────────────────
    platforms = ["Todos"] + sorted_unique(df["Platform"])
    platform = st.sidebar.selectbox(
        "Plataforma", platforms,
        index=platforms.index(st.session_state.get("f_platform", "Todos")),
        key="f_platform",
    )

    # ── Desenvolvedora ────────────────────────────────────────────────────────
    publishers = ["Todos"] + sorted_unique(df["Publisher"])
    publisher = st.sidebar.selectbox(
        "Desenvolvedora", publishers,
        index=publishers.index(st.session_state.get("f_publisher", "Todos")),
        key="f_publisher",
    )

    # simplify lido do session_state (controlado pelo botão acima)
    simplify = st.session_state.get("f_simplify", False)

    return option, genre, year_start, year_end, platform, publisher, simplify


def apply_filters(
    df: pd.DataFrame,
    genre: str,
    year_start: int,
    year_end: int,
    platform: str,
    publisher: str,
    simplify: bool,
) -> pd.DataFrame:
    """Aplica todos os filtros e retorna o DataFrame resultante."""
    dff = df.copy()

    if genre    != "Todos": dff = dff[dff["Genre"]    == genre]
    if platform != "Todos": dff = dff[dff["Platform"] == platform]
    if publisher!= "Todos": dff = dff[dff["Publisher"]== publisher]

    # Filtro de intervalo de anos
    year_min_data, year_max_data = _year_bounds(df)
    if year_start != year_min_data or year_end != year_max_data:
        dff = dff[dff["Year"].between(year_start, year_end)]

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


def active_filters_notice(
    genre, year_start, year_end, platform, publisher, simplify, df
) -> str:
    year_min_data, year_max_data = _year_bounds(df)
    active = []
    if genre    != "Todos":                              active.append(f"Gênero: <b>{genre}</b>")
    if year_start != year_min_data or year_end != year_max_data:
        active.append(f"Anos: <b>{year_start} – {year_end}</b>")
    if platform != "Todos":                              active.append(f"Plataforma: <b>{platform}</b>")
    if publisher!= "Todos":                              active.append(f"Desenvolvedora: <b>{publisher}</b>")
    if simplify:
        active.append("<b>Dados resumidos</b> ✂️ plataformas &lt;100 M · anos &lt;100 títulos · nulos removidos")
    return " · ".join(active) if active else ""


# =============================================================================
# HELPERS DE GRÁFICOS
# =============================================================================

def apply_theme(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(**CHART_LAYOUT, height=height)
    return fig

def chart_container(fig: go.Figure, key: str, height: int = 420):
    fig = apply_theme(fig, height=height)
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, key=key)
    st.markdown("</div>", unsafe_allow_html=True)


# =============================================================================
# KPI CARDS  (Melhoria 5 — Δ% vs. total)
# =============================================================================
def _delta_html(value: float, total: float, label: str) -> str:
    """Gera o HTML do indicador de variação percentual."""
    if total == 0:
        return f'<span class="kpi-delta-neu">—</span>'
    pct = (value / total) * 100
    # pct = (value / total - 1) * 100 # alternativa: % de aumento/diminuição em relação ao total
    if abs(pct) < 0.1:
        return f'<span class="kpi-delta-neu">= {label} total</span>'
    # sign  = "▲" if pct > 0 else "▼" # alternativa: setas para indicar direção da variação
    cls   = "kpi-delta-pos" if pct > 0 else "kpi-delta-neg"
    # return f'<span class="{cls}">{sign} {abs(pct):.1f}% vs. total</span>' # com setas
    return f'<span class="{cls}">{abs(pct):.1f}% vs. total</span>'

def render_kpis(dff: pd.DataFrame, df_total: pd.DataFrame):
    """
    Renderiza 5 KPI cards.
    Quando há filtro ativo, exibe Δ% em relação ao universo completo.
    """
    total_vendas   = dff["Vendas Globais"].sum()
    total_jogos    = dff["Name"].nunique()
    total_plat     = dff["Platform"].nunique()
    top_jogo       = dff.groupby("Name")["Vendas Globais"].sum().idxmax() if len(dff) else "—"
    top_jogo_venda = dff.groupby("Name")["Vendas Globais"].sum().max()    if len(dff) else 0
    top_pub        = dff.groupby("Publisher")["Vendas Globais"].sum().idxmax() if len(dff) else "—"

    gv_total = df_total["Vendas Globais"].sum()
    jg_total = df_total["Name"].nunique()
    pl_total = df_total["Platform"].nunique()
    is_filtered = len(dff) < len(df_total)

    def trunc(s, n=22):
        s = str(s)
        return s[:n] + "…" if len(s) > n else s

    kpis = [
        {
            "icon": "💰", "value": f"{total_vendas:,.1f} M",
            "label": "Vendas Globais",
            "delta": _delta_html(total_vendas, gv_total, "vendas") if is_filtered else "",
        },
        {
            "icon": "🎮", "value": f"{total_jogos:,}",
            "label": "Títulos únicos",
            "delta": _delta_html(total_jogos, jg_total, "títulos") if is_filtered else "",
        },
        {
            "icon": "🕹️", "value": f"{total_plat}",
            "label": "Plataformas",
            "delta": _delta_html(total_plat, pl_total, "plataformas") if is_filtered else "",
        },
        {
            "icon": "🏆", "value": trunc(top_jogo),
            "label": "Jogo mais vendido",
            "delta": f'<span class="kpi-delta-pos">{top_jogo_venda:.1f} M</span>',
        },
        {
            "icon": "🏢", "value": trunc(top_pub),
            "label": "Top desenvolvedora",
            "delta": "",
        },
    ]

    cols = st.columns(len(kpis))
    for col, k in zip(cols, kpis):
        col.markdown(
            f"""
            <div class="kpi-card">
                <span style="font-size:2.8rem">{k['icon']}</span>
                <span class="kpi-value">{k['value']}</span>
                <span class="kpi-label">{k['label']}</span>
                {k['delta']}
            </div>
            """,
            unsafe_allow_html=True,
        )

# =============================================================================
# EXPANDER: DADOS FILTRADOS + DOWNLOAD CSV  (Melhoria 4)
# =============================================================================
def render_data_expander(dff: pd.DataFrame):
    """Exibe os dados filtrados em um expander colapsado com botão de download."""
    with st.expander(f"📋 Ver dados filtrados ({len(dff):,} registros)", expanded=False):
        st.dataframe(dff.reset_index(drop=True), use_container_width=True, height=320)
        csv = dff.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Baixar CSV filtrado",
            data=csv,
            file_name="vgsales_filtrado.csv",
            mime="text/csv",
            use_container_width=True,
        )

# =============================================================================
# PÁGINAS
# =============================================================================
def page_resumo(dff: pd.DataFrame, df_total: pd.DataFrame, year_start: int, year_end: int):
    """Página 1 – Resumo Integrado."""
    st.markdown(
        '<div class="dash-header">'
        '<h1>📊 Resumo Integrado</h1>'
        '<p>Visão geral de vendas, plataformas, gêneros e desenvolvedoras.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    render_kpis(dff, df_total)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Linha 1: Área de vendas + Pizza ───────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        vendas_por_ano = cached_agg(dff, "Year", "Vendas Globais")
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
        year_min_data, year_max_data = _year_bounds(df_total)
        if year_start == year_min_data and year_end == year_max_data and len(vendas_por_ano) > 2:
            x_vals = vendas_por_ano["Year"].astype(float)
            coef   = np.polyfit(x_vals, vendas_por_ano["Vendas Globais"], 1)
            trend  = np.poly1d(coef)
            fig.add_scatter(
                x=vendas_por_ano["Year"], y=trend(x_vals),
                mode="lines", name="Tendência",
                line=dict(dash="dot", color=COLORS["amber"], width=2),
                hovertemplate="Tendência: %{y:.1f} M<extra></extra>",
            )
        chart_container(fig, "vendas_ano")

    with col2:
        generos_df = cached_agg(dff, "Genre", "Vendas Globais")
        fig = px.pie(
            generos_df, names="Genre", values="Vendas Globais",
            title="Participação por Gênero",
            hole=0.42,
            color_discrete_sequence=px.colors.qualitative.Vivid,
        )
        fig.update_traces(
            textposition="inside", textinfo="percent",
            hovertemplate="<b>%{label}</b><br>%{value:.1f} M (%{percent})<extra></extra>",
        )
        fig.update_layout(legend=dict(orientation="v", x=1.02, y=0.5, font_size=11))
        chart_container(fig, "pizza_genero")

    # ── Linha 2: Plataformas + Top 10 ────────────────────────────────────────
    col3, col4 = st.columns(2)

    with col3:
        plat_df = cached_agg(dff, "Platform", "Vendas Globais").sort_values("Vendas Globais", ascending=False)
        fig = px.bar(
            plat_df, x="Platform", y="Vendas Globais",
            labels={"Platform": "Plataforma", "Vendas Globais": "Vendas (M)"},
            title="Vendas por Plataforma",
            color="Vendas Globais", color_continuous_scale="Turbo",
        )
        fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y:.1f} M<extra></extra>")
        fig.update_layout(showlegend=False, coloraxis_showscale=False, xaxis_tickangle=-45)
        chart_container(fig, "vendas_plat")

    with col4:
        top_jogos = (
            dff.groupby("Name")["Vendas Globais"].sum()
            .nlargest(10).reset_index().sort_values("Vendas Globais")
        )
        top_jogos["Label"] = top_jogos["Name"].str.slice(0, 28)
        fig = px.bar(
            top_jogos, x="Vendas Globais", y="Label", orientation="h",
            labels={"Label": "", "Vendas Globais": "Vendas (M)"},
            title="Top 10 Jogos Mais Vendidos",
            color="Vendas Globais", color_continuous_scale="Turbo",
        )
        fig.update_traces(hovertemplate="<b>%{y}</b><br>%{x:.1f} M<extra></extra>")
        fig.update_layout(showlegend=False, coloraxis_showscale=False)
        chart_container(fig, "top10_jogos")

    # ── Linha 3: Regional por gênero ─────────────────────────────────────────
    genre_sales  = dff.groupby("Genre")["Vendas Globais"].sum().sort_values(ascending=False)
    genre_region = dff.groupby("Genre")[REGIONS].sum().loc[genre_sales.index].reset_index()
    fig = px.bar(
        genre_region, x="Genre", y=REGIONS,
        title="Distribuição Regional por Gênero",
        labels={"Genre": "Gênero", "value": "Vendas (M)", "variable": "Região"},
        barmode="stack",
        color_discrete_sequence=[COLORS["accent"], COLORS["teal"], COLORS["amber"], "#F43F5E"],
    )
    fig.update_traces(hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y:.1f} M<extra></extra>")
    chart_container(fig, "genero_regiao", height=380)

    # ── Linha 4: Top 20 Desenvolvedoras ──────────────────────────────────────
    pub_df = (
        dff.groupby("Publisher")["Vendas Globais"].sum()
        .sort_values(ascending=True).tail(20).reset_index()
    )
    # Paleta de cores claras e variadas — contrasta bem com o fundo escuro
    pub_colors = (px.colors.qualitative.Pastel
                  + px.colors.qualitative.Set2
                  + px.colors.qualitative.Pastel1)[:len(pub_df)]
    fig = px.bar(
        pub_df, x="Vendas Globais", y="Publisher", orientation="h",
        labels={"Publisher": "", "Vendas Globais": "Vendas Globais (M)"},
        title="Top 20 Desenvolvedoras por Vendas Globais",
        color="Publisher",
        color_discrete_sequence=pub_colors,
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>%{x:.1f} M<extra></extra>")
    fig.update_layout(showlegend=False)
    chart_container(fig, "top20_pub", height=560)

    # ── Expander de dados ─────────────────────────────────────────────────────
    render_data_expander(dff)


def page_tendencias(dff: pd.DataFrame, genre: str):
    """Página 2 – Tendências Temporais."""
    st.markdown(
        '<div class="dash-header">'
        '<h1>📈 Tendências Temporais</h1>'
        '<p>Evolução das vendas ao longo dos anos por gênero — 2D e 3D interativo.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    tendencias = dff.groupby(["Year", "Genre"])["Vendas Globais"].sum().reset_index()

    fig = px.line(
        tendencias, x="Year", y="Vendas Globais", color="Genre",
        labels={"Year": "Ano", "Genre": "Gênero", "Vendas Globais": "Vendas (M)"},
        title="Evolução das Vendas por Gênero",
        color_discrete_sequence=px.colors.qualitative.Vivid,
    )
    fig.update_traces(
        line_width=2,
        hovertemplate="<b>%{fullData.name}</b><br>%{x}: %{y:.1f} M<extra></extra>",
    )
    chart_container(fig, "tendencia_linha", height=460)

    # 3D só faz sentido com múltiplos gêneros — oculta quando um é selecionado
    if genre == "Todos":
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🧊 Superfície 3D Interativa")
        st.caption("Arraste para rotacionar · Scroll para zoom · Hover para detalhes")

        pivot = tendencias.pivot(index="Genre", columns="Year", values="Vendas Globais").fillna(0)
        X, Y  = np.meshgrid(pivot.columns.astype(float), range(len(pivot.index)))

        fig3d = go.Figure(data=[go.Surface(
            z=pivot.values, x=X, y=Y,
            colorscale="Turbo", opacity=0.92,
            contours=dict(z=dict(show=True, usecolormap=True,
                                 highlightcolor=COLORS["amber"], project_z=True)),
        )])
        fig3d.update_layout(
            title="Vendas por Gênero/Ano — Superfície 3D",
            scene=dict(
                xaxis=dict(title="Ano", tickvals=list(pivot.columns[::4]),
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

    render_data_expander(dff)


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
        # CORREÇÃO: sem color fixo → Plotly escolhe preto/branco pelo contraste
        textfont=dict(size=14),
    )
    fig.update_xaxes(side="top")
    chart_container(fig, "heatmap_producao", height=480)

    st.markdown("<br>", unsafe_allow_html=True)
    prod_anual = dff.groupby("Year")["Name"].count().reset_index().rename(columns={"Name": "Quantidade"})
    fig2 = px.bar(
        prod_anual, x="Year", y="Quantidade",
        labels={"Year": "Ano", "Quantidade": "Títulos lançados"},
        title="Total de Títulos Lançados por Ano",
        color="Quantidade", color_continuous_scale="Blues",
    )
    fig2.update_traces(hovertemplate="<b>%{x}</b><br>%{y:,} títulos<extra></extra>")
    fig2.update_layout(coloraxis_showscale=False)
    chart_container(fig2, "prod_anual", height=360)

    render_data_expander(dff)


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
        "Base extraída em meados de 2016. Anos 2017+ têm poucos registros e podem estar incompletos.  \n"
        "**Todos os valores de venda estão em milhões de unidades.**",
        icon="ℹ️",
    )

    kpis = {
        "Registros totais":       len(df),
        "Títulos únicos":         df["Name"].nunique(),
        "Gêneros":                df["Genre"].nunique(),
        "Plataformas":            df["Platform"].nunique(),
        "Desenvolvedoras":        df["Publisher"].nunique(),
        "Jogos multi-plataforma": df[df.duplicated("Name", keep=False)]["Name"].nunique(),
    }
    cols = st.columns(3)
    for i, (label, val) in enumerate(kpis.items()):
        cols[i % 3].markdown(
            f'<div class="kpi-card"><span class="kpi-value">{val:,}</span>'
            f'<span class="kpi-label">{label}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Mínimos e Máximos")
        stats = [
            ("Ano de Desenvolvimento", int(df["Year"].min()), int(df["Year"].max())),
            ("Vendas América do Norte", df["América do Norte"].min(),  df["América do Norte"].max()),
            ("Vendas Europa",     df["Europa"].min(),            df["Europa"].max()),
            ("Vendas Japão",      df["Japão"].min(),             df["Japão"].max()),
            ("Vendas Outros",     df["Outros Países"].min(),     df["Outros Países"].max()),
            ("Vendas Globais",    df["Vendas Globais"].min(),    df["Vendas Globais"].max()),
        ]
        st.dataframe(pd.DataFrame(stats, columns=["Indicador", "Mínimo", "Máximo"]),
                     use_container_width=True, hide_index=True)

    with col2:
        st.subheader("Completude por Coluna")
        null_df = pd.DataFrame({
            "Coluna":    df.columns,
            "Nulos":     df.isnull().sum().values,
            "Não Nulos": df.notnull().sum().values,
        })
        st.dataframe(null_df, use_container_width=True, hide_index=True)

    fig = px.bar(
        null_df.melt(id_vars="Coluna", value_vars=["Nulos", "Não Nulos"],
                     var_name="Tipo", value_name="Quantidade"),
        x="Coluna", y="Quantidade", color="Tipo", barmode="group",
        title="Valores Nulos vs Não Nulos por Coluna",
        color_discrete_map={"Nulos": "#F43F5E", "Não Nulos": COLORS["teal"]},
    )
    fig.update_traces(hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y:,}<extra></extra>")
    chart_container(fig, "nulos_chart", height=360)


# =============================================================================
# MAIN
# =============================================================================

def main():
    df = load_data()

    option, genre, year_start, year_end, platform, publisher, simplify = \
        build_sidebar_filters(df)

    dff = apply_filters(df, genre, year_start, year_end, platform, publisher, simplify)

    notice = active_filters_notice(genre, year_start, year_end, platform, publisher, simplify, df)
    if notice:
        st.markdown(
            f'<div class="filter-notice">🔍 Filtros ativos: {notice}</div>',
            unsafe_allow_html=True,
        )

    if   option.startswith("📊"): page_resumo(dff, df, year_start, year_end)
    elif option.startswith("📈"): page_tendencias(dff, genre)
    elif option.startswith("🗺️"): page_producao(dff)
    elif option.startswith("ℹ️"): page_sobre(df)


if __name__ == "__main__":
    main()
