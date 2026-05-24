"""Gerador do catálogo completo de 200 datasets públicos."""
import csv, pathlib

OUT = pathlib.Path(__file__).parent.parent / "data" / "public_datasets_catalog.csv"

FIELDS = ["datasetName","about","link","categoryName","cloud","vintage"]

NEW = [
    # ── BRASIL ──
    ["IBGE Censo","Censo Demográfico Brasileiro","https://www.ibge.gov.br/estatisticas/sociais/populacao/22827-censo-demografico-2022.html","Demographics","","2022"],
    ["IBGE SIDRA","Sistema IBGE de Recuperação Automática (API)","https://sidra.ibge.gov.br/","Government","","NA"],
    ["IBGE POF","Pesquisa de Orçamentos Familiares","https://www.ibge.gov.br/pof","Social Sciences","","2017"],
    ["IBGE PNAD","Pesquisa Nacional por Amostra de Domicílios","https://www.ibge.gov.br/pnad","Social Sciences","","2023"],
    ["IBGE Municípios","Dados municipais por estado","https://www.ibge.gov.br/cidades-e-estados","GIS","","NA"],
    ["DATASUS","Dados do SUS — Morbidade, mortalidade, AIH","https://datasus.saude.gov.br/","Healthcare","","NA"],
    ["DATASUS TabNet","Tabulador de dados de saúde do SUS","http://tabnet.datasus.gov.br/","Healthcare","","NA"],
    ["SINASC","Sistema de Informações sobre Nascidos Vivos","https://datasus.saude.gov.br/nascidos-vivos/","Healthcare","","NA"],
    ["SIM","Sistema de Informações sobre Mortalidade","https://datasus.saude.gov.br/mortalidade/","Healthcare","","NA"],
    ["EMBRAPA Solos","Base de dados de solos do Brasil","https://www.embrapa.br/solos/sibcs","Agriculture","","NA"],
    ["EMBRAPA Zoneamento","Zoneamento Agrícola de Risco Climático","https://www.embrapa.br/zarc","Agriculture","","NA"],
    ["INPE Queimadas","Monitoramento de focos de incêndio","https://queimadas.dgi.inpe.br/","Environment","","NA"],
    ["INPE PRODES","Desmatamento Amazônia Legal","https://www.obt.inpe.br/prodes/","Environment","","NA"],
    ["INPE DETER","Detecção de Desmatamento em Tempo Real","https://www.obt.inpe.br/deter/","Environment","","NA"],
    ["IPEA Data","Base de dados socioeconômicos do IPEA","http://www.ipeadata.gov.br/","Social Sciences","","NA"],
    ["IPEA Atlas","Atlas do Desenvolvimento Humano no Brasil","http://www.atlasbrasil.org.br/","Social Sciences","","2013"],
    ["BCB SGS","Sistema Gerenciador de Séries Temporais do BCB","https://www3.bcb.gov.br/sgspub/","Finance","","NA"],
    ["BCB Open Data","API Open Data Banco Central do Brasil","https://dadosabertos.bcb.gov.br/","Finance","","NA"],
    ["ANS Dados","Dados de planos de saúde — ANS","https://www.ans.gov.br/anstabnet/","Healthcare","","NA"],
    ["INEP Censo Escolar","Censo Escolar da Educação Básica","https://www.gov.br/inep/censo-escolar","Education","","NA"],
    ["INEP ENEM","Microdados ENEM","https://www.gov.br/inep/enem","Education","","NA"],
    ["INEP IDEB","Índice de Desenvolvimento da Educação Básica","https://www.gov.br/inep/ideb","Education","","NA"],
    ["MTE CAGED","Cadastro Geral de Empregados e Desempregados","https://www.gov.br/trabalho/caged","Social Sciences","","NA"],
    ["RAIS","Relação Anual de Informações Sociais","https://bi.mte.gov.br/bgcaged/","Social Sciences","","NA"],
    ["TCU Open","Dados abertos do Tribunal de Contas da União","https://portal.tcu.gov.br/dados-abertos/","Government","","NA"],
    ["Portal Dados BR","Portal Brasileiro de Dados Abertos","https://dados.gov.br/","Government","","NA"],
    ["ANATEL","Dados de telecomunicações ANATEL","https://www.anatel.gov.br/dadosabertos/","Telecommunications","","NA"],
    ["ANAC","Dados de aviação civil ANAC","https://www.anac.gov.br/dadosabertos/","Transportation","","NA"],
    ["DNIT","Rede de transporte e rodovias federais","https://www.gov.br/dnit/dados-abertos","Transportation","","NA"],
    ["SICAR","Cadastro Ambiental Rural","https://www.car.gov.br/publico/imoveis/","Environment","","NA"],
    # ── ONU / ONUSYS ──
    ["UN Data","UN Statistics Division Data Repository","https://data.un.org/","Government","","NA"],
    ["UNDP HDR","Human Development Reports Data","https://hdr.undp.org/data-center","Social Sciences","","NA"],
    ["UNHCR Data","Refugees and displacement data","https://www.unhcr.org/refugee-statistics/","Social Sciences","","NA"],
    ["UNODC","UN Office on Drugs and Crime Statistics","https://dataunodc.un.org/","Social Sciences","","NA"],
    ["UNComtrade","UN Comtrade: international trade statistics","https://comtradeplus.un.org/","Finance","","NA"],
    ["FAO FAOSTAT","Food and Agriculture Organization Statistics","https://www.fao.org/faostat/","Agriculture","","NA"],
    ["FAO AQUASTAT","Global water resources","https://www.fao.org/aquastat/","Environment","","NA"],
    ["WHO GHO","Global Health Observatory","https://www.who.int/data/gho","Healthcare","","NA"],
    ["WHO COVID","WHO COVID-19 Dashboard Data","https://covid19.who.int/data","Healthcare","","NA"],
    ["ILO ILOSTAT","International Labour Organization Statistics","https://ilostat.ilo.org/","Social Sciences","","NA"],
    ["UNESCO UIS","UNESCO Institute for Statistics","https://uis.unesco.org/","Education","","NA"],
    ["UNICEF MICS","Multiple Indicator Cluster Surveys","https://mics.unicef.org/","Social Sciences","","NA"],
    ["UNEP ENV","UN Environment Programme Data","https://www.unep.org/resources/datasets","Environment","","NA"],
    # ── BANCO MUNDIAL ──
    ["World Bank WDI","World Development Indicators","https://databank.worldbank.org/source/world-development-indicators","Government","","NA"],
    ["World Bank Poverty","Poverty and Inequality Platform","https://pip.worldbank.org/","Social Sciences","","NA"],
    ["World Bank Climate","Climate Change Knowledge Portal","https://climateknowledgeportal.worldbank.org/","Climate/Weather","","NA"],
    ["World Bank Education","EdStats — Education Statistics","https://datatopics.worldbank.org/education/","Education","","NA"],
    ["World Bank Health","Health Nutrition and Population","https://databank.worldbank.org/source/health-nutrition-and-population","Healthcare","","NA"],
    ["World Bank Gender","Gender Statistics","https://databank.worldbank.org/source/gender-statistics","Social Sciences","","NA"],
    ["World Bank Open","Open Data Portal","https://data.worldbank.org/","Government","","NA"],
    ["IFC","International Finance Corporation Data","https://www.ifc.org/en/data","Finance","","NA"],
    # ── OCDE ──
    ["OECD iLibrary","OECD Statistics and Indicators","https://stats.oecd.org/","Government","","NA"],
    ["OECD PISA","Programme for International Student Assessment","https://www.oecd.org/pisa/data/","Education","","2022"],
    ["OECD Health","OECD Health Statistics","https://www.oecd.org/health/health-data.htm","Healthcare","","NA"],
    ["OECD Environment","OECD Environment Statistics","https://stats.oecd.org/Index.aspx?DataSetCode=ENV_DEV","Environment","","NA"],
    ["OECD Labour","OECD Labour Market Statistics","https://stats.oecd.org/Index.aspx?DataSetCode=LFS_SEXAGE_I_R","Social Sciences","","NA"],
    ["OECD AI","OECD AI Policy Observatory Data","https://oecd.ai/en/data","Computer Networks","","NA"],
    # ── NASA / NOAA ──
    ["NASA Earthdata","NASA Earth Science Data","https://earthdata.nasa.gov/","Environment","Amazon","NA"],
    ["NASA POWER","NASA Prediction of Worldwide Energy Resources","https://power.larc.nasa.gov/","Energy","","NA"],
    ["NASA NEO","NASA Earth Observations","https://neo.gsfc.nasa.gov/","Environment","","NA"],
    ["NOAA Climate","NOAA Global Climate Data","https://www.ncei.noaa.gov/access/search/","Climate/Weather","","NA"],
    ["NOAA GHCN","Global Historical Climatology Network","https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily","Climate/Weather","","1800"],
    ["NOAA Oceans","NOAA National Centers for Coastal Ocean Science","https://coastalscience.noaa.gov/data/","Environment","","NA"],
    ["NOAA Storms","Storm Events Database","https://www.ncdc.noaa.gov/stormevents/","Climate/Weather","","1950"],
    ["NASA GISS","GISS Surface Temperature Analysis (GISTEMP)","https://data.giss.nasa.gov/gistemp/","Climate/Weather","","1880"],
    ["ESA Sentinel","ESA Sentinel Satellite Data","https://sentinels.copernicus.eu/web/sentinel/home","GIS","","NA"],
    ["USGS EarthExplorer","USGS Earth Explorer Remote Sensing","https://earthexplorer.usgs.gov/","GIS","","NA"],
    # ── SAÚDE GLOBAL ──
    ["CDC WONDER","CDC Wide-ranging Online Data for Epidemiology","https://wonder.cdc.gov/","Healthcare","","NA"],
    ["CDC NHANES","National Health and Nutrition Examination Survey","https://www.cdc.gov/nchs/nhanes/","Healthcare","","1960"],
    ["NIH PubChem","Chemical compound data","https://pubchem.ncbi.nlm.nih.gov/","Biology","","NA"],
    ["ClinicalTrials","ClinicalTrials.gov Dataset","https://clinicaltrials.gov/api/gui","Healthcare","","NA"],
    ["SEER Cancer","Surveillance, Epidemiology, and End Results","https://seer.cancer.gov/data/","Healthcare","","1973"],
    ["GBD","Global Burden of Disease Study (IHME)","https://vizhub.healthdata.org/gbd-results/","Healthcare","","1990"],
    # ── ECONOMIA / FINANÇAS ──
    ["IMF Data","International Monetary Fund Data","https://data.imf.org/","Finance","","NA"],
    ["IMF WEO","World Economic Outlook Database","https://www.imf.org/en/Publications/WEO","Finance","","NA"],
    ["BIS Stats","Bank for International Settlements Statistics","https://www.bis.org/statistics/","Finance","","NA"],
    ["Federal Reserve","Federal Reserve Economic Data (FRED)","https://fred.stlouisfed.org/","Finance","","1913"],
    ["ECB Data","European Central Bank Statistical Data Warehouse","https://sdw.ecb.europa.eu/","Finance","","NA"],
    ["Quandl","Quandl Financial Data","https://data.nasdaq.com/","Finance","","NA"],
    ["Yahoo Finance","Yahoo Finance Historical Data","https://finance.yahoo.com/","Finance","","NA"],
    ["Coinbase","Coinbase Cryptocurrency Exchange Data","https://www.coinbase.com/developer-platform","Finance","","2012"],
    # ── MACHINE LEARNING / BENCHMARK ──
    ["UCI Repository","UCI Machine Learning Repository","https://archive.ics.uci.edu/","Machine Learning","","NA"],
    ["OpenML","OpenML: Open Machine Learning","https://www.openml.org/","Machine Learning","","NA"],
    ["MNIST","MNIST Handwritten Digits","http://yann.lecun.com/exdb/mnist/","Machine Learning","","1998"],
    ["ImageNet","ImageNet Large Scale Visual Recognition","https://www.image-net.org/","Image Processing","","2009"],
    ["COCO Dataset","Common Objects in Context","https://cocodataset.org/","Image Processing","","2014"],
    ["LibriSpeech","LibriSpeech ASR corpus","https://www.openslr.org/12","Natural Language","","2015"],
    ["SQuAD","Stanford Question Answering Dataset","https://rajpurkar.github.io/SQuAD-explorer/","Natural Language","","2016"],
    ["GLUE Benchmark","General Language Understanding Evaluation","https://gluebenchmark.com/","Natural Language","","2018"],
    ["CommonVoice","Mozilla Common Voice","https://commonvoice.mozilla.org/datasets","Natural Language","GitHub","NA"],
    ["CC-100","CC-100 Multilingual Corpus","https://data.statmt.org/cc-100/","Natural Language","","2020"],
    ["The Pile","The Pile — 825GB Text Dataset","https://pile.eleuther.ai/","Natural Language","","2020"],
    ["RedPajama","RedPajama Open Dataset 1.2T tokens","https://github.com/togethercomputer/RedPajama-Data","Natural Language","GitHub","2023"],
    ["LAION-5B","LAION-5B Image-Text Pairs","https://laion.ai/blog/laion-5b/","Image Processing","","2022"],
    ["BigBench","Beyond the Imitation Game Benchmark","https://github.com/google/BIG-bench","Machine Learning","GitHub","2022"],
    # ── CLIMA / ENERGIA ──
    ["Our World in Data","Our World in Data Datasets","https://github.com/owid/owid-datasets","Social Sciences","GitHub","NA"],
    ["Global Carbon","Global Carbon Project Data","https://globalcarbonproject.org/carbonbudget/","Environment","","NA"],
    ["IRENA","International Renewable Energy Agency Stats","https://www.irena.org/Statistics","Energy","","NA"],
    ["IEA Data","International Energy Agency Statistics","https://www.iea.org/data-and-statistics","Energy","","NA"],
    ["EPA AQS","EPA Air Quality System Data","https://www.epa.gov/aqs","Environment","","1990"],
    ["GFDL","NOAA Geophysical Fluid Dynamics Lab Data","https://www.gfdl.noaa.gov/model-data/","Climate/Weather","","NA"],
    ["Copernicus C3S","Copernicus Climate Change Service ERA5","https://cds.climate.copernicus.eu/","Climate/Weather","","1940"],
    # ── CIDADES / MOBILIDADE ──
    ["NYC Open Data","New York City Open Data Portal","https://opendata.cityofnewyork.us/","Government","","NA"],
    ["SF Open Data","San Francisco Open Data","https://data.sfgov.org/","Government","","NA"],
    ["London Datastore","Greater London Authority Data","https://data.london.gov.uk/","Government","","NA"],
    ["Chicago Data","Chicago Data Portal","https://data.cityofchicago.org/","Government","","NA"],
    ["OpenStreetMap","OpenStreetMap Planet Dump","https://planet.openstreetmap.org/","GIS","","NA"],
    ["Overture Maps","Overture Maps Foundation Data","https://overturemaps.org/","GIS","","2023"],
    ["GTFS Exchange","General Transit Feed Specification Data","https://transitfeeds.com/","Transportation","","NA"],
    ["HERE Traffic","HERE Traffic Pattern Data","https://developer.here.com/","Transportation","","NA"],
    # ── REDES SOCIAIS / WEB ──
    ["Reddit Pushshift","Reddit Comments Pushshift Archive","https://archive.org/details/pushshift_reddit_archive","Social Networks","","2005"],
    ["Wikipedia Dumps","Wikipedia Article Dumps","https://dumps.wikimedia.org/","Natural Language","","NA"],
    ["Stack Exchange","Stack Exchange Data Dump","https://archive.org/details/stackexchange","Computer Networks","","2008"],
    ["arXiv Full","arXiv Full Text Corpus","https://info.arxiv.org/help/bulk_data.html","Natural Language","Amazon","1991"],
    ["PubMed Central","PubMed Central Full Text","https://www.ncbi.nlm.nih.gov/pmc/tools/ftp/","Healthcare","","NA"],
    ["DBLP","DBLP Computer Science Bibliography","https://dblp.uni-trier.de/xml/","Computer Networks","","NA"],
    ["CrossRef","CrossRef Metadata Plus — 140M records","https://www.crossref.org/blog/2023-public-data-file/","Natural Language","","NA"],
    ["OpenAlex","OpenAlex Open Scholarly Graph","https://openalex.org/","Natural Language","","NA"],
    ["Semantic Scholar","Semantic Scholar Open Research Corpus","https://api.semanticscholar.org/graph/v1/","Natural Language","","NA"],
    # ── BRASIL COMPLEMENTAR ──
    ["Transparência BR","Portal da Transparência do Governo Federal","https://transparencia.gov.br/download-de-dados","Government","","NA"],
    ["SIGA Brasil","Sistema de Informações sobre Orçamentos Públicos","https://www1.siop.planejamento.gov.br/siga/","Finance","","NA"],
    ["CVM Open","Comissão de Valores Mobiliários — dados abertos","https://dados.cvm.gov.br/","Finance","","NA"],
    ["INMET","Instituto Nacional de Meteorologia","https://bdmep.inmet.gov.br/","Climate/Weather","","1961"],
    ["ANA Hidro","Agência Nacional de Águas — HidroWeb","https://www.snirh.gov.br/hidroweb/","Environment","","NA"],
    ["MapBiomas","Mapeamento anual do uso da terra no Brasil","https://mapbiomas.org/en/statistics","Environment","","1985"],
    ["DENATRAN","Frota de veículos por município","https://www.gov.br/senatran/","Transportation","","NA"],
    ["ANEEL","Dados do setor elétrico — ANEEL","https://dadosabertos.aneel.gov.br/","Energy","","NA"],
    ["ANP","Agência Nacional do Petróleo — estatísticas","https://www.gov.br/anp/dados-estatisticos","Energy","","NA"],
    ["CONAB","Séries históricas agropecuárias CONAB","https://www.conab.gov.br/info-agro/safras/serie-historica-das-safras","Agriculture","","NA"],
    ["IBAMA","Autos de infração ambiental — IBAMA","https://servicos.ibama.gov.br/ctf/publico/areasembargo/","Environment","","NA"],
    ["STF Processos","Dados de processos judiciais STF","https://portal.stf.jus.br/servicos/dados-abertos/","Government","","NA"],
    ["TJSP Open","Tribunal de Justiça de SP — dados abertos","https://www.tjsp.jus.br/DadosAbertos","Government","","NA"],
    ["CNES","Cadastro Nacional de Estabelecimentos de Saúde","https://datasus.saude.gov.br/cnes/","Healthcare","","NA"],
    ["RIPSA","Rede de Informações para a Saúde","http://www.ripsa.org.br/","Healthcare","","NA"],
]

def main():
    existing = []
    if OUT.exists():
        with open(OUT, encoding='utf-8') as f:
            existing = list(csv.DictReader(f))

    existing_names = {r['datasetName'] for r in existing}
    added = 0
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(FIELDS)
        for row in existing:
            writer.writerow([row.get(k,'') for k in FIELDS])
        for row in NEW:
            if row[0] not in existing_names:
                writer.writerow(row)
                added += 1

    total = len(existing) + added
    print(f"✅ Catálogo salvo: {OUT}")
    print(f"   Existentes: {len(existing)} | Novos: {added} | Total: {total}")

if __name__ == '__main__':
    main()
