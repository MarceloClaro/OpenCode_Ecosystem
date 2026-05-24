import spacy
import random
from spacy.training import Example

# Prepara os dados de treinamento
# Prepara os dados de treinamento
TRAIN_DATA = [
    # Exemplos de CNPJ
    ("CNPJ 12.345.678/0001-90 emitiu a nota fiscal.", {"entities": [(5, 22, "CNPJ")]}),
    ("Empresa registrada sob o CNPJ 98.765.432/0001-10.", {"entities": [(30, 47, "CNPJ")]}),
    ("O CNPJ da empresa é 63.358.000/0001-49.", {"entities": [(20, 37, "CNPJ")]}),
    ("Fornecido pelo CNPJ 88.777.666/0001-99.", {"entities": [(20, 37, "CNPJ")]}),

    # Exemplos de valores monetários
    ("O valor foi de R$ 123,45.", {"entities": [(18, 23, "VALOR")]}),
    ("Total: R$ 2.345,67.", {"entities": [(10, 17, "VALOR")]}),
    ("Valor do produto: R$ 89,90.", {"entities": [(21, 25, "VALOR")]}),
    ("O pagamento foi de R$ 1.234,56.", {"entities": [(22, 29, "VALOR")]}),

    # Exemplos de datas
    ("A compra foi realizada em 01/01/2023.", {"entities": [(26, 36, "DATA")]}),
    ("Nota fiscal emitida em 31/12/2022.", {"entities": [(23, 33, "DATA")]}),
    ("Data de emissão: 15/08/2021.", {"entities": [(17, 27, "DATA")]}),
    ("Vencimento em 30/09/2023.", {"entities": [(14, 24, "DATA")]}),

    # Exemplos de nomes de empresas
    ("Supermercado ABC emitiu a nota.", {"entities": [(0, 16, "ORG")]}),
    ("Loja XYZ forneceu o produto.", {"entities": [(0, 8, "ORG")]}),
    ("Empresa Beta Ltda realizou a venda.", {"entities": [(0, 17, "ORG")]}),
    ("Nota emitida por Alpha Comércio.", {"entities": [(17, 31, "ORG")]}),

    # Exemplos de textos mistos
    ("A empresa Supermercado ABC com CNPJ 12.345.678/0001-90 emitiu uma nota de R$ 987,65 em 01/12/2023.", 
     {"entities": [(10, 26, "ORG"), (36, 53, "CNPJ"), (77, 82, "VALOR"), (87, 97, "DATA")]}),

    ("Loja XYZ, CNPJ 98.765.432/0001-10, vendeu produtos no valor de R$ 123,45 no dia 15/11/2022.", 
     {"entities": [(0, 8, "ORG"), (15, 32, "CNPJ"), (66, 71, "VALOR"), (80, 89, "DATA")]}),

    ("Emitido por Empresa Beta Ltda, CNPJ 22.333.444/0001-55, em 30/08/2021, totalizando R$ 456,78.", 
     {"entities": [(19, 27, "ORG"), (35, 52, "CNPJ"), (57, 66, "DATA"), (83, 88, "VALOR")]}),

    ("Pagamento de R$ 2.345,67 realizado em 31/12/2022 pela Alpha Comércio.", 
     {"entities": [(15, 22, "VALOR"), (37, 47, "DATA"), (53, 66, "ORG")]}),

    ("CNPJ 88.777.666/0001-99 da empresa Loja XYZ registrou uma venda de R$ 1.234,56 em 05/07/2022.", 
     {"entities": [(5, 22, "CNPJ"), (35, 44, "ORG"), (70, 77, "VALOR"), (82, 91, "DATA")]}),
]

# Inicia um modelo em branco para o português
nlp = spacy.blank("pt")

# Adiciona o componente de NER ao pipeline
ner = nlp.add_pipe("ner")

# Adiciona rótulos de entidades
ner.add_label("CNPJ")
ner.add_label("VALOR")
ner.add_label("DATA")
ner.add_label("ORG")

# Prepara os exemplos
examples = []
for text, annots in TRAIN_DATA:
    doc = nlp.make_doc(text)
    example = Example.from_dict(doc, annots)
    examples.append(example)

# Inicializa o modelo
nlp.initialize()

# Treinamento
optimizer = nlp.resume_training()
for i in range(200):  # Aumente o número de iterações
    random.shuffle(examples)
    for batch in spacy.util.minibatch(examples, size=8):
        nlp.update(batch, sgd=optimizer)

# Salva o modelo treinado
nlp.to_disk("model_ner")

# Carrega o modelo treinado para testar
nlp = spacy.load("model_ner")
#doc = nlp("O CNPJ 12.345.678/0001-90 emitiu uma nota fiscal de R$ 123,45.")
doc = nlp("['63.358.000/0001-49'],['9,28', '9,25'],['25/06/2012']")
if doc.ents:
    for ent in doc.ents:
        print(f"Texto: {ent.text}, Label: {ent.label_}")
else:
    print("Nenhuma entidade reconhecida.")
