import time

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import List, Dict, NoReturn
import itertools as it


# FUNCION PARA TRATAMIENTO DE CSVs OBTENIDOS DEL SCRAPING

def tratamientoDeNulos(df: pd.DataFrame) -> NoReturn:
    """
    :param df: Dataframe con los datos recolectados de investing.com;
    Tiene columnas Date, Price, Vol y %Change
    :return: Solo modifica el df
    """
    # El % de cambio se pone a cero ya que si el mercado está cerrado no hay cambio
    if '%Change' in df.columns:
        df['%Change'].fillna('0%', inplace=True)
    # El volumen se pone a cero ya que si el mercado está cerrado no hay movimiento de acciones
    if 'Vol' in df.columns:
        df['Vol'].fillna(0., inplace=True)
    # Se rellena el precio con el valor del día anterior. EJ: si cierra el viernes a 150 pues sábado y domingo
    # se rellena a 150 el precio
    df.fillna(method='ffill', inplace=True)
    # Como no hay datos para el último día de 2019 se decide poner el precio de 02-01-2020 a 01-01-2020
    # siempre que sea nulo el precio del 01-01-2020
    df.loc[0, df.iloc[0, :].isnull()] = df.iloc[1, 1]


# -----------------------------------------------------------------------------------------------------------------------------------

# FUNCIONES PARA PARTE OBLIGATORIA

def crearCarteras(suma_componentes_cartera: int, activos: List[str]) -> List[Dict]:
    """
    :param suma_componentes_cartera: Es un parámtetro que indica cual va a ser la inversión total
    por cartera (es igual en todas, lo indica el enunciado)
    :param activos: Lista con los posibles activos para las carteras
    :return: Una lista de diccionarios, un diccionario para cartera
    """
    # Obtenemos un iterador con combinaciones con repetición de los activos
    carteras_posibles = it.combinations_with_replacement(activos, len(activos))
    peso_de_aparicion_en_la_combinacion = suma_componentes_cartera / len(activos)
    lista = []
    for cartera in carteras_posibles:
        diccionario = {'ST': 0, 'CB': 0, 'PB': 0, 'GO': 0, 'CA': 0}
        for activo in cartera:
            diccionario[activo] = int(diccionario[activo] + peso_de_aparicion_en_la_combinacion)
        lista += [diccionario]
    return lista


def rentabilidadPorPartes(datos: Dict[str, pd.DataFrame]) -> Dict[str, float]:
    """
    :param datos: Los datos son un diccionario cuya clave es el nombre del activo y el
    valor es un dataframe con los datos de los csv
    :return: diccionario con la rentabilidad de cada activo en un año
    """
    ganancia_indice = {}
    for activo in datos:
        precio_inicial = datos[activo].loc[0, "Price"]
        precio_final = datos[activo].loc[len(datos[activo]) - 1, "Price"]
        ganancia_indice.update({activo: (1 + ((precio_final - precio_inicial) / precio_inicial))})
    return ganancia_indice


def rendimiento(carteras: pd.DataFrame, datos: Dict[str, pd.DataFrame]) -> List[np.float64]:
    """
    :param carteras: Dataframe con las carteras
    :param datos: Los datos son un diccionario cuya clave es el nombre del activo y el
    valor es un dataframe con los datos de los csv (web scraping)
    :return: lista con la rentabilidad de cada cartera (en porcentaje)
    """
    rentabilidad_de_cada_activo = rentabilidadPorPartes(datos)
    n_columnas = len(carteras.loc[1, :])
    lista_rentabilidades = []
    # Recorremos todas las carteras (1 cartera por fila)
    for fila in range(len(carteras.index)):
        importe_de_compra = 0
        valor_actual = 0
        cartera = carteras.iloc[fila, :]
        # Dentro de cada cartera recorremos los activos
        for columna in range(n_columnas):
            """
            · Para cada activo sacamos la rentabilidad de datos y lo mutiplicamos
            por el precio inicial
            · En importe_de_compra se va acumulando la inversón de cada activo
            en la cartera
            · En el valor_actual se acumula el dinero que se consigue tras retirar
            la inversión
            """
            activo = carteras.columns[columna]
            importe_de_compra += cartera.iloc[columna]
            valor_actual += cartera.iloc[columna] * rentabilidad_de_cada_activo[activo]

        rentabilidad = ((valor_actual - importe_de_compra) / importe_de_compra) * 100
        lista_rentabilidades += [round(rentabilidad, 4)]

    return lista_rentabilidades


