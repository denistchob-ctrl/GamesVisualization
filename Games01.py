from mpl_toolkits.mplot3d import Axes3D
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt # plotting
import numpy as np # linear algebra
import os # accessing directory structure
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import streamlit as st

#campos da base de dados
#Rank,Name,Platform,Year,Genre,Publisher,NA_Sales,EU_Sales,JP_Sales,Other_Sales,Global_Sales
#     Column        Non-Null Count  Dtype     Conteúdo  
#---  ------        --------------  -----   ----------------- 
# 0   Rank          16598 non-null  int64   Ranking of overall sales
# 1   Name          16598 non-null  str     The games name
# 2   Platform      16598 non-null  str     Platform of the games release (i.e. PC,PS4, etc.)
# 3   Year          16327 non-null  float64 Year of the game's release
# 4   Genre         16598 non-null  str     Genre of the game
# 5   Publisher     16540 non-null  str     Publisher of the game
# 6   NA_Sales      16598 non-null  float64 Sales in North America (in millions)
# 7   EU_Sales      16598 non-null  float64 Sales in Europe (in millions)
# 8   JP_Sales      16598 non-null  float64 Sales in Japan (in millions)
# 9   Other_Sales   16598 non-null  float64 Sales in the rest of the world (in millions)
# 10  Global_Sales  16598 non-null  float64 Total worldwide sales.

#python -m streamlit run Games01.py
#https://rknagao.medium.com/streamlit-101-o-b%C3%A1sico-para-colocar-seu-projeto-no-ar-38a71bd641eb

df = pd.read_csv('vgsales.csv')

subset_Plataforma = df[['Platform', 'Name', 'NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales', 'Global_Sales']]
subset_Ano = df[['Year', 'Name', 'NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales', 'Global_Sales']]
subset_Genero = df[['Genre', 'Name', 'NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales', 'Global_Sales']]
subset_Publisher = df[['Publisher', 'Name', 'NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales', 'Global_Sales']]


# Remover valores muito altos que distorcem o gráfico
# Usar a média da coluna como limite
#limite = subset['2022 Population'].mean()
#subset_filtrado = subset[subset['2022 Population'] <= limite]

st.dataframe(subset_Plataforma)
#st.bar_chart(subset_Plataforma.set_index('Platform')['Global_Sales'])

#Diferentes tamanhos de texto
st.title('Isso é um título')
st.header('Isso é um cabeçalho')
st.subheader('Isso é um subcabeçalho')
st.text('Isso é um texto normal')
#formatação
st.markdown('Texto em **negrito** ou _itálico_')
#Utilização para guardar html
st.markdown('[Isso é um texto com html](https://docs.streamlit.io/en/stable/api.html#display-text)',False)

