## Rotina criada por William Barbosa para o download dos dados do censo
# agropecuário 2006      atualizados

import pandas as pd
import numpy as np
#import sidrapy
import time
import requests
from functools import reduce
from termcolor import colored
# pd.set_option('display.width', 200)
pd.set_option('display.max_columns', None)

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

#  https://apisidra.ibge.gov.br/values/t/910/n6/1100106,1100205,1100015,1100023,1100049,1100056,1100064,1100080,1100098,1100114,1100122,1100155,1100189,1100254,1100288,1100304,1100320,1100338,1100130,1100148,1100296,1100346,1100031,1100379,1100452,1100924,1100940,1101435,1101450,1101468,1101476,1101484,1101492,1101559,1101757,1100072,1100262,1100403,1100502,1100601,1100700,1100809,1100908,1101005,1101104,1101203,1101302,1101401,1101500,1101609,1101708,1101807/v/allxp/p/all/c12521/0/c12598/0/c12603/0/c220/0

# Tabela 910 - Agrotóxico
#https://apisidra.ibge.gov.br/values/t/910/n6/1100015/v/1000183/p/all/c12521/111611/c12598/0/c12603/0/c220/0/d/v1000183%202
agrotoxico = processa_uf(UF, '910',
                         '/v/1000183/p/all/c12521/111611/c12598/0/c12603/0/c220/0/d/2/f/c' )
agrotoxico.to_csv('./Dados_Final/agrotoxico_06.csv',sep=',',decimal='.',encoding='UTF-8',index=False)

# Tabela de crédito 829
# https://apisidra.ibge.gov.br/values/t/829/n6/1100015/v/1001990/p/all/c12542/115947/c218/0/c12517/113601/c12544/111929/c220/0/d/v1001990%202

credito = processa_uf(UF, '829',
                      '/v/1001990/p/all/c12542/115947/c218/0/c12517/113601/c12544/111929/c220/0/d/2/f/c')
credito.to_csv('./Dados_Final/credito_06.csv',sep=',',decimal='.',encoding='UTF-8',index=False)


# Tabela 1118 - VBP 2006
##https://apisidra.ibge.gov.br/values/t/1118/n6/1100015/v/1999/p/all/c12547/114017/c12896/0/d/v1999%200
VBP06 = processa_uf(UF,'1118','/v/1999/p/all/c12547/114017/c12896/0/d/2/f/c')
VBP06.to_csv('./Dados_Final/VBP06.csv',sep=',',decimal='.',encoding='UTF-8',index=False)


# Tabela 1245 - Correção do solo
## https://apisidra.ibge.gov.br/values/t/1245/n6/1100015/v/1000183/p/all/c12549/112013/c218/0/c12552/0/c12548/0/c220/0/d/v1000183%202
correcao_solo = processa_uf(UF,'1245', '/v/1000183/p/all/c12549/112013/c218/0/c12552/0/c12548/0/c220/0/d/2/f/c')
# FALTA AGREGAR AQUI: DIVIDIR USOU/(USOU + NÃO USOU)
correcao_solo.to_csv('./Dados_Final/correcao_solo_06.csv',sep=',',decimal='.',encoding='UTF-8',index=False)

#
# Tabela 861 - Total de bens e equipamentos #
#
# No censo de 2006 não é compatível com o de 2017, então foi retirado dessa tabela somente o total de:
# a) Semeadeiras e/ou plantadeiras; b) Colheitadeiras; c) Adubadeiras e/ou distribuidoras de calcário


## https://apisidra.ibge.gov.br/values/t/861/n6/1100015,1100023/v/2044/p/all/c12606/113527,113528,113530/c218/0/c12603/0/c220/0/c12517/113601
bens_equip = processa_uf(UF,'861','/v/2044/p/all/c12606/113527,113528,113530/c218/0/c12603/0/c220/0/c12517/113601/d/2/f/c')


bens_equip = (bens_equip\
  .rename(columns={'Município (Código)':'geocode','Valor':'BENS'})\
    .assign(
      BENS=lambda d: d['BENS'].str.replace(r"^(\.\.\.|X|-)$", '0', regex=True).astype(float)
    )\
    .groupby('geocode',as_index=False).agg(
        BENS = ('BENS', 'sum')
        )
    [['geocode', 'BENS']]
    )

# Para os tratores, utilizou-se a tabea 860
#https://apisidra.ibge.gov.br/values/t/860/n6/1100015,1100023/v/1862/p/all/c12605/113521/c218/0/c12603/0/c220/0/c12517/113601

tratores = (processa_uf(UF,'860','/v/1862/p/all/c12605/113521/c218/0/c12603/0/c220/0/c12517/113601/d/2/f/c')\
  .rename(columns={'Município (Código)':'geocode','Valor':'TRAT'})\
    .assign(
      TRAT=lambda d: d['TRAT'].str.replace(r"^(\.\.\.|X|-)$", '0', regex=True).astype(float)
    )\
    .groupby('geocode',as_index=False).agg(
        TRAT = ('TRAT', 'sum')
        )
    [['geocode', 'TRAT']]
    )

