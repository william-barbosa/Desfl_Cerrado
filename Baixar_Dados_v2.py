################################################################################
## Rotina criada por William Barbosa para o download dos dados do censo       ##
## agropecuário 2017/2018 atualizados                                         ##
################################################################################
import pandas as pd
import numpy as np
#import sidrapy
import time
import requests
from functools import reduce
from termcolor import colored
# pd.set_option('display.width', 200)
pd.set_option('display.max_columns', None)

# Função utilizada para agregação
def categorizacao_uso_terra(x):
    if x in ['2. Non Forest Natural Formation','4. Non Vegetated Area','5. Water','6. Non Observed']:
        return 'Outros'
    else:
        return x

# Função para realizar um left join entre dois DataFrames com base na coluna 'id'
def left_join(df_left, df_right):
    return pd.merge(df_left, df_right, on='geocode', how='left')

# Função para baixar os dados a partir do API do SIDRA
def baixa_dados(url):
    try:
        requisicao = requests.get(url)  # Realizar a requisição
        requisicao.raise_for_status()   # Levantar um erro para códigos de status HTTP ruins
        data = requisicao.json()        # Converter para JSON
        df = pd.DataFrame.from_dict(data)  # Converter para DataFrame
        df.columns = df.iloc[0]  # Renomeando as colunas
        result_df = df.iloc[1:, :]    # Retornar o dataset, excluindo a primeira linha
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar dados: {e} com a URL: {url}")
        result_df = pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro

    return result_df

# Importa a lista de municipios
Cerrado = pd.read_excel('./Dados_V2/tabela_geral_mapbiomas_col8_biomas_municipios.xlsx',sheet_name='COBERTURA_COL8.0')

# Cria o código de UF
UF = pd.DataFrame(data=Cerrado['geocode'].unique(), columns=['geocode'])\
  .query("geocode not in [3520400, 2605459,4300001,4300002]")

UF['UF'] = UF['geocode'].astype(str).str[:2].astype(int)

#UF = UF.head(20)


# Função para processar o DataFrame UF e retornar o DataFrame final combinado
def processa_uf(UF, tabela,api):
    dfg = []
    urls = []
    cod_uf = []
    dados = []

    # Gerar todas as URLs necessárias
    for i in np.unique(UF['UF']):
        geocodes_list = UF.query(f"UF == {i}")['geocode'].astype(str).tolist()
        # Verificar se o comprimento de geocodes_list é maior do que 500
        if len(geocodes_list) > 500:
            print(colored(f"Dividindo geocodes para UF {i} devido ao tamanho excessivo", 'red'))
            mid_index = len(geocodes_list) // 2
            sublists = [geocodes_list[:mid_index], geocodes_list[mid_index:]]
        else:
            sublists = [geocodes_list]

        for sublist in sublists:
            geocodes = ','.join(sublist)
            url = f'https://apisidra.ibge.gov.br/values/t/{tabela}/n6/{geocodes}{api}'

            uf = pd.Series(geocodes).astype(str).str[:2].astype(int).unique()[0]
            #print(colored(f"Baixando os dados para a UF: {uf}", 'blue'))
            start_time = time.time()  # Inicia o cronômetro
            d = baixa_dados(url)
            elapsed_time = time.time() - start_time
            print(colored(f"Tempo para baixar a UF: {uf} foi {elapsed_time:.2f} segundos", 'green'))
            dados.append(d)

    return pd.concat(dados, ignore_index=True)

# Tabela 6852 - Agrotóxico - Fez uso de agrotóxico
# https://apisidra.ibge.gov.br/values/t/6852/n6/1100015/v/all/p/all/c829/46302/c12521/111611,111612/c12567/41151/c837/46544/c12603/45927/c220/110085
agrotoxico = processa_uf(UF, '6852',
                    '/v/all/p/all/c829/46302/c12521/111611,111612/c12567/41151/c837/46544/c12603/45927/c220/110085/d/2/f/c' )

# FALTA AGREGAR AQUI: DIVIDIR USOU/(USOU + NÃO USOU)
agrotoxico.to_csv('./Dados_Final/agrotoxico.csv',sep=',',decimal='.',encoding='UTF-8',index=False)

# Tabela de crédito 6895
## https://apisidra.ibge.gov.br/values/t/6895/n6/1100015/v/1001990/p/all/c829/46302/c12542/115947/c218/46502/c12517/113601/c12544/111929/c220/110085/d/v1001990%202

