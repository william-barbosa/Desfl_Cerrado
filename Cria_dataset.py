import pandas as pd
import numpy as np
from functools import reduce
import matplotlib.pyplot as plt
import libpysal
from libpysal.weights import Queen

# Função para realizar um left join entre dois DataFrames com base na coluna 'id'
def left_join(df_left, df_right):
    return pd.merge(df_left, df_right, on='geocode', how='left')

# Função utilizada para agregação
def categorizacao_uso_terra(x):
    if x in ['2. non norest natural formation','4. non vegetated area','5. water','6. non observed']:
        return 'Outros'
    else:
        return x

# VBP 17
vbp17 = (pd.read_csv('./Dados_Final/VBP17.csv',sep=',',decimal='.')\
  .rename(columns={'Município (Código)':'geocode'})\
    .assign(
      Valor=lambda x: np.where(x['Valor'] == "...", '-999',
                               np.where(x['Valor'] == "..",  '-999',
                               np.where(x['Valor'] == "X",  '-999',
                               np.where(x['Valor'] == "-",  '0',
                                        x['Valor'])
                               ))),
      VBP17 = lambda d: pd.to_numeric(d['Valor'],  errors='coerce')
      )[['geocode', 'VBP17']])

# VBP 06
vbp06 = (pd.read_csv('./Dados_Final/VBP06.csv',sep=',',decimal='.')\
  .rename(columns={'Município (Código)':'geocode'})\
    .assign(
      Valor=lambda x: np.where(x['Valor'] == "...", '-999',
                               np.where(x['Valor'] == "..",  '-999',
                               np.where(x['Valor'] == "X",  '-999',
                               np.where(x['Valor'] == "-",  '0',
                                        x['Valor'])
                               ))),
      VBP06 = lambda d: pd.to_numeric(d['Valor'],  errors='coerce')
    )[['geocode', 'VBP06']])


# Uso do agrotóxico em 2017
# Não utilizou = 111612
# Utilizou = 111611
agrotoxico17 = (pd.read_csv('./Dados_Final/agrotoxico.csv',sep=',',decimal='.')\
  .rename(columns={'Município (Código)':'geocode','Uso de agrotóxicos (Código)':'var_cod'})\
    .assign(
      Valor=lambda x: np.where(x['Valor'] == "...", '-999',
                               np.where(x['Valor'] == "..",  '-999',
                               np.where(x['Valor'] == "X",  '-999',
                               np.where(x['Valor'] == "-",  '0',
                                        x['Valor'])
                               ))),
      AGROTOXICO = lambda d: pd.to_numeric(d['Valor'],  errors='coerce'),

      var_cod=lambda x: np.select( [(x['var_cod'] == 111612), (x['var_cod'] == 111611)],
                 ['n_utilizou', 'utilizou'], default='neutral' )
    )[['geocode','var_cod', 'AGROTOXICO']])\
      .pivot(index='geocode', columns='var_cod', values='AGROTOXICO')\
        .reset_index()\
        .assign(
Total = lambda d: d['n_utilizou'] + d['utilizou'],
          AGROTX170 = lambda d: (d['utilizou'] / d['Total'])*100,
          AGROTX17 = lambda x: np.where((x['utilizou'] == -999) | (x['n_utilizou'] == -999) , -999,x['AGROTX170'] )
          )[['geocode', 'AGROTX17']]

agrotoxico06 = (pd.read_csv('./Dados_Final/agrotoxico_06.csv',sep=',',decimal='.')\
  .rename(columns={'Município (Código)':'geocode'})\
    .assign(
      Valor=lambda x: np.where(x['Valor'] == "...", '-999',
                               np.where(x['Valor'] == "..",  '-999',
                               np.where(x['Valor'] == "X",  '-999',
                               np.where(x['Valor'] == "-",  '0',
                                        x['Valor'])
                               ))),
      AGROTX06 = lambda d: pd.to_numeric(d['Valor'],  errors='coerce'),

    )[['geocode','AGROTX06']])


