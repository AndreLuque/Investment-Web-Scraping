# -----------------
# Prácitca 1 - grupo 05
# -----------------

import csv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


# No olvidar poner SU path a su chromedriver
driver = webdriver.Chrome(r"C:\Users\Usuario\Desktop\gonzalo jr\CDIA\segundo de carrera\primer "
                          r"cuatri\Progra\chromedriver.exe")

lista_nombre_csv = [
    "amundi-msci-wrld-ae-c.csv",
    "ishares-global-corporate-bond-$.csv",
    "db-x-trackers-ii-global-sovereign-5.csv",
    "spdr-gold-trust.csv",
    "usdollar.csv"
]
lista_enlaces = [
    "https://www.investing.com/funds/amundi-msci-wrld-ae-c",
    "https://www.investing.com/etfs/ishares-global-corporate-bond-$",
    "https://www.investing.com/etfs/db-x-trackers-ii-global-sovereign-5",
    "https://www.investing.com/etfs/spdr-gold-trust",
    "https://www.investing.com/indices/usdollar"
]

# En vez de hacer cinco "subprogramas" hacemos un bucle para todas las páginas de activos
for numero_enlace in range(len(lista_enlaces)):
    driver.get(lista_enlaces[numero_enlace])
    #driver.maximize_window()

    # Aceptamos las cookies, que solo aparecen al abrir la primera página:
    if numero_enlace == 0:
        try:
            accept_button = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.ID, "onetrust-accept-btn-handler")))
            accept_button.click()
        except TimeoutException:
            print("No han aparecido las cookies (Tiempo max de espera: 10 seg)")


    # Accedemos al historical data:
    try:
        """
        La página del dolar tiene una estructura diferente al resto para esta 
        parte, este if gestiona dicha excepción.
        """
        if lista_enlaces[numero_enlace] == "https://www.investing.com/indices/usdollar":
            historical_data_button = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located(
                    (By.XPATH, f'//*[@class="inv-link navbar_navbar-sub-item-link__1mznu"]')))
            historical_data_button.click()
        else:
            """
            Con esta primera parte del else lo que hacemos es buscar que <li>
            de los que estan dentro de <ul class="arial_12 newBigSubTabs " id="pairSublinksLevel2">
            es el botón de historical data, ya que en función del activo esto cambia.
            """
            texto = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((
                    By.XPATH, "//*[@id='pairSublinksLevel2']"))).text.split(sep='\n')
            encontrado: bool = False
            contador: int = 0
            while not encontrado:
                if texto[contador] == "Historical Data":
                    encontrado = True
                contador += 1
            # esta segunda parte selecciona/pulsa el historical data button
            historical_data_button = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.XPATH, f"//*[@id='pairSublinksLevel2']/li[{contador}]/a")))
            historical_data_button.click()
    except TimeoutException:
        print("No se ha podido acceder al historical data (Tiempo max de espera: 10 seg)")


    # Accedemos a la seleccion de fechas:
    try:
        date_selection_button = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.ID, "widgetFieldDateRange")))
        date_selection_button.click()
    except TimeoutException:
        print("No se ha podido acceder al boton de 'seleccionar fechas' (Tiempo max de espera: 10 seg)")


    # Rellenamos con las fechas que nos interesan:
    try:
        start_date = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.ID, "startDate")))
        start_date.clear()
        start_date.send_keys('01/01/2020')
    except TimeoutException:
        print("La fecha inicial que quiere seleccionar no está disponible")
    try:
        end_date = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.ID, "endDate")))
        end_date.clear()
        end_date.send_keys('12/31/2020')
    except TimeoutException:
        print("La fecha final que quiere seleccionar no está disponible")


    # Aplicamos las fechas seleccionadas
    try:
        apply_button = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.ID, "applyBtn")))
        apply_button.click()
    except TimeoutException:
        print("El Buton de 'apply' no está disponible (Tiempo max de espera: 10 seg)")


    # Accedemos a la tabla para extraer lo que nos interesa y transformarlo en un csv
    try:
        """
        Con este try lo que conseguimos es dar un tiempo para que cargue la tabla,
        así evitando recolectar datos sin la tabla cargada (evitas excepción)
        """
        primer_elemento = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.XPATH, '//*[@id="leftColumn"]/div[9]/table[1]/tbody/tr[1]/td[1]')))
    finally:
        tabla = driver.find_element_by_xpath('//*[@id="curr_table"]/tbody').text.split(sep='\n')

        with open(lista_nombre_csv[numero_enlace], 'w', newline='\n') as csvfile:
            csvtool = csv.writer(csvfile, delimiter=';')
            csvtool.writerow(['Date', 'Price', 'Vol', '%Change'])

            """
            Los acciones globales no tienen columna 'volumen' por eso se hace un if
            para rellenarla de guiones (al igual que hace la web con el dolar)
            """
            if numero_enlace == 0:
                for fila in tabla:
                    fila = fila.split()
                    """ fila[0] = mes, fila[1] = dia(seguido de una coma), fila[2] = año,
                     fila[3] = precio inicial, - , fila[-1] = variación diaria"""
                    csvtool.writerow([fila[0] + " " + fila[1] + " " + fila[2], fila[3], "-", fila[-1]])
            else:
                for fila in tabla:
                    fila = fila.split()
                    """ fila[0] = mes, fila[1] = dia(seguido de una coma), fila[2] = año,
                     fila[3] = precio inicial, fila[-2] = volumen, fila[-1] = variación diaria"""
                    csvtool.writerow([fila[0] + " " + fila[1] + " " + fila[2], fila[3], fila[-2], fila[-1]])

driver.close()