credito = processa_uf(UF, '6895',
                      '/v/1001990/p/all/c829/46302/c12542/115947/c218/46502/c12517/113601/c12544/111929/c220/110085/d/2/f/c')
credito.to_csv('./Dados_Final/credito.csv',sep=',',decimal='.',encoding='UTF-8',index=False)

# Tabela 6897 - VBP 2017
VBP17 = processa_uf(UF,'6897', "/v/1999/p/all/c829/46302/c12547/114017/c218/46502/c12517/113601/d/2/f/c")
VBP17.to_csv('./Dados_Final/VBP17.csv',sep=',',decimal='.',encoding='UTF-8',index=False)


# Tabela 6962 - Correção do solo
## https://apisidra.ibge.gov.br/values/t/6962/n6/1100015/v/183/p/all/c836/46531/c12549/allxt/c798/47179/c220/110085
correcao_solo = processa_uf(UF,'6962', '/v/183/p/all/c836/46531/c12549/allxt/c798/47179/c220/110085/d/2/f/c')
# FALTA AGREGAR AQUI: DIVIDIR USOU/(USOU + NÃO USOU)
correcao_solo.to_csv('./Dados_Final/correcao_solo.csv',sep=',',decimal='.',encoding='UTF-8',index=False)

# Tabela 6874 - Total de bens e equipamentos
## https://apisidra.ibge.gov.br/values/t/6874/n6/1100015,1100023/v/9572/p/all/c829/46302/c796/allxt/c12603/45927/c220/110085
bens_equip = processa_uf(UF,'6874','/v/9572/p/all/c829/46302/c796/allxt/c12603/45927/c220/110085/d/2/f/c')

bens_equip = (bens_equip[['Município (Código)',
            'Tratores, implementos e máquinas existentes no estabelecimento agropecuário (Código)' ,'Valor']]\
              .rename(columns={'Município (Código)':'geocode','Tratores, implementos e máquinas existentes no estabelecimento agropecuário (Código)':'cod'})\
             .assign(
               Valor = lambda d: d['Valor'].str.replace(r"^(\.\.\.|X|-)$", '0', regex=True).astype(float),
               cod=lambda x: np.select(
                 [
                  (x['cod'] == '40597'),
                  (x['cod'] == '40598'),
                  (x['cod'] == '40599') ,
                  (x['cod'] == '40600')
              ],
                 ['Tratores', 'Semeadeiras_plantadeiras', 'Colheitadeiras', 'Adubadeiras_e_ou_distribuidoras_de_calcário'],
              default='neutral'
              )
               ).pivot(index='geocode', columns='cod', values='Valor')\
                 .reset_index()\
                 .assign(
                   BENS = lambda d: d['Adubadeiras_e_ou_distribuidoras_de_calcário'] + d['Colheitadeiras'] + d['Semeadeiras_plantadeiras'],
                   TRAT = lambda d: d['Tratores'],
                   BENS_TRAT = lambda d: d['TRAT'] + d['BENS']
                 )
                 [['geocode', 'BENS', 'TRAT', 'BENS_TRAT' ]])

bens_equip.to_csv('./Dados_Final/bens_equip.csv',sep=',',decimal='.',encoding='UTF-8',index=False)



# Tabela 6888 - Trabalho
#trabalho = processa_uf(UF,'6888','/v/185/p/all/c829/46302/c12578/112967/c12573/45929/c218/46502/c12517/113601/d/2/f/c')
#trabalho.to_csv('./Dados_Final/trabalho.csv',sep=',',decimal='.',encoding='UTF-8',index=False)

# Tabela 6879 - Área ocupada pela agropecuária
# https://apisidra.ibge.gov.br/values/t/6879/n6/4125407/v/184/p/all/c829/46302/c12517/113601/c12567/41151/c12894/46569/d/v184%200
areaHec_agropec = processa_uf(UF, '6879','/v/184/p/all/c829/46302/c12517/113601/c12567/41151/c12894/46569/d/2/f/c')
areaHec_agropec.to_csv('./Dados_Final/areaHec_agropec.csv',sep=',',decimal='.',encoding='UTF-8',index=False)

