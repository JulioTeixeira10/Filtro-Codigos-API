import requests
from configparser import ConfigParser
import xml.etree.ElementTree as ET

dirDados = "C:\\Bancamais\\Fastcommerce\\DadosLoja"

with open("C:\\Bancamais\\Fastcommerce\\ProgramasExtras\\Conferência\\FiltroIDProduto\\Resultado.txt", "w+") as o:
        pass

def resultadoa(output):
    with open("C:\\Bancamais\\Fastcommerce\\ProgramasExtras\\Conferência\\FiltroIDProduto\\Resultado.txt", "a") as o:
        o.write(output)
        o.write("\n\n")
        o.close()

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

try:
    response = requests.request("POST", url, headers=headers, data=payload)
    xml_string = response.text
except Exception as e:
    with open("C:\\Bancamais\\Fastcommerce\\ProgramasExtras\\Conferência\\FiltroIDProduto\\Erro.txt", "w+") as e:
        e.write("Houve um erro de conexão.")
        e.close()
    exit()

#Extrai os IDs
root = ET.fromstring(response.text)
id_produtos = [record.find('Field[@Name="IDProduto"]').attrib['Value'] for record in root.findall('Record')]

#Lê e armazena os IDs do B+ em uma lista
f = open("C:\\Bancamais\\Fastcommerce\\ProgramasExtras\\Conferência\\FiltroIDProduto\\syncIDs.txt")
file = f.readlines()
IDsB = []
for id in file:
    IDsB.append(id.strip())
f.close()

#Olha se existem diferenças na quantidade de IDs entre os arquivos
if len(IDsB) != len(id_produtos):
    if len(IDsB) > len(id_produtos):
        resultadoa(f"Existem mais IDs no Bancamais: {len(IDsB)}, que no Fastcommerce: {len(id_produtos)}.")
    else:
        resultadoa(f"Existem mais IDs no Fastcommerce: {len(id_produtos)}, que no Bancamais: {len(IDsB)}.")

#Olha se existem IDs incorretos
CheckID = True
CriticalCheckID = False

for id in id_produtos:
    if id not in IDsB:
        resultadoa(f"O ID interno: {id} do Fastcommerce não existe no Bancamais.")
        CheckID = False

for id in IDsB:
    if id not in id_produtos:
        resultadoa(f"O ID interno: {id} do Bancamais não existe no Fastcommerce.")
        CheckID = False
        CriticalCheckID = True

#Mostra ao usuario o resultado geral
if CheckID == True and CriticalCheckID == False:
    resultadoa("CheckID = True // Tudo Certo")
elif CheckID == False:
    if CheckID == False and CriticalCheckID == True:
        resultadoa("CheckID = False and CriticalCheckID = True // Houve divergencias críticas.")
    else:
        resultadoa("CheckID = False // Houve divergencias.")

if (response.text.find("<ErrCod>")) > 0:
    with open("C:\\Bancamais\\Fastcommerce\\ProgramasExtras\\Conferência\\FiltroIDProduto\\Erro.txt", "w+") as e:
        e.write("Houve um erro ao checar os IDs.")
        e.write("\n")
        e.write(response.text)
        e.close()
