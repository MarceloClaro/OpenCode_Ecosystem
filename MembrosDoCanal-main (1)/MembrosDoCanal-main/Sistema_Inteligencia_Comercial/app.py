import streamlit as st
import pandas as pd
from backend import (
    load_leads,
    get_prospecting_insights,
    get_all_product_names,
    register_opportunity,
    get_purchase_opportunities,
    get_suppliers_for_product,
    get_purchase_recommendation,
    get_demand_analysis,
    get_main_kpis,
    get_inactive_stock_kpis,
    get_excess_stock_alert,
    get_inactive_product_suggestions
)

st.set_page_config(page_title="Plataforma de Inteligência Comercial", layout="wide")

# --- TÍTULO PRINCIPAL ---
st.title("🚀 Sistema de Inteligência Comercial com IA")

# --- KPIs GERAIS ---
st.divider()
kpis = get_main_kpis()
col1, col2, col3 = st.columns(3)
col1.metric("Valor Total em Estoque", kpis['total_stock_value'])
col2.metric("Oportunidades Ativas", kpis['active_deals_count'])
col3.metric("Valor em Negociação", kpis['active_deals_value'])
st.divider()

# --- LAYOUT EM ABAS ---
tab_vendas, tab_compras, tab_demanda = st.tabs([
    "🕵️‍♂️ Prospecção de Vendas", 
    "🛒 Gestão de Estoque e Compras", 
    "📈 Análise de Demanda Futura"
])

# --- ABA DE VENDAS ---
with tab_vendas:
    st.header("Gerador de Prospecção Inteligente")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Configuração", anchor=False)
        your_product = st.text_area("Descreva seu produto/serviço:", "um software de automação de marketing.", height=100)
        leads_df = load_leads()
        leads_df['display_name'] = leads_df['empresa'] + " - " + leads_df['contato_cargo']
        option = st.selectbox("Escolha o lead para prospectar:", leads_df['display_name'])
        selected_lead = leads_df.iloc[leads_df.index[leads_df['display_name'] == option].tolist()[0]]
    with col2:
        if st.button(f"Gerar Prospecção para {selected_lead['empresa']}", type="primary"):
            with st.spinner("Analisando o lead com IA..."):
                insights = get_prospecting_insights(selected_lead, your_product)
                st.session_state.insights = insights
                st.session_state.selected_lead = selected_lead
        if 'insights' in st.session_state:
            if "error" in st.session_state.insights:
                st.error(st.session_state.insights["error"])
            else:
                st.subheader("✉️ Rascunho do E-mail de Prospecção", anchor=False)
                st.text_area("", st.session_state.insights['rascunho_email'], height=250)
                st.info(f"**Gancho Sugerido:** *{st.session_state.insights['gancho_personalizado']}*", icon="💡")
                st.subheader("Registrar Oportunidade", anchor=False)
                produto_nome = st.selectbox("Qual produto está sendo ofertado?", get_all_product_names(), key="produto_oferta")
                quantidade = st.number_input("Qual a quantidade proposta?", min_value=1, value=10)
                if st.button("Registrar Oportunidade no Sistema"):
                    success = register_opportunity(st.session_state.selected_lead['empresa'], produto_nome, quantidade)
                    if success:
                        st.success(f"Oportunidade registrada!")
                        del st.session_state.insights
                    else:
                        st.error("Erro ao registrar a oportunidade.")

