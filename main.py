import defectdojo

# 1️⃣ Tenta criar o produto primeiro
response_product = defectdojo.create_product(
    defectdojo.PRODUCT_NAME,
    defectdojo.DESCRIPTION,
    defectdojo.ORIGIN,
    defectdojo.URL_BASE
)

# 2️⃣ Se o código for 201 (produto criado) ou 400 (produto já existe), continua
if response_product.status_code == 201:
    print("✅ Produto criado com sucesso.")
    product_id = response_product.json()['id']

elif response_product.status_code == 400:
    print("🔍 Produto já existe. Tentando recuperar ID...")

    try:
        product_id = defectdojo.get_product(defectdojo.PRODUCT_NAME, defectdojo.URL_BASE)
        print(f"✅ ID do Produto encontrado: {product_id}")
    except ValueError:
        print("❌ Produto não encontrado, tentando criá-lo novamente...")

        # 3️⃣ Se a busca falhar, cria novamente
        response_product = defectdojo.create_product(
            defectdojo.PRODUCT_NAME,
            defectdojo.DESCRIPTION,
            defectdojo.ORIGIN,
            defectdojo.URL_BASE
        )

        if response_product.status_code == 201:
            product_id = response_product.json()['id']
            print(f"✅ Produto criado com sucesso! ID: {product_id}")
        else:
            print(f"❌ Erro ao criar o produto: {response_product.content}")
            exit(1)

else:
    print(f"❌ Falha ao criar produto: {response_product.content}")
    exit(1)

# 4️⃣ Busca o engagement existente ou cria um novo
response_engagement = defectdojo.get_engagement(product_id, defectdojo.URL_BASE)

if len(response_engagement.json().get('results', [])) == 0:
    print("📌 Nenhum engagement encontrado. Criando um novo...")
    defectdojo.create_engagement(
        product_id,
        defectdojo.USERNAME,
        defectdojo.SOURCE_URL,
        defectdojo.URL_BASE,
        defectdojo.TOOL
    )
else:
    print("✅ Engagement já existente encontrado.")

# 5️⃣ Obtém o ID do engagement
try:
    engagement_id = defectdojo.get_engagement_code_id(product_id, defectdojo.TOOL, defectdojo.URL_BASE)
    print(f"✅ ID do Engagement: {engagement_id}")
except ValueError as e:
    print(f"❌ Erro ao buscar o engagement: {e}")
    exit(1)

# 6️⃣ Enviar os findings (vulnerabilidades) para o engagement
print("🚀 Enviando findings (vulnerabilidades) para o Defect Dojo...")
defectdojo.create_finding(engagement_id, defectdojo.FILE, defectdojo.URL_BASE)
print("✅ Findings enviados com sucesso!")
