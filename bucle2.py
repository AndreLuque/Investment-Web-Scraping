import csv
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

inicio = time.time()

driver = webdriver.Chrome(r"C:\Users\Rodrigo Durán Andrés\PycharmProjects\pythonProject\webscraping\chromedriver_win32\chromedriver.exe")

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

for numero_enlace in range(len(lista_enlaces)):
    driver.get(lista_enlaces[numero_enlace])
    # driver.maximize_window()

    # Aceptamos las cookies de la página:
    try:
        accept_button = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.ID, "onetrust-accept-btn-handler")))
        accept_button.click()

    except TimeoutException:
        print("No han aparecido las cookies")

    # Accedemos al historical data:
    try:
        # no se muy bien por que pero la pagina del dolar tiene una estructura diferente para esta parte,
        # este if gestiona dicha excepcion.
        if lista_enlaces[numero_enlace] == "https://www.investing.com/indices/usdollar":
            historical_data_button = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located(
                    (By.XPATH, f'//*[@class="inv-link navbar_navbar-sub-item-link__1mznu"]')))
            historical_data_button.click()
        else:
            # esta primera part sirve para determinar que li[n] le corresponde a Historical Data
            texto = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((
                    By.XPATH,"//*[@id='pairSublinksLevel2']"))).text.split(sep='\n')
            encontrado = False
            contador = 0
            while not encontrado:
                if texto[contador] == "Historical Data":
                    encontrado = True
                contador += 1
            # esta segunda parte lo selecciona/pulsa
            historical_data_button = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.XPATH, f"//*[@id='pairSublinksLevel2']/li[{contador}]/a")))
            historical_data_button.click()

    except TimeoutException:
        print("No se ha podido acceder al historical data e 10 seg")

    # Accedemos a la seleccion de fechas:
    try:
        date_selection_button = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.ID, "widgetFieldDateRange")))
        date_selection_button.click()

    except TimeoutException:
        print("No se ha podido acceder al boton de 'seleccionar fechas")

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
        print("La fecha final que quiere seleccionar no está disponible")

    try:
        primer_elemento = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.XPATH, '//*[@id="leftColumn"]/div[9]/table[1]/tbody/tr[1]/td[1]')))
    finally:
        tabla = driver.find_element_by_xpath('//*[@id="curr_table"]/tbody').text.split(sep='\n')

        with open(lista_nombre_csv[numero_enlace], 'w', newline='\n') as csvfile:
            csvtool = csv.writer(csvfile, delimiter=';')
            for elem in tabla:
                elem = elem.split()
                """ elem[0] = mes, elem[1] = dia(segido de una coma), elem[2] = año,
                 elem[3] = precio inicial, elem[-2] = volumen, elem[-1] = varición diaria"""
                csvtool.writerow([elem[0] + " " + elem[1] + " " + elem[2], elem[3], elem[-2], elem[-1]])

    time.sleep(5)
driver.close()

'''NOTA: HAY QUE TRATAR EL ANUNCIO QUE SALE A VECES, QUE ES NARANJA NEGRO Y BLANCO (SIGN UP), 
pero este solo sale si mueves el ratón en la pgina de crom abierta'''

final = time.time()
print(final-inicio)