# --- ABA DE COMPRAS E ESTOQUE ---
with tab_compras:
    st.header("Dashboard de Estoque e Assistente de Compras")
    st.subheader("Análise de Estoque Inativo", anchor=False)
    inactive_kpis = get_inactive_stock_kpis()
    col1, col2 = st.columns(2)
    col1.metric("Valor do Estoque Inativo", inactive_kpis['inactive_stock_value'])
    col2.metric("Nº de Produtos Inativos", inactive_kpis['inactive_product_count'])
    excess_stock_df = get_excess_stock_alert()
    if not excess_stock_df.empty:
        with st.expander("⚠️ Alerta de Excesso de Estoque"):
            st.warning("Produtos inativos com alto volume, representando custo de oportunidade:")
            st.dataframe(excess_stock_df, use_container_width=True)
    st.divider()
    st.subheader("Otimização de Estoque Inativo com IA", anchor=False)
    if st.button("Analisar Produtos Inativos e Gerar Sugestões", type="primary"):
        with st.spinner("IA está analisando seu estoque parado..."):
            st.session_state.suggestions_df = get_inactive_product_suggestions()
    if 'suggestions_df' in st.session_state:
        if st.session_state.suggestions_df.empty:
            st.success("Nenhum produto inativo encontrado para análise.")
        else:
            st.markdown("**Sugestões da IA para otimizar o estoque:**")
            for _, row in st.session_state.suggestions_df.iterrows():
                with st.container(border=True):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.info(f"**Produto:** {row['nome']}")
                        st.metric("Estoque", f"{row['quantidade']} un.")
                        st.metric("Última Venda", row['data_ultima_venda'].split(' ')[0])
                    with col2:
                        st.markdown(row['sugestoes'])
    st.divider()
    st.subheader("Assistente de Compras para Estoque Baixo", anchor=False)
    purchase_opportunities = get_purchase_opportunities()
    if purchase_opportunities.empty:
        st.success("Nenhum produto com estoque baixo encontrado.")
    else:
        for _, product in purchase_opportunities.iterrows():
            with st.container(border=True):
                st.subheader(f"Produto: {product['nome']}", anchor=False)
                col1, col2 = st.columns(2)
                col1.metric("Estoque Atual", f"{product['quantidade']} un.", delta_color="inverse")
                col2.metric("Demanda Mensal", f"{product['demanda_mensal']} un.")
                suppliers_df = get_suppliers_for_product(product['id'])
                if not suppliers_df.empty:
                    with st.expander("Ver Fornecedores e Gerar Recomendação de Compra"):
                        st.dataframe(suppliers_df, use_container_width=True)
                        if st.button(f"Gerar Análise de Compra para {product['nome']}", type="primary"):
                            with st.spinner("IA está analisando os melhores fornecedores..."):
                                recommendation = get_purchase_recommendation(product, suppliers_df)
                                if "error" in recommendation:
                                    st.error(recommendation["error"])
                                else:
                                    st.info(f"**Recomendação:** Comprar {recommendation['quantidade_sugerida']} un. do fornecedor **{recommendation['fornecedor_escolhido']}**.")
                                    st.markdown(f"**Justificativa:** *{recommendation['justificativa']}*")
                                    st.text_area("Rascunho do E-mail de Compra", recommendation['rascunho_email'], height=200, key=f"email_{product['id']}")
                else:
                    st.warning("Nenhum fornecedor cadastrado para este produto.")

# --- ABA DE ANÁLISE DE DEMANDA ---
with tab_demanda:
    st.header("Análise de Impacto das Oportunidades de Venda no Estoque")
    st.markdown("Esta análise cruza as oportunidades de venda em negociação com o estoque atual para prever possíveis rupturas.")
    demand_df = get_demand_analysis()
    if demand_df.empty:
        st.success("Nenhuma oportunidade ativa para analisar.")
    else:
        st.dataframe(demand_df, use_container_width=True, 
                     column_config={
                         "alerta": st.column_config.CheckboxColumn("Risco de Ruptura?", default=False),
                         "estoque_projetado": st.column_config.NumberColumn(format="%d un.")
                     })
        alertas = demand_df[demand_df['alerta'] == True]
        if not alertas.empty:
            st.divider()
            st.error("**Atenção!** As seguintes oportunidades podem causar ruptura de estoque:")
            for _, alerta in alertas.iterrows():
                st.markdown(f"- A negociação com **{alerta['empresa_lead']}** para vender {alerta['quantidade_proposta']} un. de **{alerta['produto_nome']}** deixará o estoque negativo.")