# Irrigação 17
irrigacao17 = (pd.read_csv('./Dados_Final/area_irrigada_hect.csv',sep=',',decimal='.')\
  .rename(columns={'Município (Código)':'geocode'})\
    .assign(
      Valor=lambda x: np.where(x['Valor'] == "...", '-999',
                               np.where(x['Valor'] == "..",  '-999',
                               np.where(x['Valor'] == "X",  '-999',
                               np.where(x['Valor'] == "-",  '0',
                                        x['Valor'])
                               ))),
      IRRIG17 = lambda d: pd.to_numeric(d['Valor'],  errors='coerce')
    )[['geocode', 'IRRIG17']])

# Irrigação 06
irrigacao06 = (pd.read_csv('./Dados_Final/area_irrigada_hect_06.csv',sep=',',decimal='.')\
  .rename(columns={'Município (Código)':'geocode'})\
    .assign(
      Valor=lambda x: np.where(x['Valor'] == "...", '-999',
                               np.where(x['Valor'] == "..",  '-999',
                               np.where(x['Valor'] == "X",  '-999',
                               np.where(x['Valor'] == "-",  '0',
                                        x['Valor'])
                               ))),
      IRRIG06 = lambda d: pd.to_numeric(d['Valor'],  errors='coerce')
    )[['geocode', 'IRRIG06']])

# Assistência Técnica em 17
assist_tec17 = pd.read_csv('./Dados_Final/assist_tec.csv',sep=',',decimal='.')\
  .rename(columns={'Município (Código)':'geocode','ASSIS_TEC':'ASSIST17'})

# Assistência Técnica em 06
assist_tec06 = pd.read_csv('./Dados_Final/assist_tec_06.csv',sep=',',decimal='.')\
  .rename(columns={'Município (Código)':'geocode','ASSIS_TEC':'ASSIST06'})

# Bens e equipamentos em 17
bens_equip17 = (pd.read_csv('./Dados_Final/bens_equip.csv',sep=',',decimal='.')[['geocode', 'BENS_TRAT']])\
  .rename(columns={'BENS_TRAT':'BENS_TR17'})

# Bens e equipamentos em 17
bens_equip06 = (pd.read_csv('./Dados_Final/bens_equip_06.csv',sep=',',decimal='.')[['geocode', 'BENS_TRAT']])\
  .rename(columns={'BENS_TRAT':'BENS_TR06'})

# Correção do solo em 17
## Fez a aplicação: 46554
## Não fez a aplicação: 46555
correcao_solo17 = (pd.read_csv('./Dados_Final/correcao_solo.csv',sep=',',decimal='.')\
  .rename(columns={'Município (Código)':'geocode','Valor':'CORRECAO_SOLO','Uso de calcário e/ou outros corretivos do pH do solo (Código)':'var_cod'})\
    .assign(
      teste=lambda x: np.where(x['CORRECAO_SOLO'] == "...", '-999',
                               np.where(x['CORRECAO_SOLO'] == "..",  '-999',
                               np.where(x['CORRECAO_SOLO'] == "X",  '-999',
                               np.where(x['CORRECAO_SOLO'] == "-",  '0',
                                        x['CORRECAO_SOLO'])
                               ))),
      CORRECAO_SOLO = lambda d: pd.to_numeric(d['teste'],  errors='coerce'),
      var_cod=lambda x: np.where(x['var_cod'] == 46554, 'fez',
                               np.where(x['var_cod'] == 46555,  'n_fez',
                                        x['var_cod'])
                               ))
    )[['geocode','var_cod', 'CORRECAO_SOLO']]\
      .pivot(index='geocode', columns='var_cod', values='CORRECAO_SOLO')\
        .reset_index()\
        .assign(
          Total = lambda d: d['fez'] + d['n_fez'],
          CORR_SOL170 = lambda d: (d['fez'] / d['Total'])*100,
          CORR_SOL17 = lambda x: np.where((x['fez'] == -999) | (x['n_fez'] == -999) , -999,x['CORR_SOL170'] )
          )[['geocode', 'CORR_SOL17']]

# Correção do solo em 06
correcao_solo06 = pd.read_csv('./Dados_Final/correcao_solo_06.csv',sep=',',decimal='.')\
  .rename(columns={'Município (Código)':'geocode','Valor':'CORR_SOL06'})\
    .assign(
      teste=lambda x: np.where(x['CORR_SOL06'] == "...", '-999',
                               np.where(x['CORR_SOL06'] == "..",  '-999',
                               np.where(x['CORR_SOL06'] == "X",  '-999',
                               np.where(x['CORR_SOL06'] == "-",  '0',
                                        x['CORR_SOL06'])
                               ))),
      CORR_SOL06 = lambda d: pd.to_numeric(d['teste'],  errors='coerce')
       #CORR_SOL06 = lambda d: pd.to_numeric(d['CORR_SOL06'], errors='coerce').fillna(0)
    )[['geocode', 'CORR_SOL06']]