bens_equip = pd.merge(bens_equip, tratores, on='geocode', how='outer')\
  .assign(
    BENS_TRAT = lambda d: d['TRAT'] + d['BENS']
  )
bens_equip.to_csv('./Dados_Final/bens_equip_06.csv',sep=',',decimal='.',encoding='UTF-8',index=False)

# Tabela 1113 - Trabalho
# https://apisidra.ibge.gov.br/values/t/1113/n6/1100015,1100023/v/2379/p/all/c2/0/c12896/0
trabalho = processa_uf(UF,'1113','/v/2379/p/all/c2/0/c12896/0/d/2/f/c')
trabalho.to_csv('./Dados_Final/trabalho_06.csv',sep=',',decimal='.',encoding='UTF-8',index=False)

# Tabela 6879 - Assistência técnica (aproveitou-se a tabela 6879 para baixar a área da agropecuária)
assist_tec = processa_uf(UF, '6879','/v/183/p/all/c829/46302/c12517/113601/c12567/113111/c12894/46569/d/2/f/c')

# Tabela 777 - Assistência técnica
# https://apisidra.ibge.gov.br/values/t/777/n6/1100015,1100023/v/allxp/p/all/c12594/0/c218/0/c12552/0/c12595/0/c12548/0,112010,112011

assist_tec0 = processa_uf(UF, '777','/v/allxp/p/all/c12594/0/c218/0/c12552/0/c12595/0/c12548/0,112010,112011/d/2/f/c')

assist_tec = (assist_tec0[['Município (Código)', 'Orientação técnica (Código)', 'Valor']]\
                .rename(columns={'Município (Código)':'geocode','Orientação técnica (Código)':'cod'})\
             .assign(
               Valor = lambda d: d['Valor'].str.replace(r"^(\.\.\.|X|-)$", '0', regex=True).astype(float),
               cod=lambda x: np.select(
                 [
                  (x['cod'] == '112010'),
                  (x['cod'] == '112011'),
                  (x['cod'] == '0')
              ],
                 ['Ocasionalmente', 'Regularmente','Total'],
              default='neutral'
              )
               ).pivot(index='geocode', columns='cod', values='Valor')\
                 .reset_index()\
                 .assign(
                   Recebeu = lambda d: d['Ocasionalmente'] + d['Regularmente'],
                   ASSIS_TEC = lambda d: (d['Recebeu'] / d['Total'])*100
                 )
                 [['geocode','ASSIS_TEC']]
                 )

assist_tec.to_csv('./Dados_Final/assist_tec_06.csv',sep=',',decimal='.',encoding='UTF-8',index=False)

# Tabela 855 - Área irrigada (Hectares)
# https://apisidra.ibge.gov.br/values/t/855/n6/1100015,1100023/v/2373/p/all/c12604/118477/c218/0/c12602/113606/c12548/0/c12603/0/d/v2373%200
area_irrigada_hect = processa_uf(UF, '855',
                                 '/v/2373/p/all/c12604/118477/c218/0/c12602/113606/c12548/0/c12603/0/d/2/f/c')
area_irrigada_hect.to_csv('./Dados_Final/area_irrigada_hect_06.csv',sep=',',decimal='.',encoding='UTF-8',index=False)

# Tabela 820
# https://apisidra.ibge.gov.br/values/t/820/n6/1100015,1100023/v/1996/p/all/c210/113946/c12548/0/c12567/0/c12552/0/d/v1996%200
despesas0 = processa_uf(UF, '820','/v/1996/p/all/c210/113946/c12548/0/c12567/0/c12552/0/d/2/f/c')

despesas = (despesas0[['Município (Código)', 'Tipo de despesa (Código)', 'Valor']]\
                .rename(columns={'Município (Código)':'geocode','Tipo de despesa (Código)':'cod'})\
             .assign(
               Total = lambda d: d['Valor'].str.replace(r"^(\.\.\.|X|-)$", '0', regex=True).astype(float)
               )
             [['geocode','Total']]
                 )

despesas.to_csv('./Dados_Final/despesas_totais_06.csv',sep=',',decimal='.',encoding='UTF-8',index=False)


# Tabela 1109 - Área ocupada pela agropecuária
# https://apisidra.ibge.gov.br/values/t/1109/n6/1100015,1100023/v/184/p/all/c218/0/c12896/0/d/v184%200

areaHec_agropec = processa_uf(UF, '1109','/v/184/p/all/c218/0/c12896/0/d/2/f/c')
areaHec_agropec.to_csv('./Dados_Final/areaHec_agropec_06.csv',sep=',',decimal='.',encoding='UTF-8',index=False)

