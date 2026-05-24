import spacy

# Carrega o modelo treinado para testar
nlp = spacy.load("model_ner")
#doc = nlp("O CNPJ 12.345.678/0001-90 emitiu uma nota fiscal de R$ 123,45.")
doc = nlp("['63.358.000/0001-49'],['9,28', '9,25'],['25/06/2012']")
if doc.ents:
    for ent in doc.ents:
        print(f"Texto: {ent.text}, Label: {ent.label_}")
else:
    print("Nenhuma entidade reconhecida.")