# Tabela 6879 - Assistência técnica
# https://apisidra.ibge.gov.br/values/t/6879/n6/1100015,1100023/v/183/p/all/c829/46302/c12517/113601/c12567/41151,113111/c12894/46569
assist_tec = processa_uf(UF, '6879','/v/183/p/all/c829/46302/c12517/113601/c12567/41151,113111/c12894/46569/d/2/f/c')

assist_tec = (assist_tec[['Município (Código)', 'Origem da orientação técnica recebida (Código)', 'Valor']]\
                .rename(columns={'Município (Código)':'geocode','Origem da orientação técnica recebida (Código)':'cod'})\
             .assign(
               Valor = lambda d: d['Valor'].str.replace(r"^(\.\.\.|X|-)$", '0', regex=True).astype(float),
               cod=lambda x: np.select(
                 [
                  (x['cod'] == '113111'),
                  (x['cod'] == '41151')
              ],
                 ['Recebeu', 'Total'],
              default='neutral'
              )
               ).pivot(index='geocode', columns='cod', values='Valor')\
                 .reset_index()\
                 .assign(
                   ASSIS_TEC = lambda d: (d['Recebeu'] / d['Total'])*100
                 )
                 [['geocode','ASSIS_TEC']]
                 )

assist_tec.to_csv('./Dados_Final/assist_tec.csv',sep=',',decimal='.',encoding='UTF-8',index=False)

# Tabela 6857 - Área irrigada (Hectares)
# https://apisidra.ibge.gov.br/values/t/6857/n6/1100015,1100023/v/2373/p/all/c829/46302/c12604/118477/c12564/41145/c12771/45951/c309/10969/d/v2373%200
area_irrigada_hect = processa_uf(UF, '6857',
                                 '/v/2373/p/all/c829/46302/c12604/118477/c12564/41145/c12771/45951/c309/10969/d/2/f/c')
area_irrigada_hect.to_csv('./Dados_Final/area_irrigada_hect.csv',sep=',',decimal='.',encoding='UTF-8',index=False)

# Tabela 6899 - Despesas - Total e Despesas com novas culturas permanentes e silvicultura
# https://apisidra.ibge.gov.br/values/t/6899/n6/1100015,1100023/v/1996/p/all/c829/46302/c210/45957,45958,113946/c218/46502/c12517/113601/d/v1996%200
despesas0 = processa_uf(UF, '6899','/v/1996/p/all/c829/46302/c210/45957,45958,113946/c218/46502/c12517/113601/d/2/f/c')

despesas = (despesas0[['Município (Código)', 'Tipo de despesa (Código)', 'Valor']]\
                .rename(columns={'Município (Código)':'geocode','Tipo de despesa (Código)':'cod'})\
             .assign(
               Valor = lambda d: d['Valor'].str.replace(r"^(\.\.\.|X|-)$", '0', regex=True).astype(float),
               cod=lambda x: np.select(
                 [
                  (x['cod'] == '113946'),
                  (x['cod'] == '45957'),
                  (x['cod'] == '45958')
              ],
                 ['Total', 'Novas_culturas_permanentes_e_silvicultura','Formação_de_pastagens'],
              default='neutral'
              )
               ).pivot(index='geocode', columns='cod', values='Valor')\
                 .reset_index()\
                 .assign(
                   DESP = lambda d: d['Novas_culturas_permanentes_e_silvicultura'] + d['Formação_de_pastagens'],
                   DESP_PERC = lambda d: (d['DESP'] / d['Total'])*100
                 )
                 #[['geocode','DESP_PERC','DESP']]
                 )

despesas.to_csv('./Dados_Final/despesas_totais.csv',sep=',',decimal='.',encoding='UTF-8',index=False)


# Tabela 6899 - Despesas com novas culturas permanentes e silvicultura; formação de pastagens
#despesas_novas_pastagens = processa_uf(UF, '6899',
#                                       '/v/1996/p/all/c829/46302/c210/45957,45958/c218/46502/c12517/113601/d/2/f/c')
#despesas_novas_pastagens.to_csv('./Dados_Final/despesas_novas_pastagens.csv',sep=',',decimal='.',encoding='UTF-8',index=False)

# Tabela 1301 - Área municipal (2010)
area_municipal = processa_uf(UF, '1301', '/v/615/p/all/d/2/f/c')
area_municipal.to_csv('./Dados_Final/area_municipal.csv',sep=',',decimal='.',encoding='UTF-8',index=False)

