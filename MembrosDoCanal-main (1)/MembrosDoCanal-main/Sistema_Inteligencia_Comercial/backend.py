
import os
import sqlite3
import pandas as pd
import json
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURAÇÃO INICIAL ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("API Key do Google não encontrada. Verifique seu arquivo .env.")
genai.configure(api_key=api_key)

DB_PATH = 'database/estoque.db'

# --- FUNÇÕES DE BANCO DE DADOS (GENÉRICAS) ---

def execute_query(query, params=(), fetch=None):
    """Executa uma query no banco de dados."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetch == 'one':
            return cursor.fetchone()
        if fetch == 'all':
            return cursor.fetchall()
        conn.commit()

def df_from_query(query, params=()):
    """Cria um DataFrame a partir de uma query."""
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn, params=params)

# --- MÓDULO DE PROSPECÇÃO DE VENDAS ---

def load_leads(file_path='leads.csv'):
    """Carrega os leads de um arquivo CSV."""
    return pd.read_csv(file_path)

def get_prospecting_insights(lead, your_product):
    """Usa a IA para gerar insights de prospecção."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    **Contexto:** Vendo '{your_product}'. Preciso de ajuda para prospectar o lead: {lead['empresa']}.
    **Descrição:** {lead['descricao_empresa']}
    **Contato:** {lead['contato_nome']} ({lead['contato_cargo']})
    **Tarefa:** Aja como um especialista em vendas B2B. Responda APENAS com um JSON contendo as chaves: `pontos_de_dor` (lista de 2-3 dores), `gancho_personalizado` (frase de abertura), e `rascunho_email` (e-mail curto e profissional para o contato).
    """
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text.strip().replace('```json', '').replace('```', ''))
    except (Exception, json.JSONDecodeError) as e:
        return {"error": f"Erro ao processar IA: {e}"}

def get_all_product_names():
    """Retorna uma lista com os nomes de todos os produtos."""
    return df_from_query("SELECT nome FROM produtos ORDER BY nome ASC")['nome'].tolist()

def register_opportunity(empresa_lead, produto_nome, quantidade_proposta):
    """Registra uma nova oportunidade de venda no banco de dados."""
    produto_id = execute_query("SELECT id FROM produtos WHERE nome = ?", (produto_nome,), fetch='one')
    if produto_id:
        query = "INSERT INTO oportunidades (empresa_lead, produto_id, quantidade_proposta, status, data_criacao) VALUES (?, ?, ?, ?, ?)"
        params = (empresa_lead, produto_id[0], quantidade_proposta, 'Em Negociação', datetime.now().strftime('%Y-%m-%d'))
        execute_query(query, params)
        return True
    return False

# --- MÓDULO DE GESTÃO DE ESTOQUE E COMPRAS ---

def get_inactive_stock_kpis(days_inactive=90):
    """Calcula os KPIs de estoque inativo."""
    query = f"""
        SELECT SUM(quantidade * preco) as valor_inativo, COUNT(*) as contagem_inativa
        FROM produtos
        WHERE data_ultima_venda <= date('now', '-{days_inactive} days')
    """
    df = df_from_query(query)
    valor_inativo = df['valor_inativo'].iloc[0] or 0
    contagem_inativa = df['contagem_inativa'].iloc[0] or 0
    return {
        "inactive_stock_value": f"R$ {valor_inativo:,.2f}",
        "inactive_product_count": contagem_inativa
    }

def get_excess_stock_alert(days_inactive=90, min_quantity=50):
    """Identifica produtos inativos com alta quantidade."""
    query = f"""
        SELECT nome, quantidade, data_ultima_venda
        FROM produtos
        WHERE data_ultima_venda <= date('now', '-{days_inactive} days') AND quantidade >= {min_quantity}
    """
    return df_from_query(query)

def get_inactive_product_suggestions(days_inactive=90):
    """Busca produtos inativos e gera sugestões de ação para eles."""
    query = f"SELECT nome, quantidade, data_ultima_venda FROM produtos WHERE data_ultima_venda <= date('now', '-{days_inactive} days')"
    inactive_products_df = df_from_query(query)

    if inactive_products_df.empty:
        return pd.DataFrame()

    suggestions = []
    model = genai.GenerativeModel('gemini-1.5-flash')

    for _, row in inactive_products_df.iterrows():
        prompt = f"""
        **Análise de Produto Inativo**
        - **Produto:** {row['nome']}
        - **Quantidade em Estoque:** {row['quantidade']}
        - **Data da Última Venda:** {row['data_ultima_venda']}

        **Tarefa:** Sugira 3 ações estratégicas e concisas para este item (ex: promoção, combo, queima de estoque). Use um subtítulo em negrito para cada ação.
        """
        try:
            response = model.generate_content(prompt)
            suggestions.append(response.text if response.parts else "Não foi possível gerar sugestões.")
        except Exception:
            suggestions.append("Erro ao contatar a IA.")
    
    inactive_products_df['sugestoes'] = suggestions
    return inactive_products_df

def get_purchase_opportunities(low_stock_threshold=10):
    query = f"SELECT id, nome, quantidade, demanda_mensal FROM produtos WHERE quantidade <= {low_stock_threshold} AND quantidade > 0"
    return df_from_query(query)

def get_suppliers_for_product(product_id):
    return df_from_query("SELECT nome_fornecedor, preco_unidade, prazo_entrega_dias FROM fornecedores WHERE produto_id = ?", (product_id,))

def get_purchase_recommendation(product, suppliers_df):
    """Usa a IA para obter uma recomendação de compra."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    **Contexto:** Preciso comprar '{product['nome']}'. Estoque atual: {product['quantidade']}, Demanda mensal: {product['demanda_mensal']}.
    **Fornecedores:**
    {suppliers_df.to_markdown(index=False)}
    **Tarefa:** Aja como um especialista em compras. Responda APENAS com um JSON com as chaves: `fornecedor_escolhido`, `quantidade_sugerida`, `justificativa` (curta e objetiva), e `rascunho_email`.
    """
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text.strip().replace('```json', '').replace('```', ''))
    except (Exception, json.JSONDecodeError) as e:
        return {"error": f"Erro ao processar IA: {e}"}



# --- MÓDULO DE ANÁLISE ESTRATÉGICA (Sinergia) ---

def get_demand_analysis():
    """Analisa o impacto de oportunidades de venda no estoque atual."""
    query = """
        SELECT 
            o.empresa_lead,
            p.nome as produto_nome,
            o.quantidade_proposta,
            p.quantidade as estoque_atual,
            (p.quantidade - o.quantidade_proposta) as estoque_projetado
        FROM oportunidades o
        JOIN produtos p ON o.produto_id = p.id
        WHERE o.status = 'Em Negociação'
    """
    df = df_from_query(query)
    df['alerta'] = df['estoque_projetado'] < 0
    return df

# --- MÓDULO DE DASHBOARD (KPIs) ---

def get_main_kpis():
    """Calcula os KPIs principais para o dashboard."""
    query_total_stock = "SELECT SUM(quantidade * preco) FROM produtos"
    total_stock_value = execute_query(query_total_stock, fetch='one')[0] or 0
    
    query_opportunities = "SELECT COUNT(*), SUM(p.preco * o.quantidade_proposta) FROM oportunidades o JOIN produtos p ON o.produto_id = p.id WHERE o.status = 'Em Negociação'"
    active_deals_count, active_deals_value = execute_query(query_opportunities, fetch='one')
    active_deals_value = active_deals_value or 0

    return {
        "total_stock_value": f"R$ {total_stock_value:,.2f}",
        "active_deals_count": active_deals_count or 0,
        "active_deals_value": f"R$ {active_deals_value:,.2f}"
    }
