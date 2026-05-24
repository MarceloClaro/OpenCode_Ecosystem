from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore

# Define a classe personalizada que herda da Vanna
class MyVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)

# Instancia com o modelo Ollama desejado
vn = MyVanna(config={'model': 'llama3.1:8b'})

# Conecta ao banco de dados SQLite
vn.connect_to_sqlite('vendas_normalizado.db')

# Carrega todos os DDLs das tabelas existentes e treina com eles
df_ddl = vn.run_sql("SELECT type, sql FROM sqlite_master WHERE sql is not null")

for ddl in df_ddl['sql'].to_list():
  vn.train(ddl=ddl)

# Sometimes you may want to add documentation about your business terminology or definitions.
vn.train(documentation="A tabela 'produto' contém informações dos produtos.")
vn.train(documentation="A tabela 'categoria' contém as categorias dos produtos.")
vn.train(documentation="A tabela 'vendas' contém a quantidade de vendas, a data de vendas dos produtos.")
vn.train(documentation="A tabela 'produto' se conecta à tabela 'vendas' pela coluna produto_id usando INNER JOIN.")
vn.train(documentation="A tabela 'produto' se conecta à tabela 'categoria' pela coluna categoria_id usando INNER JOIN.") 
vn.train(documentation="A coluna 'produto' representa o nome do item vendido; 'quantidade' é o número de unidades compradas.")

# (Opcional) Visualiza os dados de treinamento
# At any time you can inspect what training data the package is able to reference
training_data = vn.get_training_data()
print(training_data)

# Faz uma pergunta para gerar SQL
#question = "Qual é a quantidade de produtos por categoria?"
question = "Quais foram os produtos que mais venderam no mês de agosto?"

print("---------------->Pergunta:", question)
response = vn.ask(question=question)
print("---------------------- RESPOSTA --------------------")
print("----------------------->Resposta gerada:", response)