# Fizeram uso de financiamento 17
credito17 = (pd.read_csv('./Dados_Final/credito.csv',sep=',',decimal='.')\
  .rename(columns={'Município (Código)':'geocode'})\
    .assign(
      Valor=lambda x: np.where(x['Valor'] == "...", '-999',
                               np.where(x['Valor'] == "..",  '-999',
                               np.where(x['Valor'] == "X",  '-999',
                               np.where(x['Valor'] == "-",  '0',
                                        x['Valor'])
                               ))),
      CREDITO17 = lambda d: pd.to_numeric(d['Valor'],  errors='coerce')
    )[['geocode', 'CREDITO17']])

# Fizeram uso de financiamento 06
credito06 = (pd.read_csv('./Dados_Final/credito_06.csv',sep=',',decimal='.')\
  .rename(columns={'Município (Código)':'geocode'})\
    .assign(
      Valor=lambda x: np.where(x['Valor'] == "...", '-999',
                               np.where(x['Valor'] == "..",  '-999',
                               np.where(x['Valor'] == "X",  '-999',
                               np.where(x['Valor'] == "-",  '0',
                                        x['Valor'])
                               ))),
      CREDITO06 = lambda d: pd.to_numeric(d['Valor'],  errors='coerce')
    )[['geocode', 'CREDITO06']])

# Pessoal ocupado na agropecuária em 17
trabalho17 = (pd.read_csv('./Dados_Final/trabalho.csv',sep=',',decimal='.')\
  .rename(columns={'Município (Código)':'geocode'})\
    .assign(
      Valor=lambda x: np.where(x['Valor'] == "...", '-999',
                               np.where(x['Valor'] == "..",  '-999',
                               np.where(x['Valor'] == "X",  '-999',
                               np.where(x['Valor'] == "-",  '0',
                                        x['Valor'])
                               ))),
      TRAB17 = lambda d: pd.to_numeric(d['Valor'],  errors='coerce')
    )[['geocode', 'TRAB17']])

# Pessoal ocupado na agropecuária em 06
trabalho06 = (pd.read_csv('./Dados_Final/trabalho_06.csv',sep=',',decimal='.')\
  .rename(columns={'Município (Código)':'geocode'})\
    .assign(
      Valor=lambda x: np.where(x['Valor'] == "...", '-999',
                               np.where(x['Valor'] == "..",  '-999',
                               np.where(x['Valor'] == "X",  '-999',
                               np.where(x['Valor'] == "-",  '0',
                                        x['Valor'])
                               ))),
      TRAB06 = lambda d: pd.to_numeric(d['Valor'],  errors='coerce')
    )[['geocode', 'TRAB06']])


# Despesas em 17
despesas_tot17 = (pd.read_csv('./Dados_Final/despesas_totais.csv',sep=',',decimal='.')\
  .rename(columns={'Município (Código)':'geocode','DESP':'VLR_DESP', 'DESP_PERC': 'P_DESP'})\
    [['geocode', 'VLR_DESP','P_DESP']])

# Área dos estabelecimentos agropecuários em 17
areaAgro17 = (pd.read_csv('./Dados_Final/areaHec_agropec.csv',sep=',',decimal='.')\
  .rename(columns={'Município (Código)':'geocode'})\
        .assign(
      Valor=lambda x: np.where(x['Valor'] == "...", '-999',
                               np.where(x['Valor'] == "..",  '-999',
                               np.where(x['Valor'] == "X",  '-999',
                               np.where(x['Valor'] == "-",  '0',
                                        x['Valor'])
                               ))),
      A_AGRO17 = lambda d: pd.to_numeric(d['Valor'],  errors='coerce')
    )[['geocode', 'A_AGRO17']])

areaAgro17.query("A_AGRO17 != A_AGRO17")

