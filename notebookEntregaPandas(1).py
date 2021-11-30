#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np


# In[3]:


# opcion 1:  leer los csv
df_ST = pd.read_csv('amundi-msci-wrld-ae-c.csv', sep=";")
df_CB = pd.read_csv('ishares-global-corporate-bond-$.csv', sep=";")
df_PB = pd.read_csv('db-x-trackers-ii-global-sovereign-5.csv', sep=";")
df_GO = pd.read_csv('spdr-gold-trust.csv', sep=";")
df_CA = pd.read_csv('usdollar.csv', sep=";")


# In[2]:


# opcion 2: leer los csv y meterlos en un diccionario (es el que estoy usando)
df = {}
df.update({"ST": pd.read_csv('amundi-msci-wrld-ae-c.csv', sep=";")})
df.update({"CB": pd.read_csv('ishares-global-corporate-bond-$.csv', sep=";")})
df.update({"PB": pd.read_csv('db-x-trackers-ii-global-sovereign-5.csv', sep=";")})
df.update({"GO": pd.read_csv('spdr-gold-trust.csv', sep=";")})
df.update({"CA": pd.read_csv('usdollar.csv', sep=";")})


# In[3]:


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


# Con estos comandos creamos las carteras y las metemos en diccionario listo para pasarlo a DataFrame (no estoy seguro de  gestinar las carteras con un dataFrame)

# In[4]:


partes = 5 # 100/partes indica el salto minimo entre carteras
it = combinations_with_replacement(['ST','CB','PB','GO','CA'], partes)
lista = []
for j in it:
    dicionario = {'ST':0, 'CB':0, 'PB':0,'GO':0, 'CA':0}
    for i in j:
        dicionario[i] = int(dicionario[i]+(100/partes))
    lista += [dicionario]


# In[5]:


# creamos el dataFrame con las carteras
df_carteras = pd.DataFrame(lista)
df_carteras


# In[122]:


def retabilidaddic(df):
    ganaciaIndice = {}
    for i in df:
        precioInicio = df[i].loc[len(df[i])-1,"Price"]
        precioFinal = df[i].loc[0,"Price"]
        ganaciaIndice.update({i:((precioInicio-precioFinal)/(precioInicio))})
    return ganaciaIndice

def calcularGanacia(carteras, df):
    # este metodo recive una cartera o lista de estas y calcula el porcentaje de ganacias
    ganaciaIndice = retabilidad(df)
    nColumnas = len(carteras.loc[1,:])
    listaGanacias = []
    for fila in range(len(carteras.index)):
        ganancia = 0
        for columna in range(nColumnas):
            ganancia += carteras.iloc[fila,columna]*ganaciaIndice[carteras.columns[columna]]
        listaGanacias += [ganancia]
        
    return listaGanacias


# In[127]:


df_carteras["return"] = calcularGanacia(df_carteras, df)
df_carteras


# In[117]:


df_carteras.iloc[2, 2]


# In[54]:


nColumnas = len(df_carteras.loc[1,:])
nColumnas


# In[ ]:




