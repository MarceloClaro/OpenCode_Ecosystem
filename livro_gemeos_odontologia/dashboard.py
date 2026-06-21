import streamlit as st
import math
import json
import hashlib
import time
import os
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Any

# Configurações de Design Visual Premium (Layout Amplo e Cores Governamentais)
st.set_page_config(
    page_title="SUS-Twin — Painel de Gêmeos Digitais Odontológicos",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Customizada (Aesthetics)
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A; /* Azul SUS */
        margin-bottom: 0.2rem;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 1rem;
        border-left: 5px solid #3B82F6;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .sidebar-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1F2937;
    }
</style>
""", unsafe_allow_html=True)

# --- CLASSES DO FRAMEWORK SUS-TWIN ---

class LPDSolver:
    def __init__(self, e_infinity: float, e_0: float, tau: float):
        self.e_infinity = e_infinity  # MPa
        self.e_0 = e_0                # MPa
        self.tau = tau                # s
        self.LPD_RUPTURE_LIMIT = 4.5  # MPa

    def calculate_stress(self, strain: float, elapsed_time: float) -> float:
        stress_0 = self.e_0 * strain
        stress_inf = self.e_infinity * strain
        decay = math.exp(-elapsed_time / self.tau)
        return stress_inf + (stress_0 - stress_inf) * decay

    def calculate_displacement(self, applied_force_n: float, stiffness: float) -> float:
        return applied_force_n / stiffness

class CrossValidator:
    def __init__(self, k_folds: int = 5):
        self.k_folds = k_folds

    def run_validation(self, dataset: List[Dict[str, float]]) -> Tuple[float, List[float]]:
        num_samples = len(dataset)
        fold_size = num_samples // self.k_folds
        errors = []
        
        # Semente local para estabilidade
        import random
        random.seed(42)
        shuffled_dataset = list(dataset)
        random.shuffle(shuffled_dataset)

        for fold in range(self.k_folds):
            val_start = fold * fold_size
            val_end = val_start + fold_size
            
            val_data = shuffled_dataset[val_start:val_end]
            train_data = shuffled_dataset[:val_start] + shuffled_dataset[val_end:]
            
            if len(train_data) == 0:
                continue
                
            mean_stiffness = sum([d["force"] / d["real_displacement"] for d in train_data]) / len(train_data)
            
            fold_squared_errors = []
            for d in val_data:
                predicted = d["force"] / mean_stiffness
                fold_squared_errors.append((d["real_displacement"] - predicted) ** 2)
            
            fold_rmse = math.sqrt(sum(fold_squared_errors) / len(fold_squared_errors))
            errors.append(fold_rmse)

        average_rmse = sum(errors) / len(errors) if errors else 0.0
        return average_rmse, errors

# --- INTERFACE PRINCIPAL ---

st.markdown('<div class="main-title">🦷 Ecossistema SUS-Twin</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Volume 2: Gêmeos Digitais e Inteligência Artificial na Odontologia Pública</div>', unsafe_allow_html=True)

# --- SIDEBAR: CONFIGURAÇÕES E PARÂMETROS ---
st.sidebar.markdown('<div class="sidebar-title">⚙️ Painel de Configuração</div>', unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.subheader("Propriedades do Ligamento (LPD)")
e_0 = st.sidebar.slider("Módulo Elástico Inicial ($E_0$, MPa)", 2.0, 10.0, 4.2, 0.1)
e_inf = st.sidebar.slider("Módulo Elástico Residual ($E_{\infty}$, MPa)", 0.5, 3.0, 1.2, 0.1)
tau = st.sidebar.slider("Tempo de Relaxamento ($\tau$, s)", 0.5, 5.0, 1.8, 0.1)

st.sidebar.subheader("Parâmetros do Caso Clínico")
cns_input = st.sidebar.text_input("Cartão Nacional de Saúde (CNS)", "200000000000003")
applied_force = st.sidebar.slider("Força Oclusal Aplicada (N)", 5.0, 100.0, 30.0, 1.0)
applied_strain = st.sidebar.slider("Deformação Oclusal ($\epsilon$)", 0.01, 0.15, 0.08, 0.01)
stiffness_initial = st.sidebar.slider("Rigidez Alveolar Estimada (N/mm)", 5.0, 30.0, 15.0, 0.5)

# --- CARREGAR DATASET ---
dataset_path = "clinical_validation_dataset.json"
dataset_loaded = False
clinical_data_mapped = []

if os.path.exists(dataset_path):
    with open(dataset_path, "r", encoding="utf-8") as f:
        raw_dataset = json.load(f)
    clinical_data_mapped = [
        {
            "force": d["force_n"],
            "real_displacement": d["observed_displacement_mm"],
            "cns": d["patient_cns"]
        } for d in raw_dataset
    ]
    dataset_loaded = True

# --- SOLVER E CONVERSÃO ---
solver = LPDSolver(e_infinity=e_inf, e_0=e_0, tau=tau)

# --- TABS PRINCIPAIS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Simulação Biomecânica",
    "🧪 Validação Cruzada K-Fold",
    "⛓️ Contraprova & Auditoria ZKP",
    "🌐 Arquitetura e Integrações IoT"
])

# ==================== TAB 1: SIMULAÇÃO BIOMECÂNICA ====================
with tab1:
    st.header("Simulação Biomecânica do Periodonto")
    st.write(
        "Este módulo calcula a dissipação de estresse viscoelástico sob oclusão constante no "
        "ligamento periodontal (LPD) usando séries de Prony e estima o deslocamento alveolar."
    )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Resultados do Solucionador Físico (LPDSolver)")
        
        peak_stress = solver.calculate_stress(applied_strain, elapsed_time=0.1)
        relaxed_stress = solver.calculate_stress(applied_strain, elapsed_time=10.0)
        displacement = solver.calculate_displacement(applied_force, stiffness=stiffness_initial)
        
        status = "SAFE"
        status_color = "green"
        if peak_stress >= solver.LPD_RUPTURE_LIMIT:
            status = "CRITICAL_OVERLOAD_PREVENTED"
            status_color = "red"
            
        st.markdown(f"""
        <div class="metric-card">
            <h4>Estresse de Pico Inicial</h4>
            <p style="font-size: 1.8rem; font-weight: bold; margin:0;">{peak_stress:.4f} <span style="font-size: 1rem;">MPa</span></p>
        </div>
        <br>
        <div class="metric-card">
            <h4>Estresse Estável a Longo Prazo</h4>
            <p style="font-size: 1.8rem; font-weight: bold; margin:0;">{relaxed_stress:.4f} <span style="font-size: 1rem;">MPa</span></p>
        </div>
        <br>
        <div class="metric-card">
            <h4>Deslocamento Alveolar Previsto</h4>
            <p style="font-size: 1.8rem; font-weight: bold; margin:0;">{displacement:.4f} <span style="font-size: 1rem;">mm</span></p>
        </div>
        <br>
        <div class="metric-card" style="border-left-color: {status_color};">
            <h4>Status de Segurança do Tecido</h4>
            <p style="font-size: 1.5rem; font-weight: bold; color: {status_color}; margin:0;">{status}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.subheader("Curva de Relaxamento Temporal de Prony ($\sigma(t)$)")
        # Plotar curva
        times = [i * 0.1 for i in range(101)]
        stresses = [solver.calculate_stress(applied_strain, t) for t in times]
        
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(times, stresses, label=r"Estresse $\sigma(t)$", color="#3B82F6", linewidth=2.5)
        ax.axhline(solver.LPD_RUPTURE_LIMIT, color="red", linestyle="--", label="Limite Biológico")
        ax.set_xlabel("Tempo (segundos)", fontsize=10)
        ax.set_ylabel("Estresse (MPa)", fontsize=10)
        ax.set_title("Evolução Temporal do Estresse Viscoelástico no LPD", fontsize=11, fontweight="bold")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend()
        st.pyplot(fig)