# Área dos estabelecimentos agropecuários em 06
areaAgro06 = (pd.read_csv('./Dados_Final/areaHec_agropec_06.csv',sep=',',decimal='.')\
  .rename(columns={'Município (Código)':'geocode' })\
    .assign(
      Valor=lambda x: np.where(x['Valor'] == "...", '-999',
                               np.where(x['Valor'] == "..",  '-999',
                               np.where(x['Valor'] == "X",  '-999',
                               np.where(x['Valor'] == "-",  '0',
                                        x['Valor'])
                               ))),
      A_AGRO06 = lambda d: pd.to_numeric(d['Valor'],  errors='coerce')
    )[['geocode', 'A_AGRO06']])

areaAgro06.query("A_AGRO06!=A_AGRO06")

# 4101606
areaAgro17.query('geocode == 4125407')


#import requests
## URL do arquivo xlsx (coleção 9 MapBiomas)
#url = "https://storage.googleapis.com/mapbiomas-public/initiatives/brasil/collection_9/statistics/mapbiomas_brazil_col_coverage_biome_state_municipality.xlsx"

## Caminho de destino para salvar o arquivo
#caminho_destino = "./Dados_V2/mapbiomas_brazil_col_coverage_biome_state_municipality.xlsx"
## Baixar e salvar o arquivo
#response = requests.get(url)
#with open(caminho_destino, "wb") as file:
#    file.write(response.content)
#print(f"Arquivo salvo em: {caminho_destino}")


# Manipulação das informações de cobertura florestal
Cerrado = pd.read_excel('./Dados_V2/mapbiomas_brazil_col_coverage_biome_state_municipality.xlsx',sheet_name='COVERAGE_9')
# 1986, 1987, 1988, 1989, 1990, 1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022

cerrado  =  Cerrado[['geocode', 'biome','class_level_1', 2006, 2017]].query("biome == 'Cerrado'")\
    .rename(columns={'class_level_1':'Level_1'})\
  .assign(Level_1=lambda x: np.where(x['Level_1'] == "2. Non Forest Natural Formation", 'Outros',
                np.where(x['Level_1'] == "4. Non vegetated area",  'Outros',
                np.where(x['Level_1'] == "5. Water and Marine Environment",  'Outros',
                np.where(x['Level_1'] == "6. Not Observed",  'Outros',
                x['Level_1'])
                               ))))


area = cerrado[['geocode', 'Level_1', 2006, 2017]].groupby(['geocode','Level_1'],as_index=False)\
  .agg(
    a2006 = (2006, 'sum'),
    a2017 = (2017, 'sum'),
  )\
    .melt(id_vars=['geocode', 'Level_1'],value_name='Area',var_name='Ano')\
    .pivot(index= ['geocode','Ano'], columns=['Level_1'], values="Area")\
    .reset_index()\
      .apply(lambda x: x.fillna(0))\
    .assign(
            Total = lambda d: d['1. Forest'] + d['3. Farming'] + d['Outros'],
            PFOREST = lambda d: d['1. Forest'] / d['Total'],
            PFARMING = lambda d: d['3. Farming'] / d['Total'],
            Ano = lambda d: d['Ano'].str.replace("a",'', regex=True).astype(int)
            )[['geocode','Ano','PFOREST','PFARMING']]\
              .melt(id_vars=['geocode', 'Ano'],value_name='Percentual',var_name='Tipo')\
                .assign(
                  Tipo=lambda x: np.where(x['Ano'] == 2006, x['Tipo'] + '06',
                             np.where(x['Ano'] == 2017, x['Tipo'] + '17', '00')),
                  #geocode = lambda d: d['geocode'].astype(str)
                )[['geocode', 'Tipo', 'Percentual']]\
                .pivot(index= ['geocode'], columns=['Tipo'], values="Percentual")\
                .reset_index()

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
            ).apply(lambda x: x.fillna(0))\
    .groupby('geocode').apply(
      lambda df: df.assign(
        tx_desf=lambda x: ((x['1. Forest'] / x['1. Forest'].shift(1)) - 1)\
          .apply(lambda y: 0 if y > 0 else abs(y))
          ), include_groups=False
      ).reset_index(drop=False)\
        .query("Ano==2017").assign(
      geocode = lambda d: d['geocode'].astype(str)
    ).rename(columns={'geocode':'CD_GEOCMU'})

###

## Verifica mínimos

