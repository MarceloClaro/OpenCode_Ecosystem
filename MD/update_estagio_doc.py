import os
import re

fpath = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD\02-Dissertação_EstagioAtual.md"

with open(fpath, "r", encoding="utf-8") as f:
    content = f.read()

# Let's verify line 83 and 85 replacements
old_cite1 = "autonomia (de Almeida & Schmidt, 2020)"
new_cite1 = "autonomia (Schmidt, 1983)"

old_cite2 = "conceitos disciplinares (Garcia et al., 2021)"
new_cite2 = "conceitos disciplinares (Thomas, 2000)"

old_cite3 = "secretarias estaduais de Educação (Silva & Souza, 2022)"
new_cite3 = "secretarias estaduais de Educação (Oliveira et al., 2023)"

old_cite4 = "engajamento estudantil (Ferreira & Mendes, 2023)"
new_cite4 = "engajamento estudantil (Silva et al., 2023)"

if old_cite1 in content:
    content = content.replace(old_cite1, new_cite1)
    print("Replaced cite 1")
else:
    print("Cite 1 not found!")

if old_cite2 in content:
    content = content.replace(old_cite2, new_cite2)
    print("Replaced cite 2")
else:
    print("Cite 2 not found!")

if old_cite3 in content:
    content = content.replace(old_cite3, new_cite3)
    print("Replaced cite 3")
else:
    print("Cite 3 not found!")

if old_cite4 in content:
    content = content.replace(old_cite4, new_cite4)
    print("Replaced cite 4")
else:
    print("Cite 4 not found!")

# Let's replace references section
ref_match = re.search(r"# REFER\?NCIAS|REFER\?NCIAS\s+BIBLIOGR\?FICAS", content, re.IGNORECASE)
if ref_match:
    idx = ref_match.start()
    content = content[:idx]
else:
    # If not found via regex, find last heading '# REFER'
    idx = content.find("# REFER")
    if idx != -1:
        content = content[:idx]
    else:
        print("References heading not found!")

new_references = """# REFERÊNCIAS BIBLIOGRÁFICAS

ALMEIDA, Wellington Augusto Oliveira de et al. A utilização de tecnologias educacionais na aprendizagem baseada em problemas: uma revisão integrativa. *Caderno Pedagógico*, v. 21, n. 9, e8096, 2024. DOI: 10.54033/cadpedv21n9-232.

BACICH, Lilian; MORAN, José. *Metodologias ativas para uma aprendizagem mais profunda: uma abordagem teórico-prática*. Porto Alegre: Penso, 2018.

BLIKSTEIN, Paulo. Educação mão na massa: de onde vem, para onde vai. *Revista Porvir*, São Paulo, 2013. Disponível em: <https://porvir.org/educacao-mao-na-massa-de-onde-vem-para-onde-vai/>. Acesso em: 17 out. 2023.

BRASIL. Ministério da Educação. *Base Nacional Comum Curricular*. Brasília: MEC, 2018. Disponível em: <http://basenacionalcomum.mec.gov.br/images/BNCC_EI_EF_110518_versaofinal_site.pdf>. Acesso em: 17 out. 2023.

MORAN, José. Ensino e aprendizagem inovadores com tecnologias audiovisuais e telemáticas. In: MORAN, J. M.; MASETTO, M. T.; BEHRENS, M. A. (Eds.). *Novas tecnologias e mediação pedagógica*. Campinas: Papirus, 2010.

OLIVEIRA, Francisco Lindoval; NÓBREGA, Luciano; CAVALCANTE, Marcele Alves dos Santos. O uso das metodologias ativas de aprendizagem na formação do professor: das universidades para a prática nas escolas. *Revista Educação Pública*, v. 23, n. 8, 2023. Disponível em: <https://educacaopublica.cecierj.edu.br/artigos/23/8/o-uso-das-metodologias-ativas-de-aprendizagem-na-formacao-do-professor-das-universidades-para-a-pratica-nas-escolas>. Acesso em: 17 out. 2023.

PAPERT, Seymour. *Mindstorms: Children, computers, and powerful ideas*. New York: Basic Books, 1980. Disponível em: <https://archive.org/details/mindstormschil00pape>. Acesso em: 07 fev. 2022.

SCHMIDT, Henk G. Problem-based learning: rationale and description. *Medical Education*, v. 17, n. 1, p. 11-16, 1983. DOI: 10.1111/j.1365-2923.1983.tb01086.x.

SILVA, Lorena Garces et al. Aprendizagem baseada em projetos no ensino de Ciências. *Dialogia*, n. 45, 2023. DOI: 10.5585/45.2023.24026.

THOMAS, John W. *A review of research on project-based learning*. San Rafael: Autodesk Foundation, 2000. Disponível em: <https://www.pblworks.org/sites/default/files/2019-01/A_Review_of_Research_on_Project_Based_Learning.pdf>. Acesso em: 17 out. 2023.
"""

content = content + new_references

with open(fpath, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated 02-Dissertação_EstagioAtual.md successfully!")
