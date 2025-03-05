import requests
import json
from datetime import datetime, timedelta
import argparse
import os


parser = argparse.ArgumentParser(
        usage='%(prog)s --url_base URL_BASE --username USERNAME --source_url SOURCE_URL --tool TOOL --file FILE --scan_type SCAN_TYPE --product_name PRODUCT_NAME --description DESCRIPTION --origin ORIGIN --json JSON',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
parser.add_argument("-url", "--url_base",type=str, required=True)
parser.add_argument("-u", "--username",type=str, required=True)
parser.add_argument("-surl", "--source_url",type=str, required=True)
parser.add_argument("-t", "--tool",type=str, required=True)
parser.add_argument("-f", "--file",type=str, required=True)
parser.add_argument("-s", "--scan_type",type=str, required=False)
parser.add_argument("-p", "--product_name",type=str, required=True)
parser.add_argument("-d", "--description",type=str, required=True)
parser.add_argument("-o", "--origin",type=str, required=True)
parser.add_argument("-j", "--json",type=str, required=True)


args = parser.parse_args()

URL_BASE = args.url_base
USERNAME = args.username
SOURCE_URL = args.source_url
TOOL = args.tool
FILE = args.file
SCAN_TYPE = args.scan_type
PRODUCT_NAME = args.product_name
DESCRIPTION = args.description
ORIGIN = args.origin
JSON = args.json



def auth_token(JSON):
    """
    Receive token from Defect Dojo

    """

    json_obj = {}
    json_obj['Authorization'] = "Token "+JSON

    return json_obj
    


def create_product(PRODUCT_NAME, DESCRIPTION, ORIGIN, URL_BASE):
    """"
    Create new project in Defect Dojo

    :param PRODUCT_NAME: Product's name
    :param description: Product's description
    :param origin: Product's origin
    :param URL_BASE: Defect Dojo's url

    """

    headers =  auth_token(JSON)

    url = URL_BASE+"products/"

    data = {
    "name":PRODUCT_NAME,
    "description": DESCRIPTION,
    "prod_type":1,
    "sla_configuration":1,
    "origin": ORIGIN
    }

    return requests.post(url, headers=headers, data=data)


def get_product(PRODUCT_NAME,URL_BASE):
    """"
    Get project in Defect Dojo

    :param PRODUCT_NAME: Product's name
    :param URL_BASE: Defect Dojo's url

    """

    headers =  auth_token(JSON)

    url = URL_BASE+f"products/?name={PRODUCT_NAME}"

    response = requests.get(url, headers=headers)

    id = None

    if len(response.json()['results']) != 0:
        for i in range(len(response.json()['results'])):
            if response.json()['results'][i]['name'] == PRODUCT_NAME:
                id=int(response.json()['results'][i]['id'])

    if id is None:
        raise ValueError(f"Produto '{PRODUCT_NAME}' não encontrado no DefectDojo.")
            
    return id



def get_user(USERNAME,URL_BASE):
    """"
    Get user from Defect Dojo

    :param USERNAME: Product's name
    :param URL_BASE: Defect Dojo's url

    """

    headers =  auth_token(JSON)

    url = URL_BASE+f"users/?username={USERNAME}"

    response = requests.get(url, headers=headers)

    return int(response.json()['results'][0]['id'])


def get_engagement(product_id,URL_BASE):
    """"
    Get engagement in Defect Dojo

    :param product_id: Product's id
    :param URL_BASE: Defect Dojo's url

    """

    headers =  auth_token(JSON)

    url = URL_BASE+f"engagements/?product={product_id}"

    return requests.get(url, headers=headers)


def create_engagement(product_id,USERNAME,SOURCE_URL,URL_BASE,TOOL):
    """"
    Create new engagement in Defect Dojo (such as Horusec)

    :param product_id: Product's id
    :param USERNAME: Username
    :param SOURCE_URL: URL from source (such as github repository)
    :param URL_BASE: Defect Dojo's url
    :param TOOL: Tool name for the engagement


    """

    headers =  auth_token(JSON)

    user=get_user(USERNAME,URL_BASE)

    url = URL_BASE+'engagements/'


    data = {
            "name": TOOL,
            "description": "teste",
            "target_start": datetime.today().strftime('%Y-%m-%d'),
            "target_end": datetime.strftime(datetime.now() + timedelta(7), '%Y-%m-%d'),
            "status": "In Progress",
            "engagement_type": "CI/CD",
            "source_code_management_uri": SOURCE_URL,
            "deduplication_on_engagement": True,
            "lead": user,
            "product": product_id
        }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 201:
        print('Engagement was created successfully')

    else:
        print(f'Failed to create project: {response.content}')


def get_engagement_code_id(product_id,TOOL,URL_BASE):
    """"
    Get engagement id

    :param product_id: Product's id
    :param TOOL: Tool (such as Horusec)
    :param URL_BASE: Defect Dojo's url

    """

    headers =  auth_token(JSON)

    url = URL_BASE+f'engagements/?product={product_id}'

    response = requests.get(url, headers=headers)
    if len(response.json()['results']) != 0:
        for i in range(len(response.json()['results'])):
            if response.json()['results'][i]['name'] == TOOL:
                id=int(response.json()['results'][i]['id'])
    return id


def get_scan_type(FILE):
    """"
    Get scan extension type 

    :param FILE: File (such as Sarif file)

    """

    if FILE.split(".")[1] == 'sarif':
        return'SARIF'


def create_finding(engagement_id,FILE,URL_BASE):
    """"
    Create finding (vulnerabilities) to populate Defect Dojo

    :param engagement_id: Engagement's id
    :param FILE: File (such as Sarif file)
    :param URL_BASE: Defect Dojo's url

    """

    headers =  auth_token(JSON)

    url = URL_BASE+'import-scan/'

    scan_type = get_scan_type(FILE)

    data = {
    'active': True,
    'verified': True,
    'scan_type': scan_type,
    'minimum_severity': 'Low',
    'engagement': engagement_id,
    'skip_duplicates': False
    }

    FILE = os.path.join(os.getcwd(), args.file)
        
    print(f"📂 Diretório atual: {os.getcwd()}")
    print(f"🔍 Caminho esperado do arquivo: {FILE}")

    # Lista todos os arquivos no diretório atual para garantir que o arquivo está lá
    print("📄 Arquivos no diretório atual:")
    os.system("ls -lah")

    if not os.path.exists(FILE):
        print(f"❌ Erro: O arquivo '{FILE}' não foi encontrado!")
        exit(1)

    print(f"✅ Arquivo encontrado: {FILE}")

    files = {
        'file': open(FILE, 'rb')
    }

    response = requests.post(url, headers=headers, data=data, files=files)

    if response.status_code == 201:
        print('Scan results imported successfully')
    else:
        print(f'Failed to import scan results: {response.content}')