agrotoxico = left_join(agrotoxico17, agrotoxico06)
#.assign(
#  AGROTX = lambda d: (d['AGROTX17'] - d['AGROTX06'] )
#)

agrotoxico.query("AGROTX06 <0")

credito = left_join(credito17, credito06)
#.assign(
#  CREDITO = lambda d: (d['CREDITO17'] - d['CREDITO06'] )
#)

vbp = left_join(vbp17, vbp06)
#.assign(
#  VBP = lambda d: (d['VBP17'] / d['VBP06'] - 1)*100
#)

correcao_solo = left_join(correcao_solo17, correcao_solo06)
#.assign(
#  CORR_SOL = lambda d: (d['CORR_SOL17'] - d['CORR_SOL06'] )
#)

bens_equip = left_join(bens_equip17, bens_equip06)
#.assign(
#  BENS_TR = lambda d: (d['BENS_TR17'] / d['BENS_TR06'] -1)*100
#)

trabalho = left_join(trabalho17, trabalho06)
#.assign(
#  TRAB = lambda d: (d['TRAB17'] / d['TRAB06'] -1)*100
#)

assist_tec = left_join(assist_tec17, assist_tec06)
#.assign(
#  ASSIST = lambda d: (d['ASSIST17'] - d['ASSIST06'] )
#)

irrigacao = left_join(irrigacao17, irrigacao06)
#.assign(
#  IRRIG = lambda d: (d['IRRIG17'] / d['IRRIG06'] -1)*100
#)

areaAgro = left_join(areaAgro17, areaAgro06)
#.assign(
#  A_AGRO = lambda d: (d['A_AGRO17'] / d['A_AGRO06'] -1)*100
#)

areaAgro.query("geocode == 4125407")

deflorestamento = cerrado.rename(columns={'CD_GEOCMU': 'geocode'})[['geocode','tx_desf']]\
  .assign(
      geocode = lambda d: d['geocode'].astype(int)
    )

deflorestamento['geocode'].dtype

lista_df = [vbp, agrotoxico, irrigacao, area, assist_tec, bens_equip, correcao_solo,
            credito, trabalho, despesas_tot17, areaAgro, deflorestamento]

dados_final = reduce(left_join, lista_df)\
  .rename(columns={'geocode':'CD_GEOCMU'})\
    .assign(
      # CD_GEOCMU = lambda d: d['CD_GEOCMU'].astype(chr)
      CD_GEOCMU = lambda d: d['CD_GEOCMU'].astype(str)
    )

len(dados_final)
dados_final.shape

# Verifica o total de linhas que cada um dos df possui antes de realizar o join.
[len(df) for df in lista_df]


################################################################################
###                     Tratamento de dados espaciais                       ####
################################################################################

import geopandas as gpd
import matplotlib as plt
dados_final['CD_GEOCMU'].dtype


# Caminho para o seu arquivo .shp
shp_file_path = 'C:/Users/William Barbosa/Documentos/Desfl_Cerrado/Dados_V2/SHP/br_municipios/BRMUE250GC_SIR.shp'

# Importando o arquivo .shp
shp = gpd.read_file(shp_file_path)

# Realiza o join entre o shp e a base de dados
# shp_final = shp_final[~shp_final['CD_GEOCMU'].isin([3518701, 3520400,2605459])]

shp_final = shp.merge(dados_final, on='CD_GEOCMU')\
  .query("CD_GEOCMU not in ['3100609', '3500600', '2206720', '5006275','3531902', '3523800', '3518701', '3520400', '2605459', '3101607', '3520442', '3131406', '3544509', '3546108']") # Remove ilhas e municípios sem área de floresta

shp_final = shp_final.merge(cerrado[['CD_GEOCMU']],on='CD_GEOCMU')

# Filtrando somente os municípios do Cerrado
cerrado_mun = cerrado[['CD_GEOCMU']].assign(
  CD_GEOCMU = lambda d: d['CD_GEOCMU'].astype(str)
  )['CD_GEOCMU'].unique() # Lista de municípios pertencentes ao Cerrado

# Apenas 11 municípios não estão na lista final
set(shp_final['CD_GEOCMU']).symmetric_difference(cerrado_mun)


# SHP final
shp_final1 = shp_final[shp_final['CD_GEOCMU'].isin(cerrado_mun)]