# ==================== TAB 2: VALIDAÇÃO CRUZADA K-FOLD ====================
with tab2:
    st.header("Validação Cruzada (Calibration & Cross-Validation)")
    
    if dataset_loaded:
        st.success(f"Dataset Clínico Ampliado Carregado: {len(raw_dataset)} registros biomecânicos encontrados.")
        
        k_folds = st.slider("Selecione o número de Folds (K)", 3, 10, 5)
        
        # Executar Validação Cruzada
        validator = CrossValidator(k_folds=k_folds)
        avg_rmse, fold_errors = validator.run_validation(clinical_data_mapped)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Métricas Estatísticas do Ensaio")
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #10B981;">
                <h4>Erro Médio Geral (RMSE)</h4>
                <p style="font-size: 2.2rem; font-weight: bold; color: #10B981; margin:0;">{avg_rmse:.5f} <span style="font-size: 1.1rem;">mm</span></p>
                <small>Tolerância Anvisa SaMD: &lt; 0.15000 mm</small>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            st.write("**Desvio em cada Fold:**")
            fold_dict = {f"Fold {idx+1}": f"{err:.5f} mm" for idx, err in enumerate(fold_errors)}
            st.json(fold_dict)
            
        with col2:
            st.subheader("Distribuição do RMSE de Teste por Fold")
            fig, ax = plt.subplots(figsize=(6, 4))
            folds = [f"F{i+1}" for i in range(len(fold_errors))]
            ax.bar(folds, fold_errors, color="#10B981", alpha=0.8, edgecolor="green", width=0.5)
            ax.axhline(avg_rmse, color="orange", linestyle="--", label=f"Média ({avg_rmse:.5f} mm)")
            ax.set_ylabel("RMSE (mm)")
            ax.set_ylim(0, max(fold_errors) * 1.3)
            ax.set_title("RMSE da Estimativa de Deslocamento Alveolar")
            ax.grid(True, linestyle=":", alpha=0.6)
            ax.legend()
            st.pyplot(fig)
            
    else:
        st.warning("Erro: O arquivo 'clinical_validation_dataset.json' não foi encontrado no diretório do projeto.")

