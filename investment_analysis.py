import numpy as np
import pandas as pd
from typing import List, Dict, TypeVar
import itertools as it

# Activos = TypeVar('Activos')


# leer los csv y meterlos en un diccionario (es el que estoy usando)
datasets_dic = {}
datasets_dic.update({"ST": pd.read_csv('amundi-msci-wrld-ae-c.csv', sep=";")})
datasets_dic.update({"CB": pd.read_csv('ishares-global-corporate-bond-$.csv', sep=";")})
datasets_dic.update({"PB": pd.read_csv('db-x-trackers-ii-global-sovereign-5.csv', sep=";")})
datasets_dic.update({"GO": pd.read_csv('spdr-gold-trust.csv', sep=";")})
datasets_dic.update({"CA": pd.read_csv('usdollar.csv', sep=";")})

# def combinations_with_replacement(iterable, r):
#     # combinations_with_replacement('ABC', 2) --> AA AB AC BB BC CC
#     # Sacado de internet
#     pool = tuple(iterable)
#     n = len(pool)
#     if not n and r:
#         return
#     indices = [0] * r
#     yield tuple(pool[i] for i in indices)
#     while True:
#         for i in reversed(range(r)):
#             if indices[i] != n - 1:
#                 break
#         else:
#             return
#         indices[i:] = [indices[i] + 1] * (r - i)
#         yield tuple(pool[i] for i in indices)


# Obtenemos un iterador con combinaciones con repetición de los 5 activos
n_activos = 5
activos = ['ST', 'CB', 'PB', 'GO', 'CA']
carteras_posibles = it.combinations_with_replacement(activos, n_activos)

# Creamos una lista con tantos diccionarios como carteras hay (126)
lista_carteras = []
for cartera in carteras_posibles:
    dic_activos = {'ST': 0, 'CB': 0, 'PB': 0, 'GO': 0, 'CA': 0}  # clave:tipo activos; valor: % invertido
    for activo in cartera:
        dic_activos[activo] = dic_activos[activo] + (200 / n_activos)
    lista_carteras += [dic_activos]

# Creamos un dataFrame con las carteras
df_carteras = pd.DataFrame(lista_carteras)


# print(df_carteras)


def cambio_de_precio(datos: Dict[str, pd.DataFrame]) -> Dict[str, np.float64]:
    """
    Dado un diccionario:
            clave --> nombre activo
            valor --> dataframe con los datos del activo en x tiempo

     Devuelve un diccionario con el cambio de precio en porcentaje de cada activo en ese tiempo
    """
    porcentaje_de_cambio = {}
    for activo in datos.keys():
        precio_inicio = datos[activo].loc[len(datos[activo]) - 1, "Price"]
        precio_final = datos[activo].loc[0, "Price"]
        # print(activo, "   precio_inicio  ", precio_inicio, "precio_final  ", precio_final)
        cambio_del_activo = (precio_final - precio_inicio) / precio_inicio
        porcentaje_de_cambio.update({activo: cambio_del_activo})
    return porcentaje_de_cambio


def rendimiento(carteras: pd.DataFrame, datos: Dict[str, pd.DataFrame]) -> \
        List[np.float64]:
    """
     Esta función recibe un dataframe de carteras y un diccionario con los datos
      de cada activo y calcula el porcentaje de ganacias para cada cartera
    """
    porcentaje_de_cambio = cambio_de_precio(datos)
    n_columnas = len(carteras.loc[1, :])
    lista_rentabilidad = []
    # Recorremos todas las carteras (1 cartera por fila)
    for fila in range(len(carteras.index)):
        rentabilidad = 0
        # Dentro de cada cartera recorremos los activos
        for columna in range(n_columnas):
            # Acumulamos en rentabilidad: inversion en cada activo*cambio de precio en % del activo
            rentabilidad += carteras.iloc[fila, columna] * porcentaje_de_cambio[carteras.columns[columna]]
        lista_rentabilidad += [rentabilidad]

    return lista_rentabilidad


# DUDA: TENGO QUE RELLENAR LOS DATASETS CON LAS FECHAS QUE FALTAN???


df_carteras["return"] = rendimiento(df_carteras, datasets_dic)
print(df_carteras[100:130])
