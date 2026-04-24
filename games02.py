import streamlit as st
import pandas as pd
import plotly.express as px


# Carregar dados
@st.cache_data
def load_data():
    df = pd.read_csv("vgsales.csv")
    return df

df = load_data()

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

# Função auxiliar para aplicar filtro
def filter_by_genre(dataframe, genre):
    if genre == "Todos":
        return dataframe
    else:
        return dataframe[dataframe["Genre"] == genre]

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
    st.write("Ele é baseado no BeautifulSoup usando Python.")
    st.write("Há 16.598 registros.")
    st.write("Dois registros foram descartados devido a informações incompletas.")
    st.write("Analisando a base, ela foi extraída em meados de 2016, então dados com essa data podem estar com informações incompletas tanto quanto à produção de jogos como de vendas.")
    st.write("Com base na informação acima os dados de 2016 serão desconsiderados.")
    st.write("")
    st.write("DADOS DE VENDAS ESTÃO NA UNIDADE DE MILHOES")
    st.write("")

# Dashboard 1 - Visão Geral
elif option.startswith("1"):
    st.title("Vendas Globais de Jogos de Video Games")
    df_filtered = filter_by_genre(df, selected_genre)
    vendas_por_ano = df_filtered.groupby("Year")["Global_Sales"].sum().reset_index()
    fig = px.line(vendas_por_ano, x="Year", y="Global_Sales", 
                  labels={"Year": "Ano", "Global_Sales": "Vendas Totais"}, title="Vendas Globais por Ano")
    st.plotly_chart(fig)

# Dashboard 2 - Top Jogos
elif option.startswith("2"):
    st.title("Top Jogos e Franquias")
    top_jogos = df_filtered.groupby("Name")["Global_Sales"].sum().nlargest(10).reset_index()
    fig = px.bar(top_jogos, x="Name", y="Global_Sales", 
                  labels={"Name": "Título", "Global_Sales": "Vendas Totais"}, title="Top 10 Jogos Mais Vendidos")
    st.plotly_chart(fig)

# Dashboard 3 - Plataformas
elif option.startswith("3"):
    st.title("Distribuição por Plataformas")
    plataformas = df_filtered.groupby("Platform")["Global_Sales"].sum().reset_index()
    fig = px.bar(plataformas, x="Platform", y="Global_Sales", 
                  labels={"Platform": "Platform", "Global_Sales": "Vendas Totais"}, title="Vendas por Plataforma")
    st.plotly_chart(fig)

# Dashboard 4 - Gênero
elif option.startswith("4"):
    st.title("Análise por Gênero")
    generos = df_filtered.groupby("Genre")["Global_Sales"].sum().reset_index()
    fig = px.pie(generos, names="Genre", values="Global_Sales", 
                  labels={"Genre": "Gênero", "Global_Sales": "Vendas Totais"}, title="Distribuição por Gênero")
    st.plotly_chart(fig)

# Dashboard 5 - Editoras
elif option.startswith("5"):
    st.title("Editoras e Desenvolvedoras")
    editoras = df_filtered.groupby("Publisher")["Global_Sales"].sum().nlargest(10).reset_index()
    fig = px.bar(editoras, x="Publisher", y="Global_Sales", 
                  labels={"Publisher": "Desenvolvedor", "Global_Sales": "Vendas Totais"}, title="Top 10 Desenvolvedoras")
    st.plotly_chart(fig)

# Dashboard 6 - Mapa Interativo
elif option.startswith("6"):
    st.title("Distribuição Geográfica das Vendas")

    regioes = pd.DataFrame({
        "Region": ["América do Norte", "Europa", "Japão", "Resto do Mundo"],
        "Sales": [
            df_filtered["NA_Sales"].sum(),
            df_filtered["EU_Sales"].sum(),
            df_filtered["JP_Sales"].sum(),
            df_filtered["Other_Sales"].sum()
        ]
    })

    fig = px.bar(regioes, x="Region", y="Sales", 
                  labels={"Region": "Região", "Sales": "Vendas Totais"}, title="Vendas por Região")
    st.plotly_chart(fig)

# Dashboard 7 - Tendências Temporais
elif option.startswith("7"):
    st.title("Tendências Temporais")
    # Exemplo: evolução de gêneros ao longo dos anos

    tendencias = df_filtered.groupby(["Year", "Genre"])["Global_Sales"].sum().reset_index()
    fig = px.line(tendencias, x="Year", y="Global_Sales", color="Genre", 
                  labels={"Year": "Ano", "Genre": "Gênero", "Global_Sales": "Vendas Totais"},
                  title="Evolução das Vendas por Gênero")
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
    st.title("Teste 2")


