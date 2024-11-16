# importar as bibliotecas
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import timedelta

# criar as funções de carregamento de dados
@st.cache_data
def carregar_dados(empresas):
    texto_tickers = ' '.join(empresas)
    dados_acao = yf.Tickers(texto_tickers)
    cotacao_acao = dados_acao.history(period='1d', start='2020-01-01', end= '2024-11-16')['Close']
    return(cotacao_acao)

@st.cache_data
def carregar_ticker():
    base_tickers = pd.read_csv('ticket_ibra.csv', sep=';')
    tickers = list(base_tickers['Código'])
    #print(tickers)
    tickers = [t + ".SA" for t in tickers]
    return tickers

acoes = carregar_ticker()
dados = carregar_dados(acoes)

# st.write(acoes)

# criar a interface
st.header('App Preço de Ações')
st.write('O gráfico abaixo representa a evolução do preço das ações ao longo do anos.')

# preparar as visualizações = filtros
st.sidebar.header('Filtros')

#filtro de ações
lista_acoes = st.sidebar.multiselect("Escolha os ativos", dados.columns, placeholder="Choose an option")
if lista_acoes:
    dados = dados[lista_acoes]
    if len(lista_acoes)==1:
        acao_unica = lista_acoes[0]
        dados = dados.rename(columns={acao_unica: "Close"})

#filtro de datas
data_inicial = dados.index.min().to_pydatetime()
data_final = dados.index.max().to_pydatetime()
intervalo = st.sidebar.slider("Selecione o período",
                                min_value=data_inicial,
                                max_value=data_final,
                                value=(data_inicial, data_final),
                                step=timedelta(days=15))

dados = dados.loc[intervalo[0]:intervalo[1]]

#st.write(dados)

if len(lista_acoes) >= 1:
    st.line_chart(dados)

# Cálculo de perfomance
texto_performance_ativos = " "

if len(lista_acoes)==0:
    lista_acoes = list(dados.columns)
elif len(lista_acoes)==1:
    dados = dados.rename(columns={"Close": acao_unica})

carteira = [1000 for acao in lista_acoes]
total_inicial_carteira = sum(carteira)

for i, acao in enumerate(lista_acoes):
    performance_ativo = dados[acao].iloc[-1]/dados[acao].iloc[0]-1
    performance_ativo = float(performance_ativo)

    carteira[i] = carteira[i] * (1 + performance_ativo)

    if performance_ativo > 0:
        texto_performance_ativos = texto_performance_ativos + f"  \n{acao}: :blue[{performance_ativo:.1%}]"
    elif performance_ativo < 0:
        texto_performance_ativos = texto_performance_ativos + f"  \n{acao}: :red[{performance_ativo:.1%}]"
    else:
        texto_performance_ativos = texto_performance_ativos + f"  \n{acao}: {performance_ativo:.1%}"

total_final_carteira = sum(carteira)
performance_carteira = total_final_carteira/total_inicial_carteira -1

if performance_carteira > 0:
    texto_performance_carteira = f"Performance da carteira com todos os ativos: :blue[{performance_carteira:.1%}]"
elif performance_carteira < 0:
    texto_performance_carteira = f"Performance da carteira com todos os ativos: :red[{performance_carteira:.1%}]"
else:
    texto_performance_carteira = f"Performance da carteira com todos os ativos: [{performance_carteira:.1%}]"

st.write(f"""
### Performance dos Ativos
Essa foi a performance de cada ativo no período selecionado:

{texto_performance_ativos}

{texto_performance_carteira}

""")