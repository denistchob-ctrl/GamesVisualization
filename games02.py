import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

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
df = df.replace(["N/A", "Unknow"], np.nan)
df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")

# Menu lateral
st.sidebar.title("Menu de Dashboards\n Ver valores sua dimensão está correta\nPermitir seleção")
option = st.sidebar.radio(
    "Escolha o tema:",
    [
        "1. Visão Geral das Vendas Globais",
        "2. Top Jogos e Franquias",
        "3. Distribuição por Plataformas",
        "4. Análise por Gênero",
        "5. Editoras e Desenvolvedoras",
        "6. Vendas por Região",
        "7. Tendências Temporais",
        "8. Teste de Gráfico",
        "9. Teste 2",
        "0. Informações sobre a Base de Dados"
    ]
)

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
if not cb_LimparDados:
    st.sidebar.write("")
else:
    st.sidebar.write("Foram excluidas as informações redundantes da base de dados.")

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
    st.write("...")
    st.write("")

    st.write (df_filtered.describe(include="O"))
    st.write(df.isnull().sum())

# Dashboard 1 - Visão Geral
elif option.startswith("1"):
    #st.title("Vendas Globais de Jogos de Video Games")
    vendas_por_ano = df_filtered.groupby("Year")["Global_Sales"].sum().reset_index()
    fig = px.line(vendas_por_ano, x="Year", y="Global_Sales"
                , labels={"Year": "Ano de Publicação do Jogo", "Global_Sales": "Vendas Totais (em milhões)"}
                , title="Vendas Globais de Jogos de Video Games por Ano")
    st.plotly_chart(fig)

# Dashboard 2 - Top Jogos
elif option.startswith("2"):
    #st.title("Top Jogos e Franquias")
    top_jogos = df_filtered.groupby("Name")["Global_Sales"].sum().nlargest(10).reset_index()
    fig = px.bar(top_jogos, x="Name", y="Global_Sales"
               , labels={"Name": "Título do Jogo", "Global_Sales": "Vendas Totais (em milhões)"}
               , title="Top 10 Jogos Mais Vendidos")
    st.plotly_chart(fig)

# Dashboard 3 - Plataformas
elif option.startswith("3"):
    #st.title("Distribuição por Plataformas")
    plataformas = df_filtered.groupby("Platform")["Global_Sales"].sum().reset_index()
    fig = px.bar(plataformas, x="Platform", y="Global_Sales"
               , labels={"Platform": "Plataforma do Jogo", "Global_Sales": "Vendas Totais (em milhões)"}
               , title="Distribuição de Vendas por Plataforma")
    st.plotly_chart(fig)

# Dashboard 4 - Gênero
elif option.startswith("4"):
    #st.title("Análise por Gênero")
    generos = df_filtered.groupby("Genre")["Global_Sales"].sum().reset_index()
    fig = px.pie(generos, names="Genre", values="Global_Sales"
               , labels={"Genre": "Gênero", "Global_Sales": "Vendas Totais (em milhões)"}
               , title="Distribuição de Vendas por Gênero")
    st.plotly_chart(fig)

# Dashboard 5 - Editoras
elif option.startswith("5"):
    #st.title("Editoras e Desenvolvedoras")
    editoras = df_filtered.groupby("Publisher")["Global_Sales"].sum().nlargest(10).reset_index()
    fig = px.bar(editoras, x="Publisher", y="Global_Sales"
               , labels={"Publisher": "Desenvolvedor", "Global_Sales": "Vendas Totais (em milhões)"}
               , title="Top 10 Desenvolvedoras")
    st.plotly_chart(fig)

# Dashboard 6 - Mapa Interativo
elif option.startswith("6"):
    #st.title("Distribuição Geográfica das Vendas")

    regioes = pd.DataFrame({
        "Region": ["América do Norte", "Europa", "Japão", "Resto do Mundo"],
        "Sales": [
            df_filtered["NA_Sales"].sum(),
            df_filtered["EU_Sales"].sum(),
            df_filtered["JP_Sales"].sum(),
            df_filtered["Other_Sales"].sum()
        ]
    })

    fig = px.bar(regioes, x="Region", y="Sales" 
               , labels={"Region": "Região", "Sales": "Vendas Totais (em milhões)"}
               , title="Distribuição Geográfica das Vendas por Região")
    st.plotly_chart(fig)

# Dashboard 7 - Tendências Temporais
elif option.startswith("7"):
    #st.title("Tendências Temporais")
    # Exemplo: evolução de gêneros ao longo dos anos

    tendencias = df_filtered.groupby(["Year", "Genre"])["Global_Sales"].sum().reset_index()
    fig = px.line(tendencias, x="Year", y="Global_Sales", color="Genre", 
                  labels={"Year": "Ano de Publicação", "Genre": "Gênero", "Global_Sales": "Vendas Totais (em milhões)"},
                  title="Evolução das Vendas nos Anos por Gênero")
    st.plotly_chart(fig)

elif option.startswith("8"):
    st.title("Teste\n Mostrar aqui os 5 anos que mais produziram games\ne 3 linhas com os gêneros que mais tiveram games produzidos")

    data=[[1, 25, 30, 50, 1], [20, 1, 60, 80, 30], [30, 60, 1, 5, 20]]
    #montar uma matriz 3 linhas 5 colunas
    #produção por ano (pegar os 5 anos que mais tiveram produção de games)
    #pegar os 3 generos que mais produziram em todo o periodo
    fig = px.imshow(data,
                    labels=dict(x="Day of Week", y="Time of Day", color="Productivity"),
                    x=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                    y=['Morning', 'Afternoon', 'Evening']
                )
    fig.update_xaxes(side="top")
    fig.show()

elif option.startswith("9"):
    st.title("Dados Nulos e Não Nulos por Coluna")
    null_counts = df.isnull().sum()
    non_null_counts = df.notnull().sum()

    null_df = pd.DataFrame({
        "Nulos": null_counts,
        "Não Nulos": non_null_counts
    })

    plt.style.use("seaborn-v0_8")
    ax = null_df.plot(kind="bar", figsize=(12, 6), rot=45)
    plt.title("Contagem de Valores Nulos e Não Nulos por Coluna")
    plt.ylabel("Quantidade de Registros")
    plt.xlabel("Colunas")
    plt.tight_layout()
    plt.show()