# Salvando o resultado
shp_final1.to_file('./Dados_V2/SHP/mapa_regressao_vf.shp')


# FIM

for col in shp_final1.columns:
    print(col + ": " + str(shp_final1[col].dtype))

len(shp_final[['CD_GEOCMU']])

[len(df) for df in lista_df]



# Verificar e retornar o total de NA's em colunas que possuem NA's
for col in shp_final1.columns:
    na_count = shp_final1[col].isna().sum()
    if na_count > 0:
        print(f"{col}: {na_count} NA's")


shp_final1.query("PFARMING06 != PFARMING06")[['CD_GEOCMU', 'PFARMING06']]

shp_final1.query("CREDITO06 <0 ")[['NM_MUNICIP','CD_GEOCMU','CREDITO06' ]]

shp_final1.columns




def plt_na(shp, var):
    # Criar uma coluna para identificar onde var < 0
    dados = shp.assign(
        varplot=lambda d: d[var] < 0
    )

    # Mapear cores
    color_map = {True: 'red', False: 'white'}
    dados['color'] = dados['varplot'].map(color_map)

    # Contar o total de valores -999
    total_na = dados['varplot'].sum()

    # Criar o plot
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    dados.plot(ax=ax, color=dados['color'], edgecolor='0.8', linewidth=0.2)

    # Configurar a legenda
    legend_labels = {
        f'Com NA ({total_na})': 'red',
        'Com valor': 'white'
    }
    handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=label)
               for label, color in legend_labels.items()]
    ax.legend(handles=handles, loc='upper left', title='Legenda')

    # Mostrar o plot
    plt.show()

# Chamando a função
plt_na(shp_final1, 'A_AGRO17')

shp_final1[['VLR_DESP']].describe()

# CREDITO006, CREDITO17, IRRIG06, IRRIG17

### Conferir novamente para garantir que não tenha nenhum -999

colunas = ['CREDITO06', 'CREDITO17', 'IRRIG06', 'IRRIG17']

lista_final = []

for col in colunas:
  teste = shp_final1.query(f"{col} < 0")[['NM_MUNICIP', 'CD_GEOCMU']]
  teste[['Variável']] = col
  lista_final.append(teste)

lista_final = pd.concat(lista_final, ignore_index=True)\
  .pivot(index=["NM_MUNICIP", "CD_GEOCMU"],
                  columns="Variável", values="Variável")\
                    .reset_index()\
                      .apply(lambda x: x.fillna(0))

lista_final[colunas] = np.where(lista_final[colunas] == 0, 0, 1)


lista_final['CD_GEOCMU'].duplicated().sum()

np.sum(lista_final[['CREDITO06']])

lista_final[['CREDITO06']].sum()

pd.Series([lista_final[['CREDITO06']]], dtype="float64").sum(min_count=1)


for col in colunas:
    total = lista_final[col].astype(int).sum(min_count=1)
    print(f"{col} total: {total}")

lista_final.query("CREDITO06==1")
#######################################################################################
# Corrigindo o problema de missings substituindo por valores defasados espacialmente. #
#######################################################################################
# Matriz queen
# Criando a matriz de peso espacial
w = Queen.from_dataframe(shp_final1, ids='CD_GEOCMU')

# Padroniza na linha, de forma que a soma será 1
w.transform = 'r'

shp_final2 = shp_final1.assign(
    temp = lambda d: np.where(d['CREDITO06'] == -999, np.nan, d['CREDITO06']), # Substituindo -999 por NaN
    CREDITO06_w=lambda d: libpysal.weights.lag_spatial(w, d['temp']
    )
)

shp_final2.query("CD_GEOCMU=='3105400'")[["NM_MUNICIP","CD_GEOCMU", "CREDITO06","CREDITO06_w",'temp']]


ids = list(w.id_order)

# Encontrar o índice da linha correspondente ao código "3105400"
codigo = "3105400"
linha_idx = ids.index(codigo)
print(f"Soma dos pesos da primeira linha: {sum(w['3105400'].values())}")

w['3105400'].values()

shp_final2.query("CD_GEOCMU in ['3105400','3161908','3110004','3107703']")[["NM_MUNICIP","CD_GEOCMU", "CREDITO06"]]

62.5*0.3333333333333333 + 0.3333333333333333*75.0