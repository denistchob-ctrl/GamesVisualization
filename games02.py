import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # necessário para 3D

#https://gamesvisualization-v77moozvxrjfgzckeg5rp3.streamlit.app/
#dados em milhões (vendas)
#NA BASE COMPLETA, RECEM CARREGADA TEMOS AS SEGUINTES CONSIDERAÇÕES:
#jogos com o identificador ALL em console é um agrupado de todas as versoes em outros consoles
#ver o jogo Tekken 8 (all) que teve 3 versoes e cada uma delas tem seus dados também
#talvez seja interessante ignorar os registros que apontam pra esse console
#
#jogos com o identificador SERIES em console é porque o jogo tem uma série de outros jogos em outros consoles, uma linha de jogos com o mesmo nome
#verificar se também devem ser ignorados
#após o titulo, colocar o filtro se houver para que o usuário saiba que os dados estão filtrados ou não.


st.set_page_config(
    page_title="Análise de Dados de Vendas de Jogos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregar dados
@st.cache_data
def load_data():
    df = pd.read_csv("vgsales.csv")
    return df

df = load_data()
df = df.rename(columns={
    "NA_Sales": "América do Norte",
    "EU_Sales": "Europa",
    "JP_Sales": "Japão",
    "Other_Sales": "Outros Países",
    "Global_Sales": "Vendas Globais"
})

# Converter Year para inteiro, mantendo NaN se houver
df = df.replace(["N/A", "Unknown"], np.nan)
df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
# Garantir que Vendas Globais seja numérico
df["Vendas Globais"] = pd.to_numeric(df["Vendas Globais"], errors="coerce")

# Agrupar por plataforma e somar vendas globais
platform_sales = df.groupby("Platform", as_index=False)["Vendas Globais"].sum()

# Menu lateral
st.sidebar.title("Venha explorar os dados de vendas de jogos!")
option = st.sidebar.radio(
    "Escolha o tema:",
    [
        "1. Resumo Integrado",
        "2. Tendências Temporais",
        "3. Produção de Jogos por Ano/Gênero",
        "0. Informações sobre a Base de Dados"
    ]
)
#        "9. Dashboard de Teste",

# --- Filtros na barra lateral ---
# Gênero
genres = df["Genre"].dropna().unique().tolist()
genres.sort()
genres.insert(0, "Todos")
selected_genre = st.sidebar.selectbox("Selecione o gênero:", genres, index=0)

# Ano
years = df["Year"].dropna().unique().tolist()
years.sort()
years.insert(0, "Todos")
selected_year = st.sidebar.selectbox("Selecione o ano de lançamento:", years, index=0)

# Plataforma
platforms = df["Platform"].dropna().unique().tolist()
platforms.sort()
platforms.insert(0, "Todos")
selected_platform = st.sidebar.selectbox("Selecione a plataforma:", platforms, index=0)

# Desenvolvedora/Publisher
publishers = df["Publisher"].dropna().unique().tolist()
publishers.sort()
publishers.insert(0, "Todos")
selected_publisher = st.sidebar.selectbox("Selecione a Desenvolvedora:", publishers, index=0)

# --- Função de filtro combinada ---
def apply_filters(dataframe, genre, year, platform, publisher):
    df_filtered = dataframe.copy()
    if genre != "Todos":
        df_filtered = df_filtered[df_filtered["Genre"] == genre]
    if year != "Todos":
        df_filtered = df_filtered[df_filtered["Year"] == year]
    if platform != "Todos":
        df_filtered = df_filtered[df_filtered["Platform"] == platform]
    if publisher != "Todos":
        df_filtered = df_filtered[df_filtered["Publisher"] == publisher]
    return df_filtered

# --- Aplicar filtros globais ---
df_filtered = apply_filters(df, selected_genre, selected_year, selected_platform, selected_publisher   )

cb_LimparDados = st.sidebar.checkbox('Resumir os Dados')
if cb_LimparDados:
    st.sidebar.write("Foram excluídas as seguintes informações:")
    
    # Excluir registros com campos nulos
    df_filtered = df_filtered.dropna()
    
    # Filtrar apenas plataformas com vendas globais > 100 milhões
    plataformas_validas = (
        df.groupby("Platform")["Vendas Globais"].sum()
        .reset_index()
        .query("`Vendas Globais` > 100")["Platform"].tolist()
    )
    df_filtered = df_filtered[df_filtered["Platform"].isin(plataformas_validas)]
    st.sidebar.write("* Registros com algum campo nulo.")   
    st.sidebar.write("* Registros de consoles com vendas inferiores à 100milhões.")
    st.sidebar.write("* Registros de anos com produção anual inferior à 100 títulos.")
    
    # Calcular produção anual
    producao_anual = df_filtered.groupby("Year")["Name"].count()
    # Selecionar apenas anos com >= 100 títulos
    anos_validos = producao_anual[producao_anual >= 100].index
    df_filtered = df_filtered[df_filtered["Year"].isin(anos_validos)]

# Opção 0 - Informações sobre a Base de dados
if option.startswith("0"):
    st.title("Informações sobre a Base de Dados")
    st.write("A base de dados contém informações sobre vendas de jogos, incluindo detalhes como nome do jogo, plataforma, gênero, desenvolvedora, ano de lançamento e vendas em diferentes regiões." \
    " Ela é amplamente utilizada para análises de mercado e tendências na indústria de jogos.")
    st.write("Base de Dados obtida no website Kaggle (https://www.kaggle.com/datasets/gregorut/videogamesales).")
    st.write("O script para extrair os dados está disponível em https://github.com/GregorUT/vgchartzScrape .")
    st.write("Ele é baseado na biblioteca BeautifulSoup usando Python.")
    st.write("Dois registros foram descartados devido a informações incompletas conforme informações do autor.")
    st.write("Analisando a base, ela foi extraída em meados de 2016. Para 2017 há apenas 3 registros e 2020 apenas 1 registro.")
    st.write("Dito isso, os dados com essa data podem estar com informações incompletas tanto quanto à produção de jogos como de vendas.")
    st.write("** DADOS DE VENDAS ESTÃO NA UNIDADE DE MILHÕES **")
    st.write("Os dados abaixo não estão considerando nenhum filtro aplicado, ou seja, são os totais da base completa.")

    # --- Primeira tabela: Totais ---
    stats_totals = {
        "Total de Registros": len(df),
        "Total de Gêneros": df["Genre"].nunique(),
        "Total de Plataformas": df["Platform"].nunique() if "Platform" in df.columns else 0,
        "Total de Desenvolvedoras": df["Publisher"].nunique() if "Publisher" in df.columns else 0,
        "Total de Jogos multi-plataforma": df[df.duplicated(subset=["Name"], keep=False)]["Name"].nunique()
    }
    stats_totals_df = pd.DataFrame(list(stats_totals.items()), columns=["Indicador", "Valor"])

    # --- Segunda tabela: Mínimos e Máximos ---
    stats_min_max = [
        ("Limites de Ano", df["Year"].min(), df["Year"].max()),
        ("Vendas América do Norte", df["América do Norte"].min(), df["América do Norte"].max()),
        ("Vendas Europa", df["Europa"].min(), df["Europa"].max()),
        ("Vendas Japão", df["Japão"].min(), df["Japão"].max()),
        ("Vendas Outros", df["Outros Países"].min(), df["Outros Países"].max()),
        ("Vendas Globais", df["Vendas Globais"].min(), df["Vendas Globais"].max())
    ]
    stats_min_max_df = pd.DataFrame(stats_min_max, columns=["Indicador", "Mínimo", "Máximo"])

    # --- Exibir lado a lado ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Totais da Base")
        st.dataframe(stats_totals_df)
        st.write("**Observação:** O total de jogos multi-plataforma é uma estimativa baseada em registros duplicados no campo 'Name', indicando que um mesmo jogo foi lançado em múltiplas plataformas.")   

    with col2:
        st.subheader("Mínimos e Máximos")
        st.dataframe(stats_min_max_df)

    # Calcular nulos e não nulos
    null_counts = df.isnull().sum()
    non_null_counts = df.notnull().sum()

    # Organizar em DataFrame
    null_df = pd.DataFrame({
        "Coluna": df.columns,
        "Nulos": null_counts.values,
        "Não Nulos": non_null_counts.values
    })

    # Exibir gráfico interativo
    fig = px.bar(
        null_df.melt(id_vars="Coluna", value_vars=["Nulos", "Não Nulos"],
                    var_name="Tipo", value_name="Quantidade"),
        x="Coluna", y="Quantidade", color="Tipo", barmode="group",
        title="Valores Nulos e Não Nulos por Coluna"
    )
    st.plotly_chart(fig, use_container_width=True)

# Dashboard 1 - Visão Geral
# --- Nova opção: Resumo Integrado ---

# Resumo Integrado
if option.startswith("1"):
    st.title("Resumo Integrado")
    #st.subheader("Vendas, Jogos, Plataformas e Gêneros")

    # --- Preparar os dados ---
    vendas_por_ano = df_filtered.groupby("Year")["Vendas Globais"].sum().reset_index()
    top_jogos = df_filtered.groupby("Name")["Vendas Globais"].sum().nlargest(10).reset_index()
    plataformas = df_filtered.groupby("Platform")["Vendas Globais"].sum().reset_index()
    generos = df_filtered.groupby("Genre")["Vendas Globais"].sum().reset_index()

    # Primeira linha: 2 gráficos lado a lado
    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(6,4))
        
        # Gráfico original
        ax.plot(vendas_por_ano["Year"], vendas_por_ano["Vendas Globais"], marker="o", color="blue", label="Vendas")

        if selected_year == "Todos":
            # Calcular linha de tendência (regressão linear)
            x = vendas_por_ano["Year"]
            y = vendas_por_ano["Vendas Globais"]
            coef = np.polyfit(x, y, 1)  # grau 1 = linha reta
            tendencia = np.poly1d(coef)
    
            # Plotar linha de tendência
            ax.plot(x, tendencia(x), color="red", linestyle="--", label="Tendência")

        ax.set_title("Vendas Globais por Ano")
        ax.set_ylabel("Vendas Totais (em milhões)")
        ax.legend()

        st.pyplot(fig)
    # with col1:
    #     fig, ax = plt.subplots(figsize=(6,4))
    #     ax.plot(vendas_por_ano["Year"], vendas_por_ano["Vendas Globais"], marker="o", color="blue")
    #     ax.set_title("Vendas Globais por Ano")
    #     ax.set_ylabel("Vendas Totais (em milhões)")
    #     st.pyplot(fig)

    with col2:
        fig, ax = plt.subplots(figsize=(6,4))
        cores = plt.cm.tab20.colors
        ax.pie(generos["Vendas Globais"], labels=generos["Genre"], autopct="%1.1f%%", startangle=90, colors=cores)
        ax.set_title("Vendas por Gênero")
        st.pyplot(fig)

    # Segunda linha: 2 gráficos lado a lado
    col3, col4 = st.columns(2)

    with col3:
        fig, ax = plt.subplots(figsize=(6,4))
        cores_auto = plt.cm.rainbow(np.linspace(0, 1, len(plataformas)))
        ax.bar(plataformas["Platform"], plataformas["Vendas Globais"], color=cores_auto)
        ax.set_title("Vendas por Plataforma")
        ax.set_ylabel("Vendas Totais (em milhões)")
        ax.tick_params(axis="x", rotation=90)
        st.pyplot(fig)

    with col4:
        fig, ax = plt.subplots(figsize=(6,4))
        cores_jogos = ["red","blue","green","orange","purple","cyan","magenta","yellow","brown","pink"]
        top_jogos["Name_short"] = top_jogos["Name"].str.slice(0, 30)
        ax.bar(top_jogos["Name_short"] , top_jogos["Vendas Globais"], color=cores_jogos[:len(top_jogos)])
        ax.set_title("Top 10 Jogos Mais Vendidos")
        ax.set_ylabel("Vendas Totais (em milhões)")
        ax.tick_params(axis="x", rotation=90)
        st.pyplot(fig)
        
    # Terceira linha: gráfico ocupando toda a largura
    #st.markdown("Vendas por Gênero/Região")
    regions = ["América do Norte", "Europa", "Japão", "Outros Países"]
    genre_sales = df_filtered.groupby("Genre")["Vendas Globais"].sum().sort_values(ascending=False)
    genre_region = df_filtered.groupby("Genre")[regions].sum()
    genre_region = genre_region.loc[genre_sales.index]
    fig, ax = plt.subplots(figsize=(12,6))
    bottom = np.zeros(len(genre_region))
    for region in regions:
        ax.bar(genre_region.index, genre_region[region], bottom=bottom, label=region, color=cm.tab10(regions.index(region)))
        bottom += genre_region[region].values
    ax.set_title("Vendas por Gênero/Região")
    ax.set_xlabel("Gênero")
    ax.set_ylabel("Vendas Totais (em milhões)")
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    fig.tight_layout()
    st.pyplot(fig)

    # Quarta linha: gráfico ocupando toda a largura
    # Agrupar vendas por desenvolvedora
    publisher_sales = (df_filtered.groupby("Publisher")["Vendas Globais"].sum().sort_values(ascending=False).head(20))
    fig, ax = plt.subplots(figsize=(12,6))
    # Gráfico horizontal (invertendo ordem para mostrar maior no topo)
    ax.barh(publisher_sales.index[::-1], publisher_sales.values[::-1], color=cores_jogos[:len(publisher_sales)])
    ax.set_title("Top 20 Desenvolvedoras por Vendas Globais")
    ax.set_xlabel("Vendas Globais (em milhões)")
    fig.tight_layout()
    st.pyplot(fig)