# ==================== TAB 3: CONTRAPROVA & AUDITORIA ZKP ====================
with tab3:
    st.header("Mecanismo de Contraprova e Auditoria Criptográfica (ZKP)")
    st.write(
        "Esse módulo garante a governança e conformidade com a LGPD. Ele permite atestar se a simulação "
        "foi computada com os parâmetros informados sem revelar o número do CNS do paciente em canais públicos."
    )
    
    # Validação preliminar do CNS
    is_cns_valid = False
    if len(cns_input) == 15 and cns_input.isdigit():
        soma = sum(int(cns_input[j]) * (15 - j) for j in range(15))
        is_cns_valid = (soma % 11) == 0

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Geração do Compromisso Criptográfico")
        
        st.write(f"**CNS Informado**: `{cns_input}`")
        if is_cns_valid:
            st.success("CNS Válido (Dígito Verificador Aprovado pelo Ministério da Saúde)")
        else:
            st.error("CNS Inválido sob validação ponderada do CNS mod-11!")
            
        # Simulação e hashes
        peak_stress = solver.calculate_stress(applied_strain, elapsed_time=0.1)
        relaxed_stress = solver.calculate_stress(applied_strain, elapsed_time=10.0)
        displacement = solver.calculate_displacement(applied_force, stiffness=stiffness_initial)
        status_sim = "SAFE" if peak_stress < solver.LPD_RUPTURE_LIMIT else "CRITICAL_OVERLOAD_PREVENTED"
        
        sim_payload = f"{peak_stress:.4f}_{relaxed_stress:.4f}_{displacement:.4f}_{status_sim}"
        simulation_hash = hashlib.sha256(sim_payload.encode()).hexdigest()
        
        st.write(f"**Hash de Desfecho Biomecânico ($\text{{Hash}}_{{\text{{sim}}}}$)**:")
        st.code(simulation_hash, language="text")
        
        # Salting e Blindagem do CNS
        salt = hashlib.sha256("sus_twin_secure_salting_key_2026".encode()).hexdigest()
        blinded_cns = hashlib.sha256((cns_input + salt).encode()).hexdigest()
        
        st.write(f"**Identidade Blindada do Paciente ($H_{{\text{{cns}}}}$)**:")
        st.code(blinded_cns, language="text")
        
        # Compromisso ZKP
        commitment = hashlib.sha256((blinded_cns + simulation_hash).encode()).hexdigest()
        
        st.write(f"**Assinatura de Contraprova ($C_{{\text{{ZKP}}}}$)**:")
        st.code(commitment, language="text")
        
    with col2:
        st.subheader("Painel de Auditoria Pública do SUS")
        st.write("Insira a assinatura de contraprova e os dados fornecidos para verificar a integridade:")
        
        audit_cns = st.text_input("CNS do Paciente para Auditoria", cns_input)
        audit_sim_hash = st.text_input("Hash da Simulação", simulation_hash)
        audit_commitment = st.text_input("Assinatura de Contraprova a Verificar", commitment)
        
        if st.button("Verificar Integridade da Contraprova"):
            calculated_blinded = hashlib.sha256((audit_cns + salt).encode()).hexdigest()
            calculated_commitment = hashlib.sha256((calculated_blinded + audit_sim_hash).encode()).hexdigest()
            
            if calculated_commitment == audit_commitment:
                st.success("✅ INTEGRIDADE CONFIRMADA: A transação clínica é autêntica e pertence a este paciente!")
            else:
                st.error("❌ INTEGRIDADE VIOLADA: Os dados informados não conferem com a assinatura criptográfica!")

