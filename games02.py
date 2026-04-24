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

# Opção 0 - Informações sobre a Base de dados
if option.startswith("0"):
    st.title("Informações sobre a Base de Dados")
    print("Base de Dados obtida no website Kaggle")
    print("https://www.kaggle.com/datasets/gregorut/videogamesales")
    print("O script para extrair os dados está disponível em https://github.com/GregorUT/vgchartzScrape .")
    print("Ele é baseado no BeautifulSoup usando Python.")
    print("Há 16.598 registros.")
    print("Dois registros foram descartados devido a informações incompletas.")
    print("Analisando a base, ela foi extraída em meados de 2016, então dados com essa data podem estar com informações incompletas tanto quanto à produção de jogos como de vendas.")
    print("Com base na informação acima os dados de 2016 serão desconsiderados.")
    print("")
    print("")
    print("")

# Dashboard 1 - Visão Geral
elif option.startswith("1"):
    st.title("Visão Geral das Vendas Globais")
    vendas_por_ano = df.groupby("Year")["global_sales"].sum().reset_index()
    fig = px.line(vendas_por_ano, x="Year", y="Global_Sales", 
                  labels={"Year": "Ano", "Global_Sales": "Vendas Totais"}, title="Vendas Globais por Ano")
    st.plotly_chart(fig)

# Dashboard 2 - Top Jogos
elif option.startswith("2"):
    st.title("Top Jogos e Franquias")
    top_jogos = df.groupby("title")["global_sales"].sum().nlargest(10).reset_index()
    fig = px.bar(top_jogos, x="title", y="global_sales", 
                  labels={"title": "Título", "global_sales": "Vendas Totais"}, title="Top 10 Jogos Mais Vendidos")
    st.plotly_chart(fig)

# Dashboard 3 - Plataformas
elif option.startswith("3"):
    st.title("Distribuição por Plataformas")
    plataformas = df.groupby("console")["global_sales"].sum().reset_index()
    fig = px.bar(plataformas, x="console", y="global_sales", 
                  labels={"console": "Console", "global_sales": "Vendas Totais"}, title="Vendas por Plataforma")
    st.plotly_chart(fig)

# Dashboard 4 - Gênero
elif option.startswith("4"):
    st.title("Análise por Gênero")
    generos = df.groupby("genre")["global_sales"].sum().reset_index()
    fig = px.pie(generos, names="genre", values="global_sales", 
                  labels={"genre": "Gênero", "global_sales": "Vendas Totais"}, title="Distribuição por Gênero")
    st.plotly_chart(fig)

# Dashboard 5 - Editoras
elif option.startswith("5"):
    st.title("Editoras e Desenvolvedoras")
    editoras = df.groupby("publisher")["global_sales"].sum().nlargest(10).reset_index()
    fig = px.bar(editoras, x="publisher", y="global_sales", 
                  labels={"publisher": "Desenvolvedor", "global_sales": "Vendas Totais"}, title="Top 10 Desenvolvedoras")
    st.plotly_chart(fig)

# Dashboard 6 - Mapa Interativo
elif option.startswith("6"):
    st.title("Distribuição Geográfica das Vendas")

    regioes = pd.DataFrame({
        "Region": ["América do Norte", "Europa", "Japão", "Resto do Mundo"],
        "Sales": [
            df["na_sales"].sum(),
            df["eu_sales"].sum(),
            df["jp_sales"].sum(),
            df["other_sales"].sum()
        ]
    })

    fig = px.bar(regioes, x="Region", y="Sales", 
                  labels={"Region": "Região", "Sales": "Vendas Totais"}, title="Vendas por Região")
    st.plotly_chart(fig)

# Dashboard 7 - Tendências Temporais
elif option.startswith("7"):
    st.title("Tendências Temporais")
    # Exemplo: evolução de gêneros ao longo dos anos

    tendencias = df.groupby(["year", "genre"])["global_sales"].sum().reset_index()
    fig = px.line(tendencias, x="year", y="global_sales", color="genre", 
                  labels={"year": "Ano", "genre": "Gênero", "global_sales": "Vendas Totais"},
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


