#!/usr/bin/env python
# coding: utf-8

# In[148]:


import pandas as pd
import numpy as np
import time
from typing import List, Dict, TypeVar
import itertools as it


# In[105]:


# leer los csv y meterlos en un diccionario (es el que estoy usando)
datasets_dic = {}
datasets_dic.update({"ST": pd.read_csv('amundi-msci-wrld-ae-c.csv', sep=";")})
datasets_dic.update({"CB": pd.read_csv('ishares-global-corporate-bond-$.csv', sep=";")})
datasets_dic.update({"PB": pd.read_csv('db-x-trackers-ii-global-sovereign-5.csv', sep=";")})
datasets_dic.update({"GO": pd.read_csv('spdr-gold-trust.csv', sep=";")})
datasets_dic.update({"CA": pd.read_csv('usdollar.csv', sep=";")})


# In[69]:


def combinations_with_replacement(iterable, r):
    # combinations_with_replacement('ABC', 2) --> AA AB AC BB BC CC
    # Sacado de internet
    pool = tuple(iterable)
    n = len(pool)
    if not n and r:
        return
    indices = [0] * r
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != n - 1:
                break
        else:
            return
        indices[i:] = [indices[i] + 1] * (r - i)
        yield tuple(pool[i] for i in indices)


# In[206]:


def crearCarteras(sumaConponentesCartera: int, partes : int) -> List[Dict]:
    # sumaConponentesCartera es el capital inicial de las carteras
    # sumaConponentesCartera/partes indica el salto minimo entre carteras
    saltoMinimo = sumaConponentesCartera/partes
    it = combinations_with_replacement(['ST','CB','PB','GO','CA'], partes)
    lista = []
    for j in it:
        dicionario = {'ST':0, 'CB':0, 'PB':0,'GO':0, 'CA':0}
        for i in j:
            dicionario[i] = int(dicionario[i]+(saltoMinimo))
        lista += [dicionario]
    return lista


# In[142]:


def retabilidaddic(df):
    ganaciaIndice = {}
    for i in df:
        precioInicio = df[i].loc[len(df[i])-1,"Price"]
        precioFinal = df[i].loc[0,"Price"]
        ganaciaIndice.update({i:((precioFinal-precioInicio)/(precioInicio))})
    return ganaciaIndice

def calcularGanacia(carteras, df):
    # este metodo recive una cartera o lista de estas y calcula el porcentaje de ganacias
    ratioCien = 100/sum(df_carteras.iloc[1,:]) # esta variable sirve para compesar en el caso del que el sumatorio de los componentes de la carteran no sumen 100
    ganaciaIndice = retabilidaddic(df)
    nColumnas = len(carteras.loc[1,:])
    listaGanacias = []
    for fila in range(len(carteras.index)):
        ganancia = 0
        for columna in range(nColumnas):
            ganancia += carteras.iloc[fila,columna]*ganaciaIndice[carteras.columns[columna]]*ratioCien
        listaGanacias += [ganancia]
    return listaGanacias


# In[147]:


def rendimiento(carteras: pd.DataFrame, datos: Dict[str, pd.DataFrame]) ->         List[np.float64]:
    """
       Esta función recibe un dataframe de carteras y un diccionario con los datos
        de cada activo y calcula el rendimiento para cada cartera
      """
    n_columnas = len(carteras.loc[1, :])
    lista_rentabilidades = []
    # Recorremos todas las carteras (1 cartera por fila)
    for fila in range(len(carteras.index)):
        importe_de_compra = 0
        valor_actual = 0
        # Dentro de cada cartera recorremos los activos
        for columna in range(n_columnas):
            """
            · Para cada activo sacamos el precio cuando se invirtió y el precio 
            cuando se retiró a inversión (precio_inicio, precio_final)
            · En importe_de_compra se va acumulando la inversón de cada activo
            en la cartera
            · En el valor_actual se acumula el dinero que se consigue tras retirar
            la inversión
            """
            activo = carteras.columns[columna]
            precio_inicio = datos[activo].loc[len(datos[activo]) - 1, "Price"]
            precio_final = datos[activo].loc[0, "Price"]
            importe_de_compra += carteras.iloc[fila, columna]
            valor_actual += (carteras.iloc[fila, columna] / precio_inicio) * precio_final

        rentabilidad = ((valor_actual - importe_de_compra) / importe_de_compra) * 100
        lista_rentabilidades += [round(rentabilidad, 4)]

    return lista_rentabilidades


# In[204]:


def retabilidadPorPartes(df):
    ganaciaIndice = {}
    for i in df:
        precioInicio = df[i].loc[len(df[i])-1,"Price"]
        precioFinal = df[i].loc[0,"Price"]
        ganaciaIndice.update({i:(1+((precioFinal-precioInicio)/(precioInicio)))})
    return ganaciaIndice

def rendimiento2(carteras: pd.DataFrame, datos: Dict[str, float]) ->         List[np.float64]:
    """
       Esta función recibe un dataframe de carteras y un diccionario con la
       rentavilidad que tiene cada componente de las carteras
    """
    n_columnas = len(carteras.loc[1, :])
    lista_rentabilidades = []
    # Recorremos todas las carteras (1 cartera por fila)
    for fila in range(len(carteras.index)):
        importe_de_compra = 0
        valor_actual = 0
        # Dentro de cada cartera recorremos los activos
        for columna in range(n_columnas):
            """
            · Para cada activo sacamos la retavilidad de datos y lo mutiplicamos
            por el precio inicial
            · En importe_de_compra se va acumulando la inversón de cada activo
            en la cartera
            · En el valor_actual se acumula el dinero que se consigue tras retirar
            la inversión
            """
            activo = carteras.columns[columna]
            importe_de_compra += carteras.iloc[fila, columna]
            valor_actual += carteras.iloc[fila, columna] * datos[carteras.columns[columna]]
        
        rentabilidad = ((valor_actual - importe_de_compra) / importe_de_compra) * 100
        lista_rentabilidades += [round(rentabilidad, 4)]

    return lista_rentabilidades


# In[208]:


partes = 5
sumaCarteras = 100
# estan ordenados por orden de creacion que coincide con el orden de arriva abajo en este notebook

# creamos el dataFrame con las carteras
df_carteras = pd.DataFrame(crearCarteras(sumaCarteras, partes))
df_carteras

# metodo 1
inicio = time.time()
df_carteras["return"] = calcularGanacia(df_carteras, df)
final = time.time()
print(final - inicio)

# creamos el dataFrame con las carteras
df_carteras = pd.DataFrame(crearCarteras(sumaCarteras, partes))
df_carteras

# metodo 2
inicio = time.time()
df_carteras["RETURN"] = rendimiento(df_carteras, datasets_dic)
final = time.time()
print(final - inicio)

# creamos el dataFrame con las carteras
df_carteras = pd.DataFrame(crearCarteras(sumaCarteras, partes))
df_carteras

# metodo 3
inicio = time.time()
df_carteras["RETURN"] = rendimiento2(df_carteras, retabilidadPorPartes(datasets_dic))
final = time.time()
print(final - inicio)

