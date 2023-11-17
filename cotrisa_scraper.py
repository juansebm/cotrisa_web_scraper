import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import os

# Ruta al geckodriver
geckodriver_path = 'geckodriver.exe'  # Descargar desde https://github.com/mozilla/geckodriver/releases
service = webdriver.firefox.service.Service(geckodriver_path)
driver = webdriver.Firefox(service=service)
driver.get('https://www.cotrisa.cl/marketplace/precios/')

wait = WebDriverWait(driver, 10)
data = []

def click_dropdown_option(dropdown_id, option_text):
    """
    Args:
        dropdown_id (str): El ID del elemento de menú desplegable.
        option_text (str): El texto de la opción que se desea seleccionar dentro del menú desplegable.
    """
    dropdown = wait.until(EC.element_to_be_clickable((By.ID, dropdown_id)))
    dropdown.click()
    time.sleep(2)  # Espera para que el menú desplegable se abra completamente
    option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//select[@id='{dropdown_id}']/option[text()='{option_text}']")))
    option.click()
    time.sleep(2)  # Espera después de seleccionar una opción

def get_options(dropdown_id):
    """
    Args:
        dropdown_id (str): El ID del elemento de menú desplegable.

    Returns:
        list: Una lista de cadenas de texto que representa las opciones disponibles en el menú desplegable.
    """
    dropdown = wait.until(EC.element_to_be_clickable((By.ID, dropdown_id)))
    dropdown.click()
    time.sleep(2)  # Espera para que el menú desplegable se abra completamente
    options = dropdown.find_elements(By.TAG_NAME, 'option')
    return [option.text for option in options if option.get_attribute('value')]

try:
    grano_options = ["Trigo", "Maíz", "Arroz"]  # Se puede editar para extraer granos en específico
    for grano in grano_options:
        click_dropdown_option('granoSelect', grano)

        cosecha_options = get_options('cosechaSelect')
        for cosecha in cosecha_options:
            click_dropdown_option('cosechaSelect', cosecha)

            semana_options = get_options('semanaSelect')
            for semana in semana_options:
                click_dropdown_option('semanaSelect', semana)

                time.sleep(2)  # Espera para que la tabla se cargue completamente
                tabla = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'custom-table')))
                filas = tabla.find_elements(By.TAG_NAME, 'tr')
                for fila in filas[1:]:
                    columnas = fila.find_elements(By.TAG_NAME, 'td')
                    if len(columnas) == 4:
                        data.append([grano, cosecha, semana] + [c.text for c in columnas])

except Exception as e:
    print("Ocurrió un error durante la extracción de datos:", e)

finally:
    driver.quit()

# Convertir los datos a DataFrame y guardarlos en un archivo CSV
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
filename = f'precios_granos_{timestamp}.csv'
df = pd.DataFrame(data, columns=['Grano', 'Cosecha', 'Semana', 'Agroindustrial', 'Localidad', 'Precio', 'Observaciones'])
df.to_csv(filename, index=False)