elif option.startswith("3"):
    st.title("Matriz de Produção de Jogos")
    st.subheader("Análise dos 5 anos com maior produção")
    st.subheader("e os 6 gêneros mais produzidos")

    #montar uma matriz 3 linhas 5 colunas
    #produção por ano (pegar os 5 anos que mais tiveram produção de games)
    #pegar os 6 generos que mais produziram em todo o periodo

    # Top 5 anos com maior produção
    top_years = sorted(df_filtered["Year"].value_counts().nlargest(5).index.tolist())

    # Top 6 gêneros mais produzidos
    top_genres = sorted(df_filtered["Genre"].value_counts().nlargest(6).index.tolist())

    # Criar tabela cruzada (pivot)
    matrix = df_filtered[df_filtered["Year"].isin(top_years) & df_filtered["Genre"].isin(top_genres)]
    pivot = matrix.pivot_table(
        index="Genre", 
        columns="Year", 
        values="Name", 
        aggfunc="count"
    ).reindex(index=top_genres, columns=top_years, fill_value=0)

    # Exibir heatmap
    fig = px.imshow(
        pivot.values,
        labels=dict(x="Ano", y="Gênero", color="Quantidade de Jogos"),
        x=pivot.columns.astype(str),
        y=pivot.index,
        color_continuous_scale="Reds",  # muda a paleta de cores
        text_auto=True  # mostra os valores dentro das células
    )
    # Algumas opções de paletas de cores para o PLOTLY:
    # "Blues" → tons de azul claro a escuro.
    # "Reds" → tons de vermelho.
    # "Greens" → tons de verde.
    # "Viridis" → gradiente moderno, muito usado em ciência de dados.
    # "Cividis" → paleta otimizada para acessibilidade (daltonismo).
    # "Turbo" → cores vibrantes e contrastantes.
    fig.update_xaxes(side="top")
    st.plotly_chart(fig, use_container_width=True)

