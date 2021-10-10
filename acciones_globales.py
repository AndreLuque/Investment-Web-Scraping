import csv
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

driver = webdriver.Chrome(r"C:\Users\Usuario\Desktop\gonzalo jr\CDIA\segundo de carrera\primer "
                          r"cuatri\Progra\chromedriver.exe")

driver.get("https://www.investing.com/funds/amundi-msci-wrld-ae-c")
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
    historical_data_button = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.XPATH, "//*[@id='pairSublinksLevel2']/li[3]/a")))
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

""" 
Aunque el número de columnas sea 6, a nosotros solo 
nos interesan la columna 1, la 2 y la 6, que corresponden a la fecha,
a el precio  al cambio en %, respectivamente.
"""
cabeceras = driver.find_elements_by_xpath('//body/div[5]//thead/tr/th')
n_columnas = len(cabeceras)

DIAS_DE_2020 = 365
DIAS_DE_FINDE_SEMANA = 118
DIAS_SIN_FINDE_SEMANA = DIAS_DE_2020 - DIAS_DE_FINDE_SEMANA

lista_columnas = []

for fila in range(1, DIAS_SIN_FINDE_SEMANA+1):
    lista_columnas += [(driver.find_element_by_xpath(f'//table/tbody/tr[{fila}]/td[1]').text,
                        driver.find_element_by_xpath(f'//table/tbody/tr[{fila}]/td[2]').text,
                        driver.find_element_by_xpath(f'//table/tbody/tr[{fila}]/td[6]').text)]

with open('amundi-msci-wrld-ae-c.csv', 'w', newline='\n') as csvfile:
    csvtool = csv.writer(csvfile, delimiter=';')
    for elem in lista_columnas:
        csvtool.writerow(elem)

time.sleep(10)
driver.close()
