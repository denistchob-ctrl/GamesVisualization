import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
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


# Carregar dados
@st.cache_data
def load_data():
    df = pd.read_csv("vgsales.csv")
    return df

df = load_data()
# Converter Year para inteiro, mantendo NaN se houver
df = df.replace(["N/A", "Unknown"], np.nan)
df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
# Garantir que Global_Sales seja numérico
df["Global_Sales"] = pd.to_numeric(df["Global_Sales"], errors="coerce")

# Agrupar por plataforma e somar vendas globais
platform_sales = df.groupby("Platform", as_index=False)["Global_Sales"].sum()

# Menu lateral
st.sidebar.title("Menu de Dashboards\n Ver valores sua dimensão está correta\nPermitir seleção")
option = st.sidebar.radio(
    "Escolha o tema:",
    [
        "1. Resumo Integrado",
        "2. Tendências Temporais",
        "3. Produção de Jogos por Ano/Gênero",
        "4. Dados Gerais da Base de Dados",
        "8. teste 3d",
        "9. teste 3d com slider",
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

# --- Função de filtro combinada ---
def apply_filters(dataframe, genre, year, platform):
    df_filtered = dataframe.copy()
    if genre != "Todos":
        df_filtered = df_filtered[df_filtered["Genre"] == genre]
    if year != "Todos":
        df_filtered = df_filtered[df_filtered["Year"] == year]
    if platform != "Todos":
        df_filtered = df_filtered[df_filtered["Platform"] == platform]
    return df_filtered

# --- Aplicar filtros globais ---
df_filtered = apply_filters(df, selected_genre, selected_year, selected_platform)

cb_LimparDados = st.sidebar.checkbox('Resumir os Dados')
if cb_LimparDados:
    st.sidebar.write("Foram excluídas as informações redundantes da base de dados.")
    
    # Excluir registros com campos nulos
    df_filtered = df_filtered.dropna()
    st.sidebar.write("Foram excluídos os registros que tenham algum campo nulo.")   
    
    # Filtrar apenas plataformas com vendas globais > 100 milhões
    plataformas_validas = (
        df.groupby("Platform")["Global_Sales"].sum()
        .reset_index()
        .query("Global_Sales > 100")["Platform"].tolist()
    )
    df_filtered = df_filtered[df_filtered["Platform"].isin(plataformas_validas)]
    st.sidebar.write("Foram excluídos os consoles cujas vendas não ultrapassaram 100 milhões.")

# Opção 0 - Informações sobre a Base de dados
if option.startswith("0"):
    st.title("Informações sobre a Base de Dados")
    st.write("Base de Dados obtida no website Kaggle")
    st.write("https://www.kaggle.com/datasets/gregorut/videogamesales")
    st.write("O script para extrair os dados está disponível em https://github.com/GregorUT/vgchartzScrape .")
    st.write("Ele é baseado na biblioteca BeautifulSoup usando Python.")
    st.write("Há 16.598 registros.")
    st.write("Dois registros foram descartados devido a informações incompletas.")
    st.write("Analisando a base, ela foi extraída em meados de 2016, então dados com essa data podem estar com informações incompletas tanto quanto à produção de jogos como de vendas.")
    st.write("Com base na informação acima os dados de 2016 serão desconsiderados.")
    st.write("")
    st.write("DADOS DE VENDAS ESTÃO NA UNIDADE DE MILHÕES")
    st.write("")

# Dashboard 1 - Visão Geral
# --- Nova opção: Resumo Integrado ---
if option.startswith("teste original"):
    #versão original por enquanto descartada, mas pode ser reaproveitada para um dashboard de teste
    st.title("Resumo Integrado")
    st.subheader("Vendas, Jogos, Plataformas e Gêneros")

    # Gráfico 1 - Vendas Globais por Ano
    vendas_por_ano = df_filtered.groupby("Year")["Global_Sales"].sum().reset_index()
    fig1 = px.line(vendas_por_ano, x="Year", y="Global_Sales",
                   labels={"Year": "Ano", "Global_Sales": "Vendas Totais (em milhões)"},
                   title="Vendas Globais por Ano")

    # Gráfico 2 - Top 10 Jogos
    top_jogos = df_filtered.groupby("Name")["Global_Sales"].sum().nlargest(10).reset_index()
    fig2 = px.bar(top_jogos, x="Name", y="Global_Sales",
                  labels={"Name": "Título", "Global_Sales": "Vendas Totais (em milhões)"},
                  title="Top 10 Jogos Mais Vendidos")

    # Gráfico 3 - Distribuição por Plataformas
    plataformas = df_filtered.groupby("Platform")["Global_Sales"].sum().reset_index()
    fig3 = px.bar(plataformas, x="Platform", y="Global_Sales",
                  labels={"Platform": "Plataforma", "Global_Sales": "Vendas Totais (em milhões)"},
                  title="Vendas por Plataforma")

    # Gráfico 4 - Distribuição por Gênero
    generos = df_filtered.groupby("Genre")["Global_Sales"].sum().reset_index()
    fig4 = px.pie(generos, names="Genre", values="Global_Sales",
                  labels={"Genre": "Gênero", "Global_Sales": "Vendas Totais (em milhões)"},
                  title="Vendas por Gênero")

    # Gráfico 5 - Top 10 Editoras/Desenvolvedoras
    editoras = df_filtered.groupby("Publisher")["Global_Sales"].sum().nlargest(10).reset_index()
    fig5 = px.bar(editoras, x="Publisher", y="Global_Sales"
               , labels={"Publisher": "Desenvolvedor", "Global_Sales": "Vendas Totais (em milhões)"}
               , title="Top 10 Desenvolvedoras")

    # Gráfico 6 - Distribuição Geográfica das Venda
    regioes = pd.DataFrame({
        "Region": ["América do Norte", "Europa", "Japão", "Resto do Mundo"],
        "Sales": [
            df_filtered["NA_Sales"].sum(),
            df_filtered["EU_Sales"].sum(),
            df_filtered["JP_Sales"].sum(),
            df_filtered["Other_Sales"].sum()
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

# Resumo Integrado
elif option.startswith("1"):
    st.title("Resumo Integrado")
    st.subheader("Vendas, Jogos, Plataformas e Gêneros")

    # --- Preparar os dados ---
    vendas_por_ano = df_filtered.groupby("Year")["Global_Sales"].sum().reset_index()
    top_jogos = df_filtered.groupby("Name")["Global_Sales"].sum().nlargest(10).reset_index()
    plataformas = df_filtered.groupby("Platform")["Global_Sales"].sum().reset_index()
    generos = df_filtered.groupby("Genre")["Global_Sales"].sum().reset_index()

    # --- Criar subplots 2x2 ---
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    ax1, ax2, ax3, ax4 = axes.flatten()

    # Gráfico 1 - Vendas Globais por Ano (linha azul)
    ax1.plot(vendas_por_ano["Year"], vendas_por_ano["Global_Sales"], marker="o", color="blue")
    ax1.set_title("Vendas Globais por Ano")
    ax1.set_xlabel("")
    ax1.set_ylabel("Vendas Totais (em milhões)")

    # Gráfico 2 - Top 10 Jogos (barras vermelhas)
    ax4.bar(top_jogos["Name"], top_jogos["Global_Sales"], color="red")
    ax4.set_title("Top 10 Jogos Mais Vendidos")
    ax4.set_xlabel("")
    ax4.set_ylabel("Vendas Totais (em milhões)")
    ax4.tick_params(axis="x", rotation=45)

    # Gráfico 3 - Distribuição por Plataformas (barras verdes)
    ax3.bar(plataformas["Platform"], plataformas["Global_Sales"], color="green")
    ax3.set_title("Vendas por Plataforma")
    ax3.set_xlabel("")
    ax3.set_ylabel("Vendas Totais (em milhões)")
    ax3.tick_params(axis="x", rotation=45)

    # Gráfico 4 - Distribuição por Gênero (pizza colorida)
    cores = plt.cm.tab20.colors  # paleta de cores variadas
    ax2.pie(generos["Global_Sales"], labels=generos["Genre"], autopct="%1.1f%%", startangle=90, colors=cores)
    ax2.set_title("Vendas por Gênero")

    # Ajustar layout
    #fig.tight_layout()
    st.pyplot(fig)

elif option.startswith("3"):
    st.title("Matriz de Produção de Jogos")
    st.subheader("Análise dos 5 anos com maior produção")
    st.subheader("e os 6 gêneros mais produzidos")

    #montar uma matriz 3 linhas 5 colunas
    #produção por ano (pegar os 5 anos que mais tiveram produção de games)
    #pegar os 6 generos que mais produziram em todo o periodo

    # Top 5 anos com maior produção
    top_years = sorted(df["Year"].value_counts().nlargest(5).index.tolist())

    # Top 6 gêneros mais produzidos
    top_genres = sorted(df["Genre"].value_counts().nlargest(6).index.tolist())

    # Criar tabela cruzada (pivot)
    matrix = df[df["Year"].isin(top_years) & df["Genre"].isin(top_genres)]
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

elif option.startswith("4"):
    st.title("Dados Gerais da Base de Dados")
    # --- Primeira tabela: Totais ---
    stats_totals = {
        "Total de Registros": len(df),
        "Total de Gêneros": df["Genre"].nunique(),
        "Total de Consoles": df["Console"].nunique() if "Console" in df.columns else 0,
        "Total de Plataformas": df["Platform"].nunique() if "Platform" in df.columns else 0
    }
    stats_totals_df = pd.DataFrame(list(stats_totals.items()), columns=["Indicador", "Valor"])

    # --- Segunda tabela: Mínimos e Máximos ---
    stats_min_max = [
        ("Produção por Ano", df["Year"].min(), df["Year"].max()),
        ("Vendas América do Norte", df["NA_Sales"].min(), df["NA_Sales"].max()),
        ("Vendas Europa", df["EU_Sales"].min(), df["EU_Sales"].max()),
        ("Vendas Japão", df["JP_Sales"].min(), df["JP_Sales"].max()),
        ("Vendas Outros", df["Other_Sales"].min(), df["Other_Sales"].max()),
        ("Vendas Globais", df["Global_Sales"].min(), df["Global_Sales"].max())
    ]
    stats_min_max_df = pd.DataFrame(stats_min_max, columns=["Indicador", "Mínimo", "Máximo"])

    # --- Exibir lado a lado ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Totais da Base")
        st.dataframe(stats_totals_df)

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

# Dashboard 7 - Tendências Temporais
elif option.startswith("2"):
    #st.title("Tendências Temporais")
    # Exemplo: evolução de gêneros ao longo dos anos

    tendencias = df_filtered.groupby(["Year", "Genre"])["Global_Sales"].sum().reset_index()
    fig = px.line(tendencias, x="Year", y="Global_Sales", color="Genre", 
                  labels={"Year": "Ano de Publicação", "Genre": "Gênero", "Global_Sales": "Vendas Totais (em milhões)"},
                  title="Evolução das Vendas nos Anos por Gênero")
    st.plotly_chart(fig)

    #opção 2 do mesmo gráfico, mas em 3D interativo
    # --- Preparar os dados ---
    tendencias = df_filtered.groupby(["Year", "Genre"])["Global_Sales"].sum().reset_index()

    # Criar tabela cruzada (anos x gêneros)
    pivot = tendencias.pivot(index="Genre", columns="Year", values="Global_Sales").fillna(0)

    # Transformar em arrays
    X, Y = np.meshgrid(pivot.columns, range(len(pivot.index)))
    Z = pivot.values

    # --- Criar gráfico 3D interativo ---
    fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale="Viridis")])

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
    #
    #
    #2ª opção do mesmo gráfico, mas em 3D interativo
    # --- Preparar os dados ---
    tendencias = df_filtered.groupby(["Year", "Genre"])["Global_Sales"].sum().reset_index()

    anos = sorted(tendencias["Year"].dropna().unique())
    generos = sorted(tendencias["Genre"].dropna().unique())

    # Criar tabela cruzada (gêneros x anos)
    pivot = tendencias.pivot(index="Genre", columns="Year", values="Global_Sales").fillna(0)

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
