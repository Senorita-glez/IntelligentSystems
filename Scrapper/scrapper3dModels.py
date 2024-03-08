import random, requests, time, csv, re, os
from lxml import html
from urllib.parse import urljoin, urlparse

if not os.path.exists('data'):
    os.makedirs('data')

def updateSession(act):
    act = requests.Session()
    return act

def updateUserAgent():
    user_agent_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363',
    ]
    headers={"User-Agent": user_agent_list[random.randint(0, len(user_agent_list)-1)]}
    return headers

def propiedades(text, patrones):
    dicc = {}
    for key, patron in patrones.items():
        match = re.search(patron, text)
        if match:
            dicc[key] = match.group(1)
    return dicc

def get_important(tree, xpath_code):
    dicc = {}
    propierties = tree.xpath(xpath_code)
    for element in propierties:
        text = element.text_content()
        patrones = {
            'file_size': r'File Size: (.+)',
            'id': r'Model ID: ([#]\d+)',
            'polygons': r'Polygons: (\d+|N/A)',
            'vertex': r'Vertices: (\d+|N/A)',
            'is_rigged': r'Rigged: (\w{2,3})',
            'is_animated': r'Animated: (\w{2,3})',
            'license': r'License: (.+)',
            'quality': r'Quality: (.+)',
            'aviable_formats': r'Formats: ((\.\w+)(,\s*\.\w+)*|(\.))',
        }
        dicc.update(propiedades(text, patrones))
    return dicc

def get_software(tree, xpath_code):
    dicc = {}
    suma = 0
    properties = tree.xpath(xpath_code)
    patrones = {
        'textures': r'Textures & Materials:((\.\w+)(,\s*\.\w+)*)',
        'software': r'Software for Import:(.*?)\.\.\.',
        'materials': r'\.\w+ for (.+?) Categories',
    }
    for element in properties:
        text = element.text_content()
        texto = " ".join(text.strip().split())  
        dicc.update(propiedades(texto, patrones)) 

    suma = len(dicc['textures'].split(', ')) + len(dicc['materials'].split(', '))  
    newdicc = {'textures_and_materials': suma, 'software':dicc['software'] }
    return newdicc

def get_name(tree, xpathCode):
    dicc={}
    title = tree.xpath(xpathCode)

    Name= title[0].text_content()
    '''Name'''
    patronName = r'(.+) 3D Model'
    searchName = re.search(patronName,Name)
    if searchName:
        dicc['name'] = searchName.group(1)
    return dicc

def get_dscp(tree, xpath_code):
    dicc = {}
    Dscp = tree.xpath(xpath_code)
    if len(Dscp)>0:
        dicc['description']=Dscp[0].text_content()
    else:
        dicc['description']='Not Found'
    return dicc

def cat_tag(respuesta):
    dicc={}
    redirection_root_lxml=html.fromstring(respuesta.text)
    categories=redirection_root_lxml.xpath("//div[@class='ads336']//span[contains(text(),'Categories:')]/parent::p/parent::div/a[not(contains(@rel,'tag'))]/text()")
    tags=redirection_root_lxml.xpath("//div[@class='ads336']//span[contains(text(),'Tags: ')]/parent::p/following-sibling::a/text()")
    dicc={'category':'|'.join(categories),'tags':'|'.join(tags)}
    return dicc

class Page:
    def __init__(self,headers):
        self.url=None
        self.next_page_url=None
        self.parsed_response=None
        self.headers=headers
        self.sess = requests.Session()

    def setUrl(self,url):
        self.url=url

    def getParsedResponse(self):
        response=self.sess.get(self.url,headers=self.headers)
        self.parsed_response=html.fromstring(response.text)

    def getItemsLinks(self):
        self.getParsedResponse()
        items=self.parsed_response.xpath("//div[contains(@id,'site-')]//div[@class='itemtitle']/a/@href")
        return items
    
    def setNextPageUrl(self):
        self.getParsedResponse()
        self.next_page_url=self.parsed_response.xpath("//a[@class='nextpostslink' and @rel='next' and @aria-label='Next Page']/@href")[0]
        
    def getMaxPags(self):
        self.getParsedResponse()
        max_pags=self.parsed_response.xpath("//div[@class='nav-links']/a[last()-1]/text()")[0]
        return max_pags
    
