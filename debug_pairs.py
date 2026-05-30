import re
with open(r'C:\Users\marce\Downloads\Cópia de TRABALHO DE CONCLUSÃO DE CURSO.docx (2).md', 'r', encoding='utf-8') as f:
    texto = f.read()

pairs = [
    ('O bem estar psicol\u00f3gico configura-se atualmente',
     'O campo do bem-estar psicol\u00f3gico figura entre as prioridades contempor\u00e2neas'),
    ('Em um contexto onde as respostas terap\u00eauticas convencionais tornam-se insuficientes',
     'Quando as respostas terap\u00eauticas tradicionais mostram seus limites'),
    ('\u00c9 precisamente focando nessa dist\u00e2ncia que este estudo mobiliza a perspectiva decolonial',
     '\u00c9 justamente a partir dessa lacuna que esta pesquisa recorre \u00e0 perspectiva decolonial'),
    ('torna-se necess\u00e1rio mapear o estado atual do conhecimento',
     'faz-se oportuno examinar o estado da arte dos campos te\u00f3ricos'),
    ('A literatura documenta que esses familiares, predominantemente m\u00e3es, apresentam n\u00edveis de estresse expressivamente mais elevados',
     'Estudos indicam que esses familiares \u2014 em sua maioria m\u00e3es \u2014 exibem n\u00edveis de estresse significativamente superiores'),
    ('mundo interior rico e complexo (Silveira, 1992, p. 21)',
     'universo interior repleto de significados (Silveira, 1992, p. 21)'),
    ('n\u00e3o \u00e9, portanto, uma imposi\u00e7\u00e3o, mas o reconhecimento de uma afinidade entre duas correntes',
     'n\u00e3o configura um artif\u00edcio externo: trata-se do reconhecimento de uma converg\u00eancia entre duas correntes'),
    ('n\u00e3o se restringe \u00e0 domina\u00e7\u00e3o pol\u00edtica ou econ\u00f4mica, mas opera fundamentalmente no terreno da produ\u00e7\u00e3o e valida\u00e7\u00e3o do conhecimento',
     'n\u00e3o se limita ao controle pol\u00edtico ou econ\u00f4mico: ela atua sobretudo no \u00e2mbito da gera\u00e7\u00e3o e legitimação do saber'),
    ('Dados da Organiza\u00e7\u00e3o Mundial da Sa\u00fade apontam que cerca de  970 milh\u00f5es de pessoas carregam algum tipo de sofrimento mental',
     'Segundo a Organiza\u00e7\u00e3o Mundial da Sa\u00fade, aproximadamente 970 milh\u00f5es de pessoas em todo o mundo convivem com alguma forma de sofrimento mental'),
    ('Boaventura de Sousa Santos denomina esse processo \u201cepistemic\u00eddio\u201d: a destrui\u00e7\u00e3o sistem\u00e1tica de formas de conhecimento',
     'Boaventura de Sousa Santos batiza esse fen\u00f4meno de \u201cepistemic\u00eddio\u201d \u2014 o exterm\u00ednio sistem\u00e1tico de saberes'),
    ('Kwek (2024), ao investigar interven\u00e7\u00f5es comunit\u00e1rias baseadas em artes entre migrantes em Cingapura',
     'Em estudo sobre interven\u00e7\u00f5es comunit\u00e1rias mediadas pela arte junto a migrantes em Cingapura, Kwek (2024) constatou'),
]

for i, (old, new) in enumerate(pairs, 1):
    found = old in texto
    if found:
        texto = texto.replace(old, new)
        status = "OK"
    else:
        status = "FAIL"
    print(f'{i}: {status}')