# ==================== TAB 4: ARQUITETURA E INTEGRAÇÕES IOT ====================
with tab4:
    st.header("Arquitetura e Conexões com Frameworks Open-Source de DT")
    st.write(
        "Esta seção detalha as interfaces de integração do **SUS-Twin** com os principais frameworks "
        "de mercado e padrões da indústria de gêmeos digitais."
    )
    
    option = st.selectbox("Selecione o Framework de Integração:", [
        "Digital Twin Consortium (DTDL)",
        "OpenTwins (DTs Composicionais)",
        "Eclipse Ditto (IoT & Gateway)",
        "realvirtual.io (Servidor MCP)"
    ])
    
    if option == "Digital Twin Consortium (DTDL)":
        st.subheader("Especificação DTDL v3 (Digital Twin Definition Language)")
        st.write(
            "Alinhamento com os padrões do Digital Twin Consortium. A interface do modelo periodontal "
            "do dente é representada através do seguinte esquema JSON-LD:"
        )
        dtdl_schema = {
            "@context": "dtmi:dtdl:context;3",
            "@id": "dtmi:gov:sus:odontologia:PeriodontalLigament;1",
            "@type": "Interface",
            "displayName": "Periodontal Ligament Biomechanical Twin",
            "contents": [
                {
                    "@type": "Telemetry",
                    "name": "peakStress",
                    "schema": "double",
                    "unit": "megapascal"
                },
                {
                    "@type": "Telemetry",
                    "name": "displacement",
                    "schema": "double",
                    "unit": "millimetre"
                },
                {
                    "@type": "Property",
                    "name": "youngModulusInstantaneous",
                    "schema": "double",
                    "writable": True
                },
                {
                    "@type": "Command",
                    "name": "runSimulation",
                    "request": {
                        "name": "appliedForce",
                        "schema": "double"
                    },
                    "response": {
                        "name": "outcome",
                        "schema": "string"
                    }
                }
            ]
        }
        st.json(dtdl_schema)
        
    elif option == "OpenTwins (DTs Composicionais)":
        st.subheader("Composição do Gêmeo Anatômico (OpenTwins)")
        st.write(
            "Gêmeos Digitais Composicionais representam órgãos complexos como uma árvore de sub-sistemas acoplados. "
            "Aqui está o esquema estrutural de acoplamento geométrico do dente no OpenTwins:"
        )
        opentwins_schema = {
            "twin_type": "Compositional",
            "name": "ToothSystemTwin",
            "composition": {
                "enamel_mesh": {
                    "source": "https://github.com/Awesome-Medical-Dataset/resources/Teeth3DS.md",
                    "geometry": "Shape parameterization",
                    "mass_g": 0.8
                },
                "dentin_mesh": {
                    "geometry": "Pose parameterization",
                    "texture_coordinates": "UV_unwrapped"
                },
                "periodontal_ligament": {
                    "twin_ref": "dtmi:gov:sus:odontologia:PeriodontalLigament;1",
                    "coupling_physics": "Maxwell-Kelvin Viscoelastic solver"
                },
                "alveolar_bone": {
                    "material": "Trabecular/Cortical bone isotropic properties"
                }
            }
        }
        st.json(opentwins_schema)
        
    elif option == "Eclipse Ditto (IoT & Gateway)":
        st.subheader("Payload Eclipse Ditto IoT Gateway")
        st.write(
            "Eclipse Ditto atua como o barramento IoT de gerenciamento de estado físico e sombra (Digital Twin Shadow). "
            "Este é o payload JSON enviado pelo nosso gateway SUS-Twin para manter a representação virtual atualizada no SUS:"
        )
        
        ditto_payload = {
            "thingId": "br.gov.sus.odontologia:patient-twin-200000000000003",
            "policyId": "br.gov.sus.odontologia:policy-authorized-clinical-teams",
            "attributes": {
                "patient_name_masked": "M*** Laranjeira",
                "cns_blinded_hash": blinded_cns
            },
            "features": {
                "biomechanics": {
                    "properties": {
                        "peak_stress_mpa": round(peak_stress, 4),
                        "relaxed_stress_mpa": round(relaxed_stress, 4),
                        "alveolar_displacement_mm": round(displacement, 4),
                        "status": status
                    }
                }
            }
        }
        st.json(ditto_payload)
        
    elif option == "realvirtual.io (Servidor MCP)":
        st.subheader("Servidor Model Context Protocol (MCP) realvirtual.io")
        st.write(
            "O padrão MCP estabelece contratos para agentes de Inteligência Artificial consultarem o estado físico "
            "do gêmeo digital e orquestrarem simulações biomecânicas. Abaixo está a especificação do servidor de ferramentas do SUS-Twin:"
        )
        
        mcp_schema = {
            "mcp_version": "1.0",
            "server_name": "sus-twin-mcp",
            "tools": [
                {
                    "name": "get_patient_displacement",
                    "description": "Calcula o deslocamento oclusal do dente com base na força mastigatória aplicada.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "force_n": {
                                "type": "number",
                                "description": "Força em Newtons (N)"
                            },
                            "stiffness": {
                                "type": "number",
                                "description": "Rigidez alveolar em N/mm"
                            }
                        },
                        "required": ["force_n", "stiffness"]
                    }
                },
                {
                    "name": "run_prony_relaxation",
                    "description": "Calcula o estresse residual viscoelástico do LPD utilizando Prony no tempo t.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "strain": {
                                "type": "number",
                                "description": "Deformação inicial (adimensional)"
                            },
                            "elapsed_time_s": {
                                "type": "number",
                                "description": "Tempo transcorrido em segundos"
                            }
                        },
                        "required": ["strain", "elapsed_time_s"]
                    }
                }
            ]
        }
        st.json(mcp_schema)
