import numpy as np
import pandas as pd
from typing import List, Dict, TypeVar
import itertools as it

# Activos = TypeVar('Activos')

# Leer los csv y meterlos en un diccionario (es el que estoy usando)
datasets_dic = {}
datasets_dic.update({"ST": pd.read_csv('amundi-msci-wrld-ae-c.csv', sep=";")})
datasets_dic.update({"CB": pd.read_csv('ishares-global-corporate-bond-$.csv', sep=";")})
datasets_dic.update({"PB": pd.read_csv('db-x-trackers-ii-global-sovereign-5.csv', sep=";")})
datasets_dic.update({"GO": pd.read_csv('spdr-gold-trust.csv', sep=";")})
datasets_dic.update({"CA": pd.read_csv('usdollar.csv', sep=";")})

# Obtenemos un iterador con combinaciones con repetición de los 5 activos
n_activos = 5
activos = ['ST', 'CB', 'PB', 'GO', 'CA']
carteras_posibles = it.combinations_with_replacement(activos, n_activos)

# Creamos una lista con tantos diccionarios como carteras hay (126)
lista_carteras = []
for cartera in carteras_posibles:
    dic_activos = {'ST': 0, 'CB': 0, 'PB': 0, 'GO': 0, 'CA': 0}  # clave:tipo activos; valor: % invertido
    for activo in cartera:
        dic_activos[activo] = dic_activos[activo] + (100 / n_activos)
    lista_carteras += [dic_activos]

# Creamos un dataFrame con las carteras
df_carteras = pd.DataFrame(lista_carteras)


# DUDA: TENGO QUE RELLENAR LOS DATASETS CON LAS FECHAS QUE FALTAN???


def rendimiento(carteras: pd.DataFrame, datos: Dict[str, pd.DataFrame]) -> \
        List[np.float64]:
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


df_carteras["RETURN"] = rendimiento(df_carteras, datasets_dic)
# print(df_carteras[100:130])

# Escribimos el datframe en un csv
df_carteras.to_csv('portfolio_returns.csv', index=False)