# Manipulação das informações de cobertura florestal
Cerrado = pd.read_excel('./Dados_V2/tabela_geral_mapbiomas_col8_biomas_municipios.xlsx',sheet_name='COBERTURA_COL8.0')
# 1986, 1987, 1988, 1989, 1990, 1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022

cerrado  =  Cerrado[['geocode', 'biome','level_1', 2006, 2017]].query("biome == 'Cerrado'") \
  .assign( Level_1 = Cerrado['level_1'].apply(categorizacao_uso_terra) )


cerrado = cerrado[['geocode', 'Level_1', 2006, 2017]].groupby(['geocode','Level_1'],as_index=False)\
  .agg(
    a2006 = (2006, 'sum'),
    a2017 = (2017, 'sum'),
  )\
    .melt(id_vars=['geocode', 'Level_1'],value_name='Area',var_name='Ano')\
    .pivot(index= ['geocode','Ano'], columns=['Level_1'], values="Area")\
    .reset_index()\
    .assign(Total = lambda d: d['1. Forest'] + d['3. Farming'] + d['Outros'],
            Percent = lambda d: d['1. Forest'] / d['Total'],
            Ano = lambda d: d['Ano'].str.replace("a",'', regex=True).astype(int)
            )\
    .groupby('geocode').apply(
      lambda df: df.assign(
        tx_desf=lambda x: ((x['1. Forest'] / x['1. Forest'].shift(1)) - 1)\
          .apply(lambda y: 0 if y > 0 else abs(y))
          ), include_groups=False
      ).reset_index(drop=False)\
        .query("Ano==2017").assign(
      geocode = lambda d: d['geocode'].astype(str)
    ).rename(columns={'geocode':'CD_GEOCMU'})


# 3101607, 3520442, 3131406, 3544509, 3546108
cerrado.query('CD_GEOCMU==3131406')
cerrado.head(15)
cerrado.shape




#area_municipal = (pd.read_csv('./Dados_Final/area_municipal.csv',sep=',',decimal='.')\
#  .rename(columns={'Município (Código)':'geocode','Valor':'AREA_MUNI'})#\
#    # .assign(
#    #   AREA_MUNI = lambda d: d['AREA_MUNI'].str.replace("-|X", '0', regex=True).astype(float)
#    # )
#    [['geocode', 'AREA_MUNI']])





#cerrado.to_csv('./Dados_Final/teste.csv',sep=',',decimal='.',encoding='UTF-8',index=False)


###########

# def verificar_faltantes(x, y):
#   X = x.groupby('geocode').size().reset_index(name='counts_X').sort_values(by='counts_X', ascending=False)
#   Y =y.groupby('geocode').size().reset_index(name='counts_Y').sort_values(by='counts_Y', ascending=False)

#   # Realizar o left join
#   final = X.merge(Y, on='geocode', how='left')

#   # Filtrar os casos em que 'counts_Y' está NaN (não há correspondência)
#   faltantes = final[final['counts_Y'].isna()]

#   return faltantes


# verificar_faltantes(area_municipal,despesas_novas_pastagens)

# # Verificar o total de municipior pertencentes ao cerrado

# cerrado[['CD_GEOCMU']].nunique()

# area_municipal[['geocode']].nunique()


# dados_final.query("CD_GEOCMU == '3538907'")
# Cerrado.query("geocode == 3538907")
# shp.query("CD_GEOCMU == 3500600")
# OS dois municipios faltantes não estão no shp!
# '3500600', '3538907'

################################################################################
###                     Tratamento de dados espaciais                       ####
################################################################################

import geopandas as gpd
import matplotlib as plt
dados_final['CD_GEOCMU'].dtype


# Caminho para o seu arquivo .shp
shp_file_path = 'C:/Users/William Barbosa/Documents/Desfl_Cerrado/Dados_V2/SHP/br_municipios/BRMUE250GC_SIR.shp'

# Importando o arquivo .shp
shp = gpd.read_file(shp_file_path)

# Realiza o join entre o shp e a base de dados
# shp_final = shp_final[~shp_final['CD_GEOCMU'].isin([3518701, 3520400,2605459])]

shp_final = shp.merge(dados_final, on='CD_GEOCMU')\
  .query("CD_GEOCMU not in ['3518701', '3520400', '2605459', '3101607', '3520442', '3131406', '3544509', '3546108']") # Remove ilhas e municípios sem área de floresta


shp_final = shp_final.merge(cerrado,on='CD_GEOCMU')

