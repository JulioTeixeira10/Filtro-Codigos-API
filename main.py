import requests
from configparser import ConfigParser
import xml.etree.ElementTree as ET

dirDados = "C:\\Bancamais\\Fastcommerce\\DadosLoja"

#Administração do arquivo .cfg
config_object = ConfigParser()
config_object.read(f"{dirDados}\\StoreData.cfg")
STOREINFO = config_object["STOREINFO"]

StoreName = STOREINFO["StoreName"]
StoreID = STOREINFO["StoreID"]
Username = STOREINFO["Username"]
password = STOREINFO["password"]

#Request
url = "https://www.rumo.com.br/sistema/adm/APILogon.asp"
payload= (f"""StoreName={StoreName}&StoreID={StoreID}&Username={Username}&
          method=ReportView&password={password}&ObjectID=425&Fields=IDProduto""")
headers = {'Content-Type': 'application/x-www-form-urlencoded'}

response = requests.request("POST", url, headers=headers, data=payload)
xml_string = response.text

#Arquivo XML
with open("C:\\Users\\Usefr\\Desktop\\Integração[Bmais - FC ]\\FiltroIDProduto\\fileresponse.xml", "w+") as fr:
    fr = fr.write(xml_string)

#Extrai os IDs
root = ET.fromstring(response.text)
id_produtos = [record.find('Field[@Name="IDProduto"]').attrib['Value'] for record in root.findall('Record')]

#Lê e armazena os IDs do B+ em uma lista
f = open("C:\\Users\\Usefr\\Desktop\\Integração[Bmais - FC ]\\FiltroIDProduto\\file1.txt")
file = f.readlines()
IDsB = []
for id in file:
    IDsB.append(id.strip())

#Olha se existem diferenças na quantidade de IDs entre os arquivos
if len(IDsB) != len(id_produtos):
    if len(IDsB) > len(id_produtos):
        print(f"Existem mais IDs no Bancamais: {len(IDsB)}, que no Fastcommerce: {len(id_produtos)}.")
    else:
        print(f"Existem mais IDs no Fastcommerce: {len(id_produtos)}, que no Bancamais: {len(IDsB)}.")

#Olha se existem IDs incorretos
CheckID = True
for id in id_produtos:
        if id not in IDsB:
            print(f"""O ID interno: {id} do Fastcommerce não existe no Bancamais, adicione esse id ao produto correspondente no Bancamais.""")
            CheckID = False

for id in IDsB:
    if id not in id_produtos:
        print(f"""O ID interno: {id} do Bancamais não existe no Fastcommerce, corrija esse ID o antes possível para evitar que o 'ERRO18' aconteça ao utilizar alguma ferremante de integração.""")
        CheckID = False

#Mostra ao usuario o resultado geral
if CheckID == True:
    print("Tudo certo.")
elif CheckID == False:
    print("Houve divergencias.")