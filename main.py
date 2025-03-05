import defectdojo

# cria projeto e retorna codigo para saber se ja existe ou nao projeto com o nome esperado
response_product = defectdojo.create_product(defectdojo.PRODUCT_NAME, defectdojo.DESCRIPTION, defectdojo.ORIGIN, defectdojo.URL_BASE)

# se codigo for 201, ira criar um novo engagement code, caso contrario, ira adicionar so as findigs (vulnerabilidades)
if response_product.status_code == 201 or response_product.status_code == 400:

    if response_product.status_code == 201:
        product_id = response_product.json()['id']

    elif response_product.status_code == 400:
        product_id = defectdojo.get_product(defectdojo.PRODUCT_NAME,defectdojo.URL_BASE)

    response_engagement = defectdojo.get_engagement(product_id,defectdojo.URL_BASE)
    
    if len(response_engagement.json()['results']) == 0:
        
        defectdojo.create_engagement(product_id,defectdojo.USERNAME,defectdojo.SOURCE_URL,defectdojo.URL_BASE,defectdojo.TOOL)

    engagement_id = defectdojo.get_engagement_code_id(product_id,defectdojo.TOOL,defectdojo.URL_BASE)

    defectdojo.create_finding(engagement_id,defectdojo.FILE,defectdojo.URL_BASE)

else:

    print(f'Failed to create project: {response_product.content}')