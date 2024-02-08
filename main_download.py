import configparser
import requests
import os
import zipfile
import sys
from tqdm import tqdm

# Inicializa a variável global para acumular os itens
all_items = []

# Carregar configurações
config = configparser.ConfigParser()
config.read('config.ini')

def fetch_integrations(offset=0):
    global all_items  # Indica que a função irá utilizar a variável global

    base_url = config['DEFAULT']['base_url']
    params = {
        "onlyData": "true",
        "limit": 1000,
        "q": "{status : 'ACTIVATED'}",
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
        all_items.extend([item['id'] for item in items])
        
        # Verifica se ainda há mais itens para buscar
        if data.get("hasMore", False):
            fetch_integrations(offset + len(items))
    else:
        print(f"Erro ao buscar integrações: {response.status_code}")

def download_integration_details(items=all_items, directory = "../files"):
    os.makedirs(directory, exist_ok=True)

    headers = {
        "Authorization": config['DEFAULT']['authorization'],
        "Accept": "application/octet-stream"
    }
    
    for item_id in tqdm(items, desc="Downloading integration archives"):
        download_url = f"{config['DEFAULT']['authorization']}/{item_id}/archive"
        response = requests.get(download_url, headers=headers)
        
        if response.status_code == 200:
            file_path = os.path.join(directory, f"{item_id}.iar").replace("|","-")  # .iar extension for integration archive files
            with open(file_path, 'wb') as file:
                file.write(response.content)
        else:
            print(f"Erro ao baixar o arquivo de arquivamento da integração {item_id}: {response.status_code}")

def unzip_integration_archives(directory="../files", log_file="unzip.log"):
    target_directory = os.path.join(directory, "open")
    
    # Abre o arquivo de log para escrita
    original_stdout = sys.stdout  # Salva a referência original de sys.stdout para restaurá-la depois
    with open(log_file, 'w') as f:
        sys.stdout = f  # Redireciona sys.stdout para o arquivo de log
        
        # Certifica-se de que o diretório 'open' exista
        os.makedirs(target_directory, exist_ok=True)
        
        # Lista todos os arquivos .IAR no diretório especificado
        iar_files = [f for f in os.listdir(directory) if f.endswith('.iar')]
        
        for iar_file in tqdm(iar_files, desc="Unzipping archives", file=sys.stdout):
            item_id = iar_file[:-4]  # Remove a extensão .iar para obter o item_id
            item_target_directory = os.path.join(target_directory, item_id)
            
            # Cria um diretório para o item_id se não existir
            os.makedirs(item_target_directory, exist_ok=True)
            
            # Caminho completo para o arquivo .IAR
            iar_file_path = os.path.join(directory, iar_file)
            
            try:
                # Descompacta o arquivo .IAR
                with zipfile.ZipFile(iar_file_path, 'r') as zip_ref:
                    zip_ref.extractall(item_target_directory)
                print(f"Arquivo {iar_file} descompactado em {item_target_directory}")
            except FileNotFoundError:
                print(f"Arquivo {iar_file_path} não encontrado. Ignorando...")
            except zipfile.BadZipFile:
                print(f"Arquivo {iar_file_path} não é um arquivo ZIP válido ou está corrompido. Ignorando...")
            except Exception as e:
                print(f"Erro desconhecido ao descompactar {iar_file_path}: {e}. Ignorando...")
    
    sys.stdout = original_stdout  # Restaura sys.stdout para a referência original

# Chama a função inicialmente com offset 0
#fetch_integrations(0)

# Após acumular todos os IDs, baixa os detalhes de cada integração
#download_integration_details()

# Chama a função para descompactar os arquivos .IAR
unzip_integration_archives()
