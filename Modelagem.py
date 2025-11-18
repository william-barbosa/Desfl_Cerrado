################################################################################
######                             Modelagem                              ######
################################################################################
import geopandas as gpd
import matplotlib.pyplot as plt
#import pysal as py
#from splot.mapping import vba_choropleth as maps
import libpysal
from libpysal.weights import Queen
import numpy as np
from mlxtend.preprocessing import standardize

db = libpysal.io.open('./Dados_V2/SHP/mapa_regressao_vf.dbf','r')
shp_final = gpd.read_file('./Dados_V2/SHP/mapa_regressao_vf.shp')

db.header

for col in shp_final.columns:
  print(col + ': ' + str(np.sum(shp_final[col].isna())))


# Matriz queen
# Criando a matriz de peso espacial
w = Queen.from_dataframe(shp_final, ids='CD_GEOCMU')

w.transform = 'r' # Padroniza na linha, de forma que a soma será 1


# Obter os IDs das observações
ids = list(w.neighbors.keys())

# verifica o ID na lista
ids[0]

print(f"Soma dos pesos da primeira linha: {sum(w['2201945'].values())}")


####
for col in shp_final.columns:
    print(col + ": " + str(shp_final[col].dtype))

# Corrigindo os problemas de zero e substituindo pela variável defasada espacialmente

X = shp_final[['NM_MUNICIP', 'CD_GEOCMU', 'tx_desf',
               'AGROTX06', 'AGROTX17',
               'CREDITO06', 'CREDITO17',
               'VBP06','VBP17',
               'CORR_SOL06','CORR_SOL17',
               'BENS_TR06','BENS_TR17']]\
  .assign(
  VBP06o=lambda d: d['VBP06'] ,
  VBP06 = lambda d: d['VBP06']  * (3.67 / 6.77), # Trazendo a valores de 2017 (valores por 1000)
  AGROTX_w06 = lambda d: libpysal.weights.lag_spatial(w, d['AGROTX06']),
  AGROTX_w17 = lambda d: libpysal.weights.lag_spatial(w, d['AGROTX17']),
  AGROTX06 =  lambda x: np.where((x['AGROTX06'] == 0), x['AGROTX_w06'], x['AGROTX06']),
  AGROTX17 =  lambda x: np.where((x['AGROTX17'] == 0), x['AGROTX_w17'], x['AGROTX17']),
  AGROTX = lambda d: (d['AGROTX17'] - d['AGROTX06'] ),

  CREDITO_w06 = lambda d: libpysal.weights.lag_spatial(w, d['CREDITO06']),
  CREDITO_w17 = lambda d: libpysal.weights.lag_spatial(w, d['CREDITO17']),
  CREDITO06 =  lambda x: np.where((x['CREDITO06'] == 0), x['CREDITO_w06'], x['CREDITO06']),
  CREDITO17 =  lambda x: np.where((x['CREDITO17'] == 0), x['CREDITO_w17'], x['CREDITO17']),
  CREDITO = lambda d: (d['CREDITO17'] - d['CREDITO06'] ),

  VBP = lambda d: (d['VBP17'] / d['VBP06'] - 1)*100,

  CORR_SOL = lambda d: (d['CORR_SOL17'] - d['CORR_SOL06'] ),

  BENS_TR_w06 = lambda d: libpysal.weights.lag_spatial(w, d['BENS_TR06']),
  BENS_TR_w17 = lambda d: libpysal.weights.lag_spatial(w, d['BENS_TR17']),
  BENS_TR06 =  lambda x: np.where((x['BENS_TR06'] == 0), x['BENS_TR_w06'], x['BENS_TR06']),
  BENS_TR17 =  lambda x: np.where((x['BENS_TR17'] == 0), x['BENS_TR_w17'], x['BENS_TR17']),
  BENS_TR0 = lambda d: (d['BENS_TR17'] / d['BENS_TR06'] -1)*100,

  BENS_TR = lambda x: np.where((x['CD_GEOCMU'] == '2201945') | (x['CD_GEOCMU'] == '2102374'), 0, x['BENS_TR0']) ,


  )

X[['NM_MUNICIP','CD_GEOCMU', 'AGROTX', 'CREDITO','VBP', 'CORR_SOL', 'BENS_TR','BENS_TR0']]\
  .describe()

(8/4)-1
7

X.hist(column='BENS_TR',bins=10)
plt.figure(figsize=(8, 6))
X.boxplot(column='BENS_TR')
plt.show()


## Converter o VBP para preços de 2017
X[['NM_MUNICIP', 'CD_GEOCMU', 'BENS_TR','BENS_TR06', 'BENS_TR17']].query('BENS_TR >=36862')

X[['NM_MUNICIP', 'CD_GEOCMU','BENS_TR_w06', 'BENS_TR_w17']].query('CD_GEOCMU=="2201945"')

shp_final[['NM_MUNICIP', 'CD_GEOCMU','BENS_TR06','BENS_TR17']].query("CD_GEOCMU == '5221858'")




## AGROTX06: 7 linhas iguais a zero
##  AGROTX17: 6 linhas iguais a zero



shp1 = shp_final.assign(
  VBP = lambda d: (d['VBP17'] / d['VBP06'] - 1)*100,
  AGROTX = lambda d: (d['AGROTX17'] / d['AGROTX06'] - 1)*100,
  IRRIG = lambda d: (d['IRRIG17'] / d['IRRIG06'] - 1)*100,
  ASSIST = lambda d: (d['ASSIST17'] / d['ASSIST06'] - 1)*100,
  BENS_TR = lambda d: (d['BENS_TR17'] / d['BENS_TR06'] - 1)*100,
  CORR_SOL = lambda d: (d['CORR_SOL17'] / d['CORR_SOL06'] - 1)*100,
  CREDITO = lambda d: (d['CREDITO17'] / d['CREDITO06'] - 1)*100,
  TRAB = lambda d: (d['TRAB17'] / d['TRAB06'] - 1)*100,
  A_AGRO = lambda d: (d['A_AGRO17'] / d['A_AGRO06'] - 1)*100
  )

shp1[['VBP', 'AGROTX', 'IRRIG', 'ASSIST', 'BENS_TR', 'CORR_SOL', 'CREDITO', 'TRAB', 'A_AGRO']].describe()

shp1.query('geocode == 4125407')



type(db)
# Variável resposta
vr_fl = db.by_col("tx_desf")

y = np.array(vr_fl)
y.shape = (len(vr_fl),1)

#x_names = ['IRRIGAC', 'VBP17', #'AREA_AG',
#           'AGROTOX', 'ASSIST_', 'CREDITO', 'DESPESA', 'TRABALH', 'BENS_EQ']
x_names = ['VBP17', 'CORRECA',#'Farming',
           'DESPESA', 'TRABALH', 'Sl_Sdst','Nordest','CREDITO']


pondera = np.array(db.by_col("AREA_AG"))
pondera.shape = (len(pondera),1)



X = []
#X.append(db.by_col("IRRIGAC"))
X.append(np.log(db.by_col("VBP17")))
X.append(db.by_col("CORRECA"))
#X.append(np.log(np.array(db.by_col("Farming"))+1))
#X.append(db.by_col("AGROTOX"))
#X.append(db.by_col("ASSIST_"))
#X.append(db.by_col("CREDITO"))
X.append(db.by_col("DESPESA"))
X.append(db.by_col("TRABALH"))

X.append(db.by_col("Sl_Sdst"))
X.append(db.by_col("Nordest"))
X.append(np.log(np.array(db.by_col("CREDITO"))+1))