# -----------------------------------------------------------------------------------------------------------------------------------


# FUNCIONES PARA PARTE OPCIONAL

def participaciones_cartera(cartera: pd.Series, datos: Dict[str, pd.DataFrame]) -> Dict[str, float]:
    """
    :return:  Dada una cartera calcula las participaciones de cada activo en la cartera
    """
    participaciones = {}
    for activo in cartera.index:
        participaciones[activo] = cartera[activo] / datos[activo].loc[0, "Price"]

    return participaciones


def desviacion_estandar(values: List[float], promedio: float) -> float:
    """
    :return:  Calcula la desviación estándar de una cartera dada la fórmula
    """
    n_dias = len(values)
    sumatorio: float = 0
    for dia in range(n_dias):
        sumatorio += (values[dia] - promedio) ** 2

    return ((1 / n_dias) * sumatorio) ** (1 / 2)


def volatilidad(values, promedio) -> float:
    """
    :return:  Calcula la volatilidad de una cartera a partir de la desviación estándar
    """
    return round(((desviacion_estandar(values, promedio) / promedio) * 100), 4)


def calculo_lista_volatilidades(carteras: pd.DataFrame, datos: Dict[str, pd.DataFrame]):
    """
    :param carteras: dataframe con las posibles carteras
    :param datos: datos de los activos (conseguidos mediante web scraping)
    :return: Devuelve una lista con la volatilidad de cada cartera
    """

    n_dias = len(datos["ST"]["Date"])  # nº de días == filas del df
    volatility = []

    for indice_cartera in carteras.index:  # Recorremos las carteras

        # Para cada cartera calculamos el promedio y los 'values'
        cartera = carteras.loc[indice_cartera]
        promedio = 0
        participaciones = participaciones_cartera(cartera, datos)
        values: List[float] = [0] * 366

        for dia in range(n_dias):
            for activo in datos:
                value = datos[activo].loc[dia, "Price"] * participaciones[activo]
                promedio += value
                values[dia] += value

        promedio = promedio / n_dias
        volatility += [volatilidad(values, promedio)]

    return volatility


# -----------------------------------------------------------------------------------------------------------------------------------