# Dashboard 7 - Tendências Temporais
elif option.startswith("2"):
    #st.title("Tendências Temporais")
    # Exemplo: evolução de gêneros ao longo dos anos

    tendencias = df_filtered.groupby(["Year", "Genre"])["Vendas Globais"].sum().reset_index()
    fig = px.line(tendencias, x="Year", y="Vendas Globais", color="Genre", 
                  labels={"Year": "Ano de Publicação", "Genre": "Gênero", "Vendas Globais": "Vendas Totais (em milhões)"},
                  title="Evolução das Vendas nos Anos por Gênero")
    st.plotly_chart(fig)

    #opção 2 do mesmo gráfico, mas em 3D interativo
    # --- Preparar os dados ---
    tendencias = df_filtered.groupby(["Year", "Genre"])["Vendas Globais"].sum().reset_index()

    # Criar tabela cruzada (anos x gêneros)
    pivot = tendencias.pivot(index="Genre", columns="Year", values="Vendas Globais").fillna(0)

    # Transformar em arrays
    X, Y = np.meshgrid(pivot.columns, range(len(pivot.index)))
    Z = pivot.values

    # --- Criar gráfico 3D interativo ---
    fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale="Turbo")])

    # Ajustar eixos
    fig.update_layout(
        title="Tendências Temporais",
        scene=dict(
            xaxis=dict(title="Ano", tickvals=list(pivot.columns), ticktext=list(pivot.columns)),
            yaxis=dict(title="Gênero", tickvals=list(range(len(pivot.index))), ticktext=list(pivot.index)),
            zaxis=dict(title="Vendas Totais (em milhões)")
        ),
        autosize=True,
        margin=dict(l=65, r=50, b=65, t=90)
    )

    st.plotly_chart(fig, use_container_width=True)