def downloadModel(urlModel, session):
    response = session.get(urlModel)
    tree = html.fromstring(response.content)

    enlace_pag_download = tree.xpath('/html/body/div[3]/article/div[3]/div[1]/div[3]/div[1]/div[2]/a/@href')

    if enlace_pag_download:
        enlace_pag_download = enlace_pag_download[0]
        response_download_page = requests.get(enlace_pag_download)
        tree_download_page = html.fromstring(response_download_page.content)
        enlace_descarga = tree_download_page.xpath('/html/body/div[3]/div[7]/div/div/div[6]/a/@href')
        
        if enlace_descarga:
            enlace_descarga = enlace_descarga[0]

            url_base = 'https://open3dmodel.com'
            url_completa = urljoin(url_base, enlace_descarga)
            print(f"URL completa: {url_completa}")
            time.sleep(random.uniform(1,3))
            response = session.get(url_completa)

            if response.status_code == 200:
                print('response url', response.url)
                formulario_xpath = '/html/body/div[1]/div[2]/form'
                root = html.fromstring(response.text)
                formulario = root.xpath(formulario_xpath)
                if formulario != []:
                    params = {}
                    for input_element in formulario[0].xpath('.//input'):
                        nombre = input_element.get('name')
                        valor = input_element.get('value')
                        params[nombre] = valor
                        print(f"{nombre}: {valor}")
                        
                    response = session.get(response.url, params=params)
                    time.sleep(random.uniform(0,1))
                content_disposition = response.headers.get('Content-Disposition')
                
                if content_disposition and 'filename' in content_disposition:
                    filename = content_disposition.split('filename=')[1]
                    filename = filename.strip('"')
                    print('encabezado Content-Dispositiono', filename)
                else:
                    parsed_url = urlparse(url)
                    filename = parsed_url.path.split('/')[-1]
                    print('Si no hay encabezado', filename)

                filename = 'data/' + filename
                print(filename)
                with open(filename, 'wb') as file:
                    file.write(response.content)
                print(f'Archivo descargado correctamente como {filename}')
                return filename
            else:
                print(f'Error al descargar el archivo. Código de estado: {response.status_code}')
                print(response.text)
                return None
        else:
            print("No se pudo encontrar el enlace de descarga en la página de descarga.")
            return None
    else:
        print("No se pudo encontrar el enlace a la página de descarga.")
        return None

Datos=['path',
       'file_size', 'id', 'name',
       'description','uri','aviable_formats',
       'textures_and_materials','polygons',
       'vertex','is_rigged', 'is_animated','license',
       'quality','software','category','tags'
       ]

initial_url='https://open3dmodel.com/3d-models/' #page1
headers=updateUserAgent()
page=Page(headers)
i,m=0,0
max_pags=100
with open("data/Modelos_3D.csv", mode="w", newline='',encoding='utf-8') as archivo: 
    escritura = csv.writer(archivo)
    escritura.writerow(Datos)
    while i<max_pags:
        print(f"Numero de pagina: {i+1}")
        if i==0:
            url=initial_url
        page.setUrl(url)
        page.setNextPageUrl()
        models_links=page.getItemsLinks()
        print('Max: ',len(models_links))
        for link in models_links:
                ori = page.sess
                response = ori.get(link,headers=headers)
                path = downloadModel(link, ori)
                if path != None:
                    pathdicc = {'path': str(path)}
                else:
                    pathdicc = {'path': 'not found'}
                tree = html.fromstring(response.content)
                properties = get_important(tree, '/html/body/div[3]/div/div[5]/ul/li')
                software=get_software(tree,'/html/body/div[3]/article/div[3]/div[1]/div[3]/div[2]/div[5]')
                description=get_dscp(tree,'/html/body/div[3]/article/div[3]/div[1]/div[3]/div[1]/div[1]/p')
                name=get_name(tree,'/html/body/div[3]/article/div[3]/div[1]/div[3]/h1')   
                link={'uri': response.url}
                propleft=cat_tag(response)
                Propiedades= pathdicc|properties|software|description|name|link|propleft #Only works in python versions > 3.9
                Propordenadas = {key: Propiedades[key] for key in Datos} 
                m+=1
                print(f'Modelo extraido no. {m}')
                escritura.writerow(list(Propordenadas.values()))
        url=page.next_page_url
        time.sleep(random.uniform(1,3))
        i=i+1
