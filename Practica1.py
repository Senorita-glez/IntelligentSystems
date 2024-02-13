import csv
from selenium import webdriver

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os


Datos=['ID','Nombre del Modelo','Descripcion','URL','Formatos','Indicador de Texturas',
'Indicador de Materiales','Tamaño','Numero de Poligonos','Numero de Vertices'
,'Rigged','Animado','Licencia','Calidad','Software Compatible','Categorias','Tags']
t=3
def Scraper3D():
    driver = webdriver.Firefox()
    driver.get('https://open3dmodel.com/')
    try:
        WebDriverWait(driver, t).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'labels-single')))
        link =  driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[6]/a',)
        link.click()
        i=0
        with open("Modelos_3D.csv", mode="w", newline='') as archivo: 
            escritura = csv.writer(archivo)
            escritura.writerow(Datos)
        while i<2:
            WebDriverWait(driver, t).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'labels-single')))
            modelos = driver.find_elements(By.CLASS_NAME, 'itemtitle')
            with open("Modelos_3D.csv", mode="a", newline='') as archivo: 
                escritura = csv.writer(archivo)
                for modelo in modelos:
                    ID_modelo = modelo.find_element(By.TAG_NAME, 'a').text.strip()
                    escritura.writerow([ID_modelo])

            pag_siguiente =WebDriverWait(driver, t).until(EC.element_to_be_clickable((By.XPATH, '//a[@class="nextpostslink"]')))
            pag_siguiente.click()  
            WebDriverWait(driver, t).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'labels-single')))
            i+=1

                 
    except Exception as e:
        print("Error durante el scraping:",e)
        if os.path.exists("Modelos_3D.csv"):
            os.remove("Modelos_3D.csv")
    finally:
        driver.quit()
        print("Scraping Completo")
Scraper3D()