def main():
    # TRATAMIENTO DE CSV SACADOS DEL SCRAPING (NECESARIOS PARA AMBAS PARTES)

    # Leemos los csv y meterlos en un diccionario
    datasets_dic = {}
    datasets_dic.update({"ST": pd.read_csv('amundi-msci-wrld-ae-c.csv', sep=";")})
    datasets_dic.update({"CB": pd.read_csv('ishares-global-corporate-bond-$.csv', sep=";")})
    datasets_dic.update({"PB": pd.read_csv('db-x-trackers-ii-global-sovereign-5.csv', sep=";")})
    datasets_dic.update({"GO": pd.read_csv('spdr-gold-trust.csv', sep=";")})
    datasets_dic.update({"CA": pd.read_csv('usdollar.csv', sep=";")})
    # Convertimos la columna Vol del dollar en 0s, ya que su valor es - para toda fila
    datasets_dic['CA']['Vol'] = 0
    datasets_dic['ST']['Vol'] = 0

    # Completamos los dataframes con los datos para que tengan todos los días del año:
    dates = pd.date_range('2020-01-01 00:00:00', periods=366)
    # Generamos un df con todas las fechas de 2020
    df_fechas = pd.DataFrame(dates, columns=['Date'])

    for activo in datasets_dic.keys():
        # Normalizamos el formato de las fechas, para que sean igules que las generadas en dates
        datasets_dic[activo].iloc[:, 0] = pd.to_datetime(datasets_dic[activo].iloc[:, 0],
                                                         infer_datetime_format=True)
        # Hacemos la unión de dates y el df de cada activo; Las fechas que ya estaban se mantienen
        # y las que no se añaden rellenando el resto de columnas con NaN (se ordenan de primer a último dia)
        datasets_dic[activo] = pd.merge(df_fechas, datasets_dic[activo], on='Date', how='outer')
        # Se tratan los nulos
        tratamientoDeNulos(datasets_dic[activo])

    # Modificación del us dollar para cumplir los requisitos
    datasets_dic["CA"].loc[0, "Price"] = 100
    for dia in datasets_dic["CA"].index:
        datasets_dic["CA"].loc[dia, "Price"] = (datasets_dic["CA"].loc[dia, "Price"] / 100)

    # EJECUCIÓN INDEPENDIENTE MEDIANTE INPUTS Y UN WHILE
    introducido = ''
    while introducido != '1' and introducido != '2':
        print("Devuelva 1 para generar gráfico y csv con rentabilidad")
        print("Devuelva 2 para  generar gráfico y csv rentabilidad y volatilidad")
        introducido = input('Escriba aquí su elección:  ')

        if introducido == '1':
            # Creamos el dataFrame con las carteras
            activos = ['ST', 'CB', 'PB', 'GO', 'CA']
            suma_cartera = 100
            df_carteras = pd.DataFrame(crearCarteras(suma_cartera, activos))

            # Añadimos al dataframe de carteras (copia) la columna return con la rentabilidad/rendimiento
            df_carteras["RETURN"] = rendimiento(df_carteras, datasets_dic)

            # Escribimos el dataframe en un csv
            df_carteras.to_csv('portfolio_returns.csv', index=False)

            # Generación de gráfica para análisis
            grafica1 = ''
            while grafica1 != 'yes' and grafica1 != 'no':
                grafica1 = str.lower(input('\n¿Desea ver la gráfica con el rendimiento de las carteras? (yes/no):  '))

                if grafica1 == 'yes':
                    # Plot para visualizar si es más probable encontrar carteras con rendimiento positivo o negativo
                    x_values = range(1, 127)
                    y_values = df_carteras['RETURN']
                    plt.plot(x_values, y_values, 'bo')
                    plt.axhline(0, c='r')
                    csfont = {'fontname': 'Comic Sans MS'}  # Para cambiar la fuente del título
                    plt.title("RENDIMIENTO DE LAS CARTERAS", csfont)
                    plt.ylabel("Rendimiento")
                    plt.show()

        if introducido == "2":
            # Cargamos el dataframe de carteras con rendimiento (columna RETURN)
            df_carteras_rend_vol = pd.read_csv('portfolio_returns.csv', sep=",")

            # Añadimos la columna VOLAT al df
            df_carteras_rend_vol["VOLAT"] = calculo_lista_volatilidades(df_carteras_rend_vol.iloc[:, 0:5], datasets_dic)

            # Escribimos el dataframe en un csv
            df_carteras_rend_vol.to_csv('portfolio_volatility.csv', index=False)

            # Generación de gráfica para análisis
            grafica2 = ''
            while grafica2 != 'yes' and grafica2 != 'no':
                grafica2 = str.lower(input('\n¿Desea ver la gráfica comparando el rendimiento y la volatilidad? ('
                                           'yes/no):  '))

                if grafica2 == 'yes':
                    csfont = {'fontname': 'Comic Sans MS'}  # Para cambiar la fuente del título
                    plt.figure(figsize=(8, 8), tight_layout=True)  # Para fijar el tamaño de la pestaña

                    # Hacemos un scatter plot
                    plt.subplot(211)
                    x_values = df_carteras_rend_vol['VOLAT']
                    y_values = df_carteras_rend_vol['RETURN']
                    plt.plot(x_values, y_values, 'go')
                    plt.title("VOLATILIDAD VS RENDIMIENTO", csfont)
                    plt.xlabel("Volatility")
                    plt.ylabel("Return")

                    # Realizamos un stem plot (mismos datos, otro tipo de visualización)
                    plt.subplot(212)
                    plt.stem(x_values, y_values)
                    plt.xlabel("Volatility")
                    plt.ylabel("Return")
                    plt.show()

        elif introducido != '1':
            print('\nLas opciones son 1 o 2; lo que ha introducido no es válido')


if __name__ == "__main__":
    main()