elif option.startswith("8"):

    #
    #teste com 3d
    #
    #2ª opção do mesmo gráfico, mas em 3D interativo
    # --- Preparar os dados ---
    tendencias = df_filtered.groupby(["Year", "Genre"])["Vendas Globais"].sum().reset_index()

    anos = sorted(tendencias["Year"].dropna().unique())
    generos = sorted(tendencias["Genre"].dropna().unique())

    # Criar tabela cruzada (gêneros x anos)
    pivot = tendencias.pivot(index="Genre", columns="Year", values="Vendas Globais").fillna(0)

    X, Y = np.meshgrid(pivot.columns, range(len(pivot.index)))
    Z = pivot.values

    # --- Gráfico inicial (superfície completa) ---
    fig = go.Figure()

    fig.add_trace(go.Surface(z=Z, x=X, y=Y, colorscale="Viridis"))

    # --- Frames para slider (um ano por vez) ---
    frames = []
    for ano in anos:
        z = pivot[ano].values.reshape(len(generos), 1)
        x = [ano] * len(generos)
        y = list(range(len(generos)))
        frames.append(go.Frame(
            data=[go.Scatter3d(x=x, y=y, z=z.flatten(),
                            mode="markers+lines",
                            marker=dict(size=5, color=z.flatten(), colorscale="Viridis"))],
            name=str(ano)
        ))

    fig.frames = frames

    # --- Layout com slider ---
    fig.update_layout(
        title="Tendências Temporais (Superfície 3D com Slider)",
        scene=dict(
            xaxis=dict(title="Ano", tickvals=list(pivot.columns), ticktext=list(pivot.columns)),
            yaxis=dict(title="Gênero", tickvals=list(range(len(generos))), ticktext=generos),
            zaxis=dict(title="Vendas Totais (em milhões)")
        ),
        sliders=[{
            "steps": [
                {"args": [[str(ano)], {"frame": {"duration": 300, "redraw": True},
                                    "mode": "immediate"}],
                "label": str(ano),
                "method": "animate"} for ano in anos
            ],
            "active": 0,
            "x": 0.1,
            "y": -0.1,
            "len": 0.9
        }]
    )

    st.plotly_chart(fig, use_container_width=True)

