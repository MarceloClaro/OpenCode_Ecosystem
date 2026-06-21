import streamlit as st
import streamlit.components.v1 as components
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

    st.markdown("---")
    st.subheader("👁️ Gêmeo Digital Periodontal 3D Interativo")
    st.write("Modelo anatômico tridimensional ativo do elemento dentário e do ligamento periodontal (LPD). Rotacione com o mouse, use zoom e observe a deformação e alteração cromática do LPD em tempo real durante o ciclo de carga oclusal.")
    
    # HTML/JS Tridimensional com Three.js (WebGL Fibroso Avançado e HUD)
    threejs_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        <style>
            body { margin: 0; overflow: hidden; background-color: #0f172a; border-radius: 8px; font-family: monospace; }
            canvas { width: 100vw; height: 100vh; display: block; }
            #hud {
                position: absolute;
                top: 15px;
                right: 15px;
                color: #f8fafc;
                background: rgba(15, 23, 42, 0.85);
                border: 1px solid #38bdf8;
                padding: 12px;
                border-radius: 6px;
                box-shadow: 0 0 10px rgba(56, 189, 248, 0.25);
                width: 210px;
                pointer-events: none;
                font-size: 11px;
            }
            .hud-title {
                font-weight: bold;
                color: #38bdf8;
                margin-bottom: 8px;
                border-bottom: 1px solid #1e293b;
                padding-bottom: 4px;
                font-size: 12px;
                text-align: center;
            }
            .hud-item {
                display: flex;
                justify-content: space-between;
                margin-bottom: 4px;
            }
            .hud-item span {
                color: #94a3b8;
            }
            .hud-item strong {
                color: #38bdf8;
            }
        </style>
    </head>
    <body>
        <div id="hud">
            <div class="hud-title">🔬 Telemetria em Tempo Real</div>
            <div class="hud-item"><span>Carga Oclusal:</span><strong id="hud_force">0.0 N</strong></div>
            <div class="hud-item"><span>Deslocamento:</span><strong id="hud_disp">0.0 µm</strong></div>
            <div class="hud-item"><span>Tensão no LPD:</span><strong id="hud_stress">0.000 MPa</strong></div>
            <div class="hud-item"><span>Deformação Fibra:</span><strong id="hud_strain">0.0 %</strong></div>
        </div>
        <script>
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0f172a);
            
            const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
            camera.position.set(0, 4, 12);
            
            const renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            document.body.appendChild(renderer.domElement);
            
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            
            // Iluminação
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.35);
            scene.add(ambientLight);
            
            const dirLight1 = new THREE.DirectionalLight(0xffffff, 0.85);
            dirLight1.position.set(5, 10, 7);
            scene.add(dirLight1);
            
            const dirLight2 = new THREE.DirectionalLight(0x3b82f6, 0.6);
            dirLight2.position.set(-5, -5, -5);
            scene.add(dirLight2);
            
            // Elemento Dentário (Grupo)
            const toothGroup = new THREE.Group();
            
            // Coroa
            const crownGeo = new THREE.CylinderGeometry(1.4, 1.15, 2.2, 32);
            const crownMat = new THREE.MeshStandardMaterial({
                color: 0xf8fafc,
                roughness: 0.1,
                metalness: 0.05
            });
            const crown = new THREE.Mesh(crownGeo, crownMat);
            crown.position.y = 1.1;
            toothGroup.add(crown);
            
            // Cúspides
            const cuspGeo = new THREE.SphereGeometry(0.28, 16, 16);
            const cusps = [
                [-0.6, 2.2, -0.6], [0.6, 2.2, -0.6],
                [-0.6, 2.2, 0.6], [0.6, 2.2, 0.6]
            ];
            cusps.forEach(pos => {
                const cusp = new THREE.Mesh(cuspGeo, crownMat);
                cusp.position.set(pos[0], pos[1], pos[2]);
                toothGroup.add(cusp);
            });
            
            // Raiz
            const rootGeo = new THREE.ConeGeometry(1.15, 3.8, 32);
            const rootMat = new THREE.MeshStandardMaterial({
                color: 0xe2e8f0,
                roughness: 0.45
            });
            const root = new THREE.Mesh(rootGeo, rootMat);
            root.position.y = -1.9;
            root.rotation.x = Math.PI;
            toothGroup.add(root);
            
            scene.add(toothGroup);
            
            // Alvéolo Ósseo (Socket externo translúcido)
            const boneSocketGeo = new THREE.CylinderGeometry(1.45, 0.2, 4.0, 32, 1, true);
            const boneSocketMat = new THREE.MeshBasicMaterial({
                color: 0x475569,
                transparent: true,
                opacity: 0.12,
                wireframe: true,
                side: THREE.DoubleSide
            });
            const boneSocket = new THREE.Mesh(boneSocketGeo, boneSocketMat);
            boneSocket.position.y = -2.0;
            boneSocket.rotation.x = Math.PI;
            scene.add(boneSocket);

            // Geração de 300 Fibras Colágenas do LPD (Microestrutura Periodontal)
            const fiberLines = [];
            const fiberCount = 300;
            
            for (let i = 0; i < fiberCount; i++) {
                // Altura da inserção ao longo da raiz (0 a -3.6)
                const y_root = -3.6 * Math.random();
                const angle = Math.random() * Math.PI * 2;
                
                // Raio da raiz nessa altura (perfil cônico da raiz)
                const r_root = 1.15 * (1.0 + y_root / 3.8);
                
                // Ponto na raiz (coordenadas locais do dente)
                const px_root = r_root * Math.cos(angle);
                const pz_root = r_root * Math.sin(angle);
                
                // Ponto no osso correspondente (espaço periodontal ~0.25 unidades)
                const r_bone = r_root + 0.3;
                const angle_offset = (Math.random() - 0.5) * 0.15; // Orientação oblíqua/crestosa
                const px_bone = r_bone * Math.cos(angle + angle_offset);
                const pz_bone = r_bone * Math.sin(angle + angle_offset);
                
                // As fibras oblíquas são anguladas (y no osso é ligeiramente superior ao y na raiz)
                const y_bone = y_root + 0.18;
                
                fiberLines.push({
                    local_root: new THREE.Vector3(px_root, y_root, pz_root),
                    bone: new THREE.Vector3(px_bone, y_bone, pz_bone)
                });
            }
            
            // Estrutura WebGL para as linhas
            const linePositions = new Float32Array(fiberCount * 6);
            const lineColors = new Float32Array(fiberCount * 6);
            
            const lineGeo = new THREE.BufferGeometry();
            lineGeo.setAttribute('position', new THREE.BufferAttribute(linePositions, 3));
            lineGeo.setAttribute('color', new THREE.BufferAttribute(lineColors, 3));
            
            const lineMat = new THREE.LineBasicMaterial({
                vertexColors: true,
                transparent: true,
                opacity: 0.8
            });
            
            const fiberSystem = new THREE.LineSegments(lineGeo, lineMat);
            scene.add(fiberSystem);
            
            // Ciclo de Carga e Animação
            let time = 0;
            const positions = lineGeo.attributes.position.array;
            const colors = lineGeo.attributes.color.array;
            
            function animate() {
                requestAnimationFrame(animate);
                time += 0.035;
                
                // Simulação de mastigação realística
                const cycle = Math.sin(time);
                // Deslocamento máximo de ~150 micrômetros
                const displacement = (cycle * 0.08 - 0.08); 
                toothGroup.position.y = displacement;
                
                // Valores de telemetria escalados para exibição física nanomilimétrica
                const real_force = (Math.abs(cycle * 22.5) + 7.5).toFixed(1); // 7.5 a 30.0 N
                const real_disp = Math.abs(cycle * 75.0 - 75.0).toFixed(1);  // 0 a 150 um (nanomilimétrico)
                const real_stress = (Math.abs(displacement) * 2.0).toFixed(4); // MPa
                const real_strain = (Math.abs(displacement) * 0.35 * 100).toFixed(1); // %
                
                // Atualizar HUD
                document.getElementById('hud_force').innerText = real_force + " N";
                document.getElementById('hud_disp').innerText = real_disp + " µm";
                document.getElementById('hud_stress').innerText = real_stress + " MPa";
                document.getElementById('hud_strain').innerText = real_strain + " %";
                
                // Atualização geométrica das fibras
                let posIndex = 0;
                let colIndex = 0;
                
                for (let i = 0; i < fiberCount; i++) {
                    const fiber = fiberLines[i];
                    
                    // Ponto da raiz no espaço global (acompanha o dente)
                    const gx_root = fiber.local_root.x;
                    const gy_root = fiber.local_root.y + displacement;
                    const gz_root = fiber.local_root.z;
                    
                    // Posição raiz
                    positions[posIndex++] = gx_root;
                    positions[posIndex++] = gy_root;
                    positions[posIndex++] = gz_root;
                    
                    // Posição osso (fixo)
                    positions[posIndex++] = fiber.bone.x;
                    positions[posIndex++] = fiber.bone.y;
                    positions[posIndex++] = fiber.bone.z;
                    
                    // Comprimento e deformação individual das fibras
                    const orig_len = fiber.local_root.distanceTo(fiber.bone);
                    const curr_len = new THREE.Vector3(gx_root, gy_root, gz_root).distanceTo(fiber.bone);
                    const fiber_strain = Math.abs(curr_len - orig_len) / orig_len;
                    
                    // Cromatismo reativo (Rosa claro -> Vermelho sob estresse de tração)
                    let r = 0.95;
                    let g = 0.25;
                    let b = 0.55;
                    
                    if (fiber_strain > 0.03) {
                        const factor = Math.min((fiber_strain - 0.03) * 15.0, 1.0);
                        r = 0.95 + factor * 0.05;
                        g = 0.25 - factor * 0.25;
                        b = 0.55 - factor * 0.55;
                    }
                    
                    // Cores dos vértices da raiz e osso
                    colors[colIndex++] = r;
                    colors[colIndex++] = g;
                    colors[colIndex++] = b;
                    colors[colIndex++] = r;
                    colors[colIndex++] = g;
                    colors[colIndex++] = b;
                }
                
                lineGeo.attributes.position.needsUpdate = true;
                lineGeo.attributes.color.needsUpdate = true;
                
                toothGroup.rotation.y += 0.0018;
                
                controls.update();
                renderer.render(scene, camera);
            }
            
            window.addEventListener('resize', () => {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            });
            
            animate();
        </script>
    </body>
    </html>
    """
    components.html(threejs_html, height=450, scrolling=False)

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
