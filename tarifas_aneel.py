#!/usr/bin/env python
#coding: utf-8
import pandas as pd
from datetime import datetime

url = 'https://dadosabertos.aneel.gov.br/dataset/5a583f3e-1646-4f67-bf0f-69db4203e89e/resource/fcf2906c-7c32-4b9b-a637-054e7a5234f4/download/tarifas-homologadas-distribuidoras-energia-eletrica.csv'
tarifas = pd.read_csv(url, low_memory=False,encoding='latin-1',sep=';')
#tarifas = pd.read_csv(r'C:\Users\guisa\Downloads\mysite\tarifas.csv', low_memory=False,encoding='latin-1',sep=';')

distribuidoras =tarifas['SigAgente'].dropna().unique().tolist()

tarifas = tarifas[(tarifas['DscBaseTarifaria'] == "Tarifa de Aplicação")]
tarifas = tarifas[(tarifas['SigAgenteAcessante'] == "Não se aplica")]
tarifas = tarifas[(tarifas['DscDetalhe'] == "Não se aplica")]
tarifas = tarifas[(tarifas['DscModalidadeTarifaria'] == "Azul")|(tarifas['DscModalidadeTarifaria'] == "Verde")]
tarifas = tarifas[(tarifas['DscSubGrupo'] == "A2")|(tarifas['DscSubGrupo'] == "A3")|(tarifas['DscSubGrupo'] == "A3a")|(tarifas['DscSubGrupo'] == "A4")|(tarifas['DscSubGrupo'] == "AS")]
tarifas = tarifas.reset_index(drop=True)

tarifas['VlrTUSD']=tarifas['VlrTUSD'].str.replace(',','.')
tarifas['VlrTE']=tarifas['VlrTE'].str.replace(',','.')

for a in range(0,len(tarifas)):
    tarifas.loc[a,'DatFimVigencia']=datetime.strptime(tarifas.loc[a,'DatFimVigencia'], '%Y-%M-%d')
dict_types = {"DatFimVigencia":"datetime64[ns]"}
tarifas = tarifas.astype(dict_types)

for a in range(0,len(tarifas)):
    tarifas.loc[a,'AnoVigencia']=tarifas.loc[a,'DatFimVigencia'].year
tarifas = tarifas[(tarifas['AnoVigencia'] > 2023)]

tarifas = tarifas.reset_index(drop=True)
tarifas.set_index(['SigAgente','DscSubGrupo','DscModalidadeTarifaria','NomPostoTarifario','DscUnidadeTerciaria'], inplace=True)
tarifas.sort_index()

def tarifa_atual(distribuidora,subgrupo,modalidade):
    """
    Retorna as tarifas para simulação das contas no cativo e livre.
    Parametros:
    distribuidora
    subgrupo: A2, A3, A3a, A4, AS
    modalidade: Azul e Verde
    Uso:
    Para usar digite
    tarifa_atual(distribuidora,subgrupo,modalidade)
    """
    try:
        if (modalidade == 'Verde'):
            demanda_fp_kw = tarifas.query("SigAgente == @distribuidora and DscSubGrupo == @subgrupo and DscModalidadeTarifaria == @modalidade and NomPostoTarifario =='Não se aplica' and DscUnidadeTerciaria =='kW'")
            demanda_ponta_kw = 0
            TUSDd_P = 0
        elif (modalidade == 'Azul'):
            demanda_ponta_kw = tarifas.query("SigAgente == @distribuidora and DscSubGrupo == @subgrupo and DscModalidadeTarifaria == @modalidade and NomPostoTarifario =='Ponta' and DscUnidadeTerciaria =='kW'")
            demanda_fp_kw = tarifas.query("SigAgente == @distribuidora and DscSubGrupo == @subgrupo and DscModalidadeTarifaria == @modalidade and NomPostoTarifario =='Fora ponta' and DscUnidadeTerciaria =='kW'")
            TUSDd_P = float(demanda_ponta_kw.iloc[0,10])

        fora_ponta_mwh =  tarifas.query("SigAgente == @distribuidora and DscSubGrupo == @subgrupo and DscModalidadeTarifaria == @modalidade and NomPostoTarifario =='Fora ponta' and DscUnidadeTerciaria =='MWh'")
        ponta_mwh =  tarifas.query("SigAgente == @distribuidora and DscSubGrupo == @subgrupo and DscModalidadeTarifaria == @modalidade and NomPostoTarifario =='Ponta' and DscUnidadeTerciaria =='MWh'")
        TE_FP = float(fora_ponta_mwh.iloc[0,11])/1000
        TUSDe_FP = float(fora_ponta_mwh.iloc[0,10])/1000
        TE_P = float(ponta_mwh.iloc[0,11])/1000
        TUSDe_P = float(ponta_mwh.iloc[0,10])/1000
        TUSDd_FP = float(demanda_fp_kw.iloc[0,10])

        DscREH = fora_ponta_mwh.iloc[0,1]
        #print("TE_FP " + str(TE_FP))
        #print("TE_P " + str(TE_P))
        #print("TUSDd_FP " + str(TUSDd_FP))
        #print("TUSDd_P " + str(TUSDd_P))
        #print("TUSDe_P " + str(TUSDe_P))
        #print("TUSDe_FP " + str(TUSDe_FP))
        #print("DscREH " + DscREH)
        return TE_FP, TUSDe_FP, TE_P, TUSDe_P, TUSDd_P, TUSDd_FP, DscREH
    except:
        return 0,0,0,0,0,0,0

distribuidora = 'LIGHT'
subgrupo = 'A4'
modalidade = 'Azul'
print(tarifa_atual(distribuidora,subgrupo,modalidade)[6])