elif option.startswith("9"):

    #
    #
    #
    #3ª opção do mesmo gráfico, mas em 3D interativo
    st.write("Em desenvolvimento...")
    
elif option.startswith("teste original"):
    #versão original por enquanto descartada, mas pode ser reaproveitada para um dashboard de teste
    st.title("Resumo Integrado")
    st.subheader("Vendas, Jogos, Plataformas e Gêneros")

    # Gráfico 1 - Vendas Globais por Ano
    vendas_por_ano = df_filtered.groupby("Year")["Vendas Globais"].sum().reset_index()
    fig1 = px.line(vendas_por_ano, x="Year", y="Vendas Globais",
                   labels={"Year": "Ano", "Vendas Globais": "Vendas Totais (em milhões)"},
                   title="Vendas Globais por Ano")

    # Gráfico 2 - Top 10 Jogos
    top_jogos = df_filtered.groupby("Name")["Vendas Globais"].sum().nlargest(10).reset_index()
    fig2 = px.bar(top_jogos, x="Name", y="Vendas Globais",
                  labels={"Name": "Título", "Vendas Globais": "Vendas Totais (em milhões)"},
                  title="Top 10 Jogos Mais Vendidos")

    # Gráfico 3 - Distribuição por Plataformas
    plataformas = df_filtered.groupby("Platform")["Vendas Globais"].sum().reset_index()
    fig3 = px.bar(plataformas, x="Platform", y="Vendas Globais",
                  labels={"Platform": "Plataforma", "Vendas Globais": "Vendas Totais (em milhões)"},
                  title="Vendas por Plataforma")

    # Gráfico 4 - Distribuição por Gênero
    generos = df_filtered.groupby("Genre")["Vendas Globais"].sum().reset_index()
    fig4 = px.pie(generos, names="Genre", values="Vendas Globais",
                  labels={"Genre": "Gênero", "Vendas Globais": "Vendas Totais (em milhões)"},
                  title="Vendas por Gênero")

    # Gráfico 5 - Top 10 Editoras/Desenvolvedoras
    editoras = df_filtered.groupby("Publisher")["Vendas Globais"].sum().nlargest(10).reset_index()
    fig5 = px.bar(editoras, x="Publisher", y="Vendas Globais"
               , labels={"Publisher": "Desenvolvedor", "Vendas Globais": "Vendas Totais (em milhões)"}
               , title="Top 10 Desenvolvedoras")

    # Gráfico 6 - Distribuição Geográfica das Venda
    regioes = pd.DataFrame({
        "Region": ["América do Norte", "Europa", "Japão", "Outros Países"],
        "Sales": [
            df_filtered["América do Norte"].sum(),
            df_filtered["Europa"].sum(),
            df_filtered["Japão"].sum(),
            df_filtered["Outros Países"].sum()
        ]
    })
    fig6 = px.bar(regioes, x="Region", y="Sales" 
               , labels={"Region": "Região", "Sales": "Vendas Totais (em milhões)"}
               , title="Vendas por Região")

    # Layout organizado com proporções
    col1, col2 = st.columns([2, 2])  # col1 mais larga
    with col1:
        st.plotly_chart(fig1, use_container_width=False)
    with col2:
        st.plotly_chart(fig2, use_container_width=False)

    col3, col4 = st.columns([2, 2])  # plataformas precisa de mais espaço
    with col3:
        st.plotly_chart(fig3, use_container_width=True)
    with col4:
        st.plotly_chart(fig4, use_container_width=True)

    col5, col6 = st.columns([2, 2])  # editoras em barra larga, regiões em barra menor
    with col5:
        st.plotly_chart(fig5, use_container_width=True)
    with col6:
        st.plotly_chart(fig6, use_container_width=True)
