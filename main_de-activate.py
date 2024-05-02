##################################################
## Script para download de Oracle Integration Cloud (OIC) Integrations
##################################################
## GNU GENERAL PUBLIC LICENSE Version 2
##################################################
## Author: Lucas Oleiro
## Copyright: 2024
## Credits: Lucas Oleiro
## License: GNU
## Version: 1.0
## Email: oleiro-oic@gmail.com
## Status: production
##################################################

import configparser
import logging
import requests
from tqdm import tqdm

# Inicializa a variável global para acumular os itens
all_items = []

# Carregar configurações
config = configparser.ConfigParser()
config.read('config.ini')

def fetch_integrations(offset=0,_status="ACTIVATED"):
    global all_items  # Indica que a função irá utilizar a variável global

    base_url = config['DEFAULT']['base_url']
    params = {
        "onlyData": "true",
        "limit": 1000,
        "q": "{ status : '" + _status + "'}",
        "offset": offset
    }
    headers = {
        "Authorization": config['DEFAULT']['authorization']
    }

    response = requests.get(base_url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])
        
        # Adiciona os IDs dos itens à lista global
        all_items.extend([item['id'] for item in items if item.get('pattern') == 'Scheduled'])
        
        # Verifica se ainda há mais itens para buscar
        if data.get("hasMore", False):
            fetch_integrations(offset + len(items))
    else:
        print(f"Erro ao buscar integrações: {response.status_code} - {response.reason}")

# Configuração básica do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def update_integrations(ids,_status="ACTIVATED", stopScheduleForDeactivation="false"):
    base_url = config['DEFAULT']['base_url']
    headers = {
        "Authorization": config['DEFAULT']['authorization'],
        "X-HTTP-Method-Override": "PATCH",
        "Content-Type": "application/json"
    }

    for id in tqdm(ids, desc="Atualizando status de integrações"):
        url = f"{base_url}/{id}"
        
        _data = {
            "status": _status
            #,"stopScheduleForDeactivation": "true"
        }
        
        response = requests.post(url, headers=headers, json=_data)
        
        if response.status_code == 200 or response.status_code == 412:
            logging.info(id)
        else:
            print(f"Erro: {response.status_code} - {response.reason}")
            print(url)
            print(headers)
            print(_data)
            print(id)
            print(response.text)
            exit()

def start_integrations_schedule(ids,_status="ACTIVATED"):
    base_url = config['DEFAULT']['base_url']
    headers = {
        "Authorization": config['DEFAULT']['authorization'],
        "Accept": "application/json"
    }

    for id in tqdm(ids, desc="Iniciando schedule de integrações"):
        url = f"{base_url}/{id}/schedule/start"
        
        response = requests.post(url, headers=headers)
        
        if response.status_code == 200 or response.status_code == 412:
            logging.info(id)
        else:
            print(f"Erro: {response.status_code} - {response.reason}")
            print(url)
            print(headers)
            print(id)
            print(response.text)
            exit()

def read_file(file_path):
    global all_items
    
    with open(file_path, 'r') as file:
        # Lê todas as linhas do arquivo
        all_items.extend([line.strip() for line in file.readlines()])

# Chama a função inicialmente com offset 0
#fetch_integrations()

read_file("integracoes para ativar TEST2.txt")

# [print(item) for item in all_items]

# Atualiza o status desejado para as integrações
#update_integrations(all_items,"ACTIVATED","false")

start_integrations_schedule(all_items)