# Filtrando somente os municípios do Cerrado
cerrado_mun = cerrado[['CD_GEOCMU']].assign(
  CD_GEOCMU = lambda d: d['CD_GEOCMU'].astype(str)
  )['CD_GEOCMU'].unique() # Lista de municípios pertencentes ao Cerrado

# Apenas dois municípios não estão na lista final
set(shp_final['CD_GEOCMU']).symmetric_difference(cerrado_mun)

# SHP final
shp_final1 = shp_final[shp_final['CD_GEOCMU'].isin(cerrado_mun)]

shp_final1 = shp_final1.drop('Ano',axis=1)

# Salvando o resultado
shp_final1.to_file('./Dados_V2/SHP/mapa_regressao_vf.shp')

len(np.unique(cerrado[['CD_GEOCMU']]))

for col in shp_final.columns:
    print(col + ": " + str(shp_final[col].dtype))

len(shp_final[['CD_GEOCMU']])

[len(df) for df in lista_df]


# Verificar e retornar o total de NA's em colunas que possuem NA's
for col in shp_final.columns:
    na_count = shp_final[col].isna().sum()
    if na_count > 0:
        print(f"{col}: {na_count} NA's")


import matplotlib.pyplot as plt

def count_na_per_row(df):
    """
    Conta a quantidade de valores NA em cada linha de um DataFrame.

    Parâmetros:
    df (DataFrame): O DataFrame a ser verificado.

    Retorna:
    Series: Uma série com a quantidade de valores NA em cada linha.
    """
    #return df.apply(lambda row: row.isna().sum(), axis=1)
    return df.apply(lambda row: row.isna().all(), axis=1)


def plt_na(shp,var):
  dados = shp.assign(
      varplot = lambda d: d[var].isna()
    )
  color_map = {True: 'red', False: '#0000CD'}
  dados['color'] = dados['varplot'].map(color_map)

  fig, ax = plt.subplots(1, 1, figsize=(10, 6))
  dados.plot(ax=ax, color=dados['color'], edgecolor='0.8', linewidth=0.2)

  legend_labels = {'Com NA': 'red', 'Com valor': '#0000CD'}
  handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=label)
               for label, color in legend_labels.items()]
  ax.legend(handles=handles, loc='upper left', title='Legenda')

    # Mostrar o plot
  plt.show()

plt_na(shp_final,'IRRIGACAO')
plt_na(shp_final,'tx_desf')

## Fazer um loop para criar uma flag que indique NA para cada uma das variáveis e linhas

na_counts = count_na_per_row(shp_final)
shp_final['na_counts'] = na_counts

shp_final.query('na_counts != 0')[['NM_MUNICIP',]]


################################################################################
import geopandas as gpd
import matplotlib.pyplot as plt
import pysal as py
from splot.mapping import vba_choropleth as maps
from matplotlib import colors
import contextily
import spreg
import xlsxwriter
#from .sqlite import head_to_sql, start_sql
import os
import libpysal
from mlxtend.preprocessing import standardize
import numpy as np

shp_final.plot()
plt.show()

# # LISA
# tx_desf = shp_final['tx_desf']
# tx_desf_lisa = pygeoda.local_moran(queen_w, tx_desf)

# Início da modelagem
db = libpysal.io.open('./Dados_V2/SHP/mapa_regressao_vf.dbf','r')
shp_final = gpd.read_file('./Dados_V2/SHP/mapa_regressao_vf.shp')

db.header

# Matriz queen
queen_w = pygeoda.queen_weights(shp_final)
# Criando a matriz de peso espacial
w = libpysal.weights.Queen.from_shapefile('./Dados_V2/SHP/mapa_regressao_vf.shp')
w.transform = 'r' # Padroniza na linha, de forma que a soma será 1


shp_final['VBP17']
X = []
#X.append(db.by_col("IRRIGAC"))
X.append(shp_final['VBP17'])

x_names = ['VBP17']

# Criando as variáveis
vr_fl = shp_final["tx_desf"]
y = np.array(vr_fl)
y.shape = (len(vr_fl),1)


# Estima um OLS com os testes

# Normalizar a matriz
X0 = X#standardize(X)

ols = spreg.OLS(y,X0,w=w, name_x=x_names, name_y='des1785', name_w = 'Matriz Queen',name_ds='Dados_Desma',spat_diag=True)

print(ols.summary)