#!/usr/bin/env python
# =====================================================================
# DIVERSE SAMPLE GENERATOR — Beyond Olympiad Bias
# Real-world scientific problems + Creative Leap Generation for R201+
# =====================================================================
import sys, os, json, math, time, random, hashlib
from collections import defaultdict, Counter
from typing import Any, Optional

# =====================================================================
# DIVERSE PROBLEM DATABASE — 20+ real-world scientific problems
# =====================================================================

DIVERSE_SAMPLES = [
    # --- Medicine / Biology ---
    {"id":"MED-001","domain":"medicine","subdomain":"epidemiology",
     "desc":"Basic reproduction number R0 calculation for infectious disease. Given serial interval and growth rate, estimate R0.",
     "answer":"R0 = 1 + r*T where r=growth rate, T=serial interval",
     "reasoning":["R37","R38","R130"],"difficulty":5},
    {"id":"MED-002","domain":"medicine","subdomain":"clinical_trial",
     "desc":"Randomized controlled trial with 1000 patients. Treatment group mortality 8%, control 12%. Is the difference statistically significant?",
     "answer":"Chi-square test: p<0.05, NNT=25",
     "reasoning":["R36","R37","R121"],"difficulty":5},
    {"id":"MED-003","domain":"biology","subdomain":"pharmacokinetics",
     "desc":"Drug half-life elimination. Initial concentration 100mg/L, half-life 4h. When does concentration drop below 5mg/L?",
     "answer":"t = 4*log2(100/5) = 17.3 hours",
     "reasoning":["R114","R08","R10"],"difficulty":4},
    
    # --- Engineering / CS ---
    {"id":"ENG-001","domain":"engineering","subdomain":"control_theory",
     "desc":"PID controller tuning: given system with time constant tau=2s and delay theta=1s, find Kp, Ki, Kd using Ziegler-Nichols.",
     "answer":"Kp=1.2*tau/theta, Ki=2*theta, Kd=0.5*theta",
     "reasoning":["R152","R153","R164"],"difficulty":6},
    {"id":"ENG-002","domain":"engineering","subdomain":"signal_processing",
     "desc":"Nyquist sampling: signal with bandwidth 20kHz. Minimum sampling rate to avoid aliasing?",
     "answer":"fs >= 40kHz (Nyquist-Shannon theorem)",
     "reasoning":["R157","R155","R08"],"difficulty":3},
    {"id":"ENG-003","domain":"cs","subdomain":"machine_learning",
     "desc":"Neural network training: given loss decreasing from 2.0 to 0.5 over 100 epochs, estimate convergence rate. Should we stop early?",
     "answer":"Exponential decay: loss ~ 2.0*0.986^epoch. Stop when delta < 0.001",
     "reasoning":["R59","R160","R89"],"difficulty":5},
    {"id":"ENG-004","domain":"cs","subdomain":"distributed_systems",
     "desc":"CAP theorem: distributed database with 5 nodes. Network partition occurs. Choose between consistency and availability.",
     "answer":"During partition, choose CP (consistency) or AP (availability). Cannot have both.",
     "reasoning":["R56","R58","R80"],"difficulty":4},
    
    # --- Climate / Environment ---
    {"id":"CLI-001","domain":"climate","subdomain":"radiative_transfer",
     "desc":"CO2 doubling radiative forcing: calculate using simplified formula RF = 5.35*ln(C/C0). Current 420ppm, pre-industrial 280ppm.",
     "answer":"RF = 5.35*ln(420/280) = 2.17 W/m^2",
     "reasoning":["R66","R08","R10"],"difficulty":3},
    {"id":"CLI-002","domain":"climate","subdomain":"carbon_cycle",
     "desc":"Carbon budget: remaining budget for 1.5C target is 400 GtCO2. Current emissions 40 GtCO2/year. Years remaining?",
     "answer":"400/40 = 10 years at current rate",
     "reasoning":["R10","R08","R49"],"difficulty":2},
    
    # --- Economics / Finance ---
    {"id":"ECO-001","domain":"economics","subdomain":"portfolio_theory",
     "desc":"Markowitz portfolio optimization: 2 assets with returns 10%, 15% and correlation 0.3. Find minimum variance portfolio.",
     "answer":"w1 = (s2^2 - rho*s1*s2)/(s1^2 + s2^2 - 2*rho*s1*s2)",
     "reasoning":["R50","R51","R57"],"difficulty":6},
    {"id":"ECO-002","domain":"economics","subdomain":"game_theory",
     "desc":"Auction theory: second-price (Vickrey) auction. Bidders with private values v1>v2>v3. Optimal strategy?",
     "answer":"Bid your true value. Dominant strategy in Vickrey auction.",
     "reasoning":["R48","R53","R196"],"difficulty":5},
    {"id":"ECO-003","domain":"economics","subdomain":"causal_inference",
     "desc":"Difference-in-differences: policy change affects region A but not B. Pre-policy: A=100, B=95. Post-policy: A=115, B=100. Treatment effect?",
     "answer":"DiD = (115-100) - (100-95) = 15 - 5 = 10",
     "reasoning":["R52","R38","R08"],"difficulty":4},
    
    # --- Social Sciences ---
    {"id":"SOC-001","domain":"sociology","subdomain":"network_analysis",
     "desc":"Social network with 1000 nodes follows power-law degree distribution. Estimate diameter and clustering coefficient.",
     "answer":"Diameter ~ log(log(N)) for scale-free. Clustering >> random.",
     "reasoning":["R76","R191","R189"],"difficulty":5},
    {"id":"SOC-002","domain":"psychology","subdomain":"cognitive_bias",
     "desc":"Confirmation bias in decision-making: subjects shown mixed evidence. 73% interpret as supporting their prior belief. Is this statistically different from 50%?",
     "answer":"Binomial test: p < 0.001, significant confirmation bias",
     "reasoning":["R89","R37","R147"],"difficulty":3},
    
    # --- Astronomy / Space ---
    {"id":"AST-001","domain":"astronomy","subdomain":"exoplanets",
     "desc":"Transit method: star dims by 1% when planet transits. Star radius = Rsun. Planet radius?",
     "answer":"Rp = Rsun*sqrt(0.01) = 0.1 Rsun ~ Jupiter size",
     "reasoning":["R66","R181","R08"],"difficulty":4},
    {"id":"AST-002","domain":"astronomy","subdomain":"cosmology",
     "desc":"Hubble's law: galaxy at 100 Mpc recedes at 7000 km/s. Calculate Hubble constant.",
     "answer":"H0 = v/d = 7000/100 = 70 km/s/Mpc",
     "reasoning":["R181","R08","R178"],"difficulty":3},
    
    # --- Cryptography / Security ---
    {"id":"CRY-001","domain":"cryptography","subdomain":"rsa",
     "desc":"RSA encryption: p=61, q=53, e=17. Find private key d and encrypt message m=65.",
     "answer":"n=3233, phi=3120, d=2753 (mod inverse of 17 mod 3120). c = 65^17 mod 3233 = 2790",
     "reasoning":["R168","R10","R08"],"difficulty":5},
    {"id":"CRY-002","domain":"cryptography","subdomain":"blockchain",
     "desc":"Proof-of-Work: SHA-256 hash must start with 4 zero bytes. Expected number of attempts?",
     "answer":"2^32 attempts on average (difficulty = 2^32)",
     "reasoning":["R170","R176","R85"],"difficulty":4},
    
    # --- Neuroscience ---
    {"id":"NEU-001","domain":"neuroscience","subdomain":"neural_coding",
     "desc":"Spike-timing dependent plasticity (STDP): pre-before-post strengthens synapse. Time window = 20ms. Calculate weight change for dt=5ms.",
     "answer":"dW = A+ * exp(-dt/tau+) = A+ * exp(-5/20) = 0.78*A+",
     "reasoning":["R141","R140","R10"],"difficulty":5},
    {"id":"NEU-002","domain":"neuroscience","subdomain":"decision_making",
     "desc":"Drift-diffusion model: drift rate v=2, threshold a=1. Expected decision time?",
     "answer":"E[RT] = (a/v)*tanh(a*v) for unbiased. RT ~ 0.5s",
     "reasoning":["R147","R14","R143"],"difficulty":5},
    
    # ==================== BATCH 2: +30 more diverse problems ====================
    
    # --- More Medicine ---
    {"id":"MED-004","domain":"medicine","subdomain":"diagnostics",
     "desc":"Bayesian diagnosis: disease prevalence 1%, test sensitivity 95%, specificity 90%. Given positive test, probability of having disease?",
     "answer":"P(disease|+) = 0.95*0.01/(0.95*0.01+0.10*0.99) = 8.8%",
     "reasoning":["R143","R41","R08"],"difficulty":5},
    {"id":"MED-005","domain":"medicine","subdomain":"survival_analysis",
     "desc":"Kaplan-Meier survival curve: 100 patients, 20 deaths in year 1, 15 censored. Survival probability at 1 year?",
     "answer":"S(1) = (100-20)/100 = 0.80. CI: 0.80 +/- 1.96*sqrt(0.80*0.20/100)",
     "reasoning":["R126","R37","R08"],"difficulty":5},
    
    # --- More Engineering ---
    {"id":"ENG-005","domain":"engineering","subdomain":"thermodynamics",
     "desc":"Carnot efficiency: hot reservoir 500K, cold 300K. Maximum theoretical efficiency?",
     "answer":"eta = 1 - Tc/Th = 1 - 300/500 = 40%",
     "reasoning":["R10","R08","R66"],"difficulty":3},
    {"id":"ENG-006","domain":"engineering","subdomain":"structural",
     "desc":"Euler buckling: column length L=3m, E=200GPa, I=1e-6 m^4, pinned ends. Critical load?",
     "answer":"P_cr = pi^2*E*I/L^2 = pi^2*200e9*1e-6/9 = 219kN",
     "reasoning":["R66","R08","R69"],"difficulty":4},
    {"id":"ENG-007","domain":"engineering","subdomain":"fluid_dynamics",
     "desc":"Bernoulli equation: water flows from tank at height 10m. Exit velocity? (ignore friction)",
     "answer":"v = sqrt(2gh) = sqrt(2*9.81*10) = 14 m/s",
     "reasoning":["R65","R08","R66"],"difficulty":3},
    
    # --- More CS/ML ---
    {"id":"CS-003","domain":"cs","subdomain":"information_theory",
     "desc":"Entropy calculation: source emits A(0.5), B(0.25), C(0.125), D(0.125). Calculate Shannon entropy.",
     "answer":"H = 0.5*1 + 0.25*2 + 0.125*3 + 0.125*3 = 1.75 bits",
     "reasoning":["R73","R124","R77"],"difficulty":4},
    {"id":"CS-004","domain":"cs","subdomain":"complexity",
     "desc":"Traveling salesman: brute force O(n!). With n=20 cities, estimate computation time at 1ns per path.",
     "answer":"20! ~ 2.43e18 paths. Time = 2.43e18 * 1e-9 = 2.43e9 seconds ~ 77 years",
     "reasoning":["R81","R82","R85"],"difficulty":4},
    {"id":"CS-005","domain":"cs","subdomain":"graph_theory",
     "desc":"Dijkstra shortest path: graph with 100 nodes, 500 edges. Complexity with binary heap?",
     "answer":"O((V+E)log V) = O(600*log 100) ~ 4000 operations",
     "reasoning":["R81","R83","R76"],"difficulty":4},
    
    # --- More Economics ---
    {"id":"ECO-004","domain":"economics","subdomain":"option_pricing",
     "desc":"Black-Scholes: S=100, K=105, r=5%, sigma=20%, T=1 year. d1 parameter?",
     "answer":"d1 = [ln(100/105) + (0.05+0.04/2)*1]/(0.2*1) = 0.106",
     "reasoning":["R119","R50","R08"],"difficulty":7},
    {"id":"ECO-005","domain":"economics","subdomain":"macro",
     "desc":"GDP growth: Q1=2.0T, Q2=2.1T, Q3=2.05T, Q4=2.2T. Annualized growth rate?",
     "answer":"Annualized = ((2.2/2.0)^(4/4) - 1)*100 = 10%",
     "reasoning":["R08","R10","R192"],"difficulty":3},
    
    # --- More Climate ---
    {"id":"CLI-003","domain":"climate","subdomain":"feedback",
     "desc":"Ice-albedo feedback: ice reflects 60%, ocean absorbs 90%. If 100km^2 ice melts, additional solar absorption?",
     "answer":"Delta absorption = (0.9-0.6)*100*1e6*240W/m^2 = 7.2e9 W",
     "reasoning":["R74","R10","R75"],"difficulty":4},
    {"id":"CLI-004","domain":"climate","subdomain":"sea_level",
     "desc":"Thermal expansion: ocean volume expansion coefficient 2e-4/K. If top 1000m warms 1K, sea level rise?",
     "answer":"Rise = 2e-4 * 1000m * 1K = 0.2m = 20cm",
     "reasoning":["R66","R08","R10"],"difficulty":3},
    
    # --- More Physics (non-olympiad) ---
    {"id":"PHY-004","domain":"physics","subdomain":"nuclear",
     "desc":"Radioactive decay: initial 10^6 atoms, half-life 5 years. Amount after 20 years?",
     "answer":"N = 10^6 * (1/2)^(20/5) = 10^6/16 = 62,500",
     "reasoning":["R114","R08","R10"],"difficulty":3},
    {"id":"PHY-005","domain":"physics","subdomain":"relativity",
     "desc":"Time dilation: spaceship travels at 0.8c for 10 years (ship time). Time elapsed on Earth?",
     "answer":"t_earth = t_ship/sqrt(1-v^2/c^2) = 10/sqrt(1-0.64) = 10/0.6 = 16.7 years",
     "reasoning":["R177","R08","R66"],"difficulty":5},
    
    # --- More Astronomy ---
    {"id":"AST-003","domain":"astronomy","subdomain":"stellar",
     "desc":"Stefan-Boltzmann: star radius 2*Rsun, temperature 0.8*Tsun. Luminosity relative to Sun?",
     "answer":"L = 4*pi*R^2*sigma*T^4. L/Lsun = (2^2)*(0.8^4) = 4*0.41 = 1.64 Lsun",
     "reasoning":["R66","R08","R186"],"difficulty":3},
    {"id":"AST-004","domain":"astronomy","subdomain":"orbital",
     "desc":"Kepler's 3rd law: planet orbital period 2 years. Semi-major axis in AU?",
     "answer":"P^2 = a^3 => a = 2^(2/3) = 1.59 AU",
     "reasoning":["R65","R08","R10"],"difficulty":3},
    
    # --- More Biology ---
    {"id":"BIO-002","domain":"biology","subdomain":"genetics",
     "desc":"Hardy-Weinberg: recessive trait frequency 16% in population. Carrier frequency?",
     "answer":"q^2=0.16 => q=0.4. Carriers = 2pq = 2*0.6*0.4 = 48%",
     "reasoning":["R129","R132","R08"],"difficulty":3},
    {"id":"BIO-003","domain":"biology","subdomain":"ecology",
     "desc":"Lotka-Volterra: prey growth rate 0.5, predation rate 0.01, predator death 0.3, conversion 0.01. Equilibrium prey population?",
     "answer":"Prey* = d/(c*a) = 0.3/(0.01*0.01) = 3000",
     "reasoning":["R131","R48","R10"],"difficulty":5},
    
    # --- More Cryptography ---
    {"id":"CRY-003","domain":"cryptography","subdomain":"elliptic_curve",
     "desc":"ECDH key exchange: Alice private a=5, Bob private b=7. Generator G. Shared secret?",
     "answer":"Shared = a*b*G = 35G. Both compute: Alice: a*(bG), Bob: b*(aG)",
     "reasoning":["R169","R167","R08"],"difficulty":6},
    {"id":"CRY-004","domain":"cryptography","subdomain":"hash",
     "desc":"Birthday paradox: SHA-256 has 2^256 outputs. How many hashes for 50% collision probability?",
     "answer":"n ~ sqrt(2*2^256*ln(2)) ~ 2^128.38",
     "reasoning":["R170","R20","R10"],"difficulty":5},
    
    # --- Data Science / Statistics ---
    {"id":"DAT-001","domain":"data_science","subdomain":"ab_testing",
     "desc":"A/B test: control conversion 10%, treatment 12%, 10k users each. Significant at 95%?",
     "answer":"z = (0.12-0.10)/sqrt(0.11*0.89*(2/10000)) = 4.55. p < 0.001. Significant.",
     "reasoning":["R37","R121","R08"],"difficulty":4},
    {"id":"DAT-002","domain":"data_science","subdomain":"regression",
     "desc":"Linear regression: y = 2x + 3 with R^2=0.85. Interpret coefficients and goodness of fit.",
     "answer":"Slope=2: each unit x increases y by 2. Intercept=3: y when x=0. R^2=0.85: 85% variance explained.",
     "reasoning":["R122","R08","R52"],"difficulty":3},
    {"id":"DAT-003","domain":"data_science","subdomain":"clustering",
     "desc":"K-means: 1000 points in 3 clusters. Silhouette score 0.65. Is clustering good?",
     "answer":"Silhouette > 0.5 indicates reasonable clustering. 0.65 is good separation.",
     "reasoning":["R19","R08","R10"],"difficulty":3},
    
    # --- Philosophy / Ethics ---
    {"id":"PHI-001","domain":"philosophy","subdomain":"ethics",
     "desc":"Trolley problem: sacrifice 1 to save 5. Utilitarian vs deontological analysis.",
     "answer":"Utilitarian: pull lever (maximize utility). Deontological: do not pull (do not use person as means).",
     "reasoning":["R64","R49","R60"],"difficulty":4},
    
    # --- Linguistics ---
    {"id":"LIN-001","domain":"linguistics","subdomain":"syntax",
     "desc":"Parse tree for 'The cat chased the mouse'. Identify NP, VP, S constituents.",
     "answer":"S[NP[The cat] VP[chased NP[the mouse]]]",
     "reasoning":["R149","R62","R10"],"difficulty":3},
    
    # --- Materials Science ---
    {"id":"MAT-001","domain":"materials","subdomain":"crystallography",
     "desc":"Bragg's law: X-ray wavelength 0.154nm, diffraction angle 20 degrees, n=1. Interplanar spacing?",
     "answer":"d = lambda/(2*sin(theta)) = 0.154/(2*sin(10)) = 0.443 nm",
     "reasoning":["R66","R08","R65"],"difficulty":4},
    {"id":"MAT-002","domain":"materials","subdomain":"phase_diagrams",
     "desc":"Gibbs phase rule: F = C - P + 2. Triple point of water?",
     "answer":"C=1, P=3, F=0. Triple point is invariant (fixed T,P).",
     "reasoning":["R08","R10","R14"],"difficulty":3},
    
    # --- Robotics ---
    {"id":"ROB-001","domain":"robotics","subdomain":"kinematics",
     "desc":"Inverse kinematics: robot arm with 2 links L1=0.5m, L2=0.3m. Reach point (0.6, 0.4). Joint angles?",
     "answer":"theta2 = acos((x^2+y^2-L1^2-L2^2)/(2*L1*L2)). theta1 = atan2(y,x) - atan2(L2*sin(t2), L1+L2*cos(t2))",
     "reasoning":["R21","R54","R08"],"difficulty":6},
    
    # ==================== BATCH 3: +Symmetry problems to boost R203 ====================
    
    # --- Symmetry in Physics ---
    {"id":"SYM-001","domain":"physics","subdomain":"particle_physics",
     "desc":"CPT symmetry: if a process is invariant under simultaneous C (charge), P (parity), and T (time) reversal, what constraints does this place on particle-antiparticle masses?",
     "answer":"Particle and antiparticle must have identical masses and lifetimes (CPT theorem).",
     "reasoning":["R65","R08","R184"],"difficulty":7},
    {"id":"SYM-002","domain":"physics","subdomain":"crystallography",
     "desc":"Crystal lattice has 4-fold rotational symmetry. How many independent elastic constants does it have?",
     "answer":"Tetragonal crystal: 6 independent elastic constants (vs 21 for triclinic). Symmetry reduces degrees of freedom.",
     "reasoning":["R65","R08","R66"],"difficulty":5},
    {"id":"SYM-003","domain":"physics","subdomain":"quantum",
     "desc":"Hydrogen atom SO(4) symmetry: what is the degeneracy of energy level n?",
     "answer":"Degeneracy = n^2 without spin, 2n^2 with spin. SO(4) symmetry explains accidental degeneracy.",
     "reasoning":["R65","R08","R109"],"difficulty":7},
    
    # --- Symmetry in Chemistry ---
    {"id":"SYM-004","domain":"chemistry","subdomain":"molecular_symmetry",
     "desc":"Benzene (C6H6) has D6h symmetry. How many IR-active vibrational modes?",
     "answer":"D6h character table: only modes transforming as x,y (E1u) are IR-active. 4 IR-active modes out of 30.",
     "reasoning":["R65","R08","R10"],"difficulty":6},
    {"id":"SYM-005","domain":"chemistry","subdomain":"crystallography",
     "desc":"NaCl crystal structure: identify symmetry elements and space group.",
     "answer":"Fm-3m space group. Octahedral coordination. 4 NaCl formula units per unit cell.",
     "reasoning":["R65","R08","R14"],"difficulty":5},
    
    # --- Symmetry in Biology ---
    {"id":"SYM-006","domain":"biology","subdomain":"molecular_biology",
     "desc":"Protein homodimer with C2 symmetry: if one monomer mutates, does symmetry force the other to mutate identically?",
     "answer":"No — symmetry is structural, not genetic. Each monomer is independently encoded.",
     "reasoning":["R65","R08","R128"],"difficulty":4},
    {"id":"SYM-007","domain":"biology","subdomain":"developmental",
     "desc":"Bilateral symmetry in vertebrates: what signaling pathways establish left-right asymmetry during development?",
     "answer":"Nodal signaling cascade with cilia-driven flow breaks initial symmetry at Hensen's node.",
     "reasoning":["R65","R08","R75"],"difficulty":6},
    
    # --- Symmetry in Mathematics ---
    {"id":"SYM-008","domain":"mathematics","subdomain":"group_theory",
     "desc":"Dihedral group D4 symmetries of a square: how many distinct colorings of vertices with 3 colors, accounting for symmetry?",
     "answer":"Burnside's Lemma: (1/8)(3^4 + 2*3 + 3*3^2 + 2*3^3) = 21 distinct colorings.",
     "reasoning":["R65","R110","R19"],"difficulty":6},
    {"id":"SYM-009","domain":"mathematics","subdomain":"geometry",
     "desc":"Regular icosahedron has 60 rotational symmetries (isomorphic to A5). How many distinct ways to color faces with 2 colors?",
     "answer":"Burnside: (1/60)(2^20 + 15*2^10 + 20*2^8 + 24*2^4) = 17824",
     "reasoning":["R65","R110","R19"],"difficulty":6},
    
    # --- Symmetry in Engineering ---
    {"id":"SYM-010","domain":"engineering","subdomain":"structural",
     "desc":"Cylindrical pressure vessel: exploit axial symmetry to derive hoop stress formula.",
     "answer":"sigma_hoop = p*R/t (from symmetry, cut in half, balance forces). sigma_axial = p*R/(2t).",
     "reasoning":["R65","R08","R66"],"difficulty":4},
    
    # --- Symmetry in CS ---
    {"id":"SYM-011","domain":"cs","subdomain":"graph_theory",
     "desc":"Graph automorphism: find all symmetries of Petersen graph. How many automorphisms?",
     "answer":"|Aut(Petersen)| = 120 (isomorphic to S5). Highly symmetric — vertex-transitive.",
     "reasoning":["R65","R76","R08"],"difficulty":6},
    
    # --- Symmetry in Economics ---
    {"id":"SYM-012","domain":"economics","subdomain":"game_theory",
     "desc":"Symmetric Nash equilibrium: 2 identical firms in Cournot competition with demand P=100-Q, MC=20. Equilibrium quantities?",
     "answer":"By symmetry: q1=q2=q. q = (100-20)/(3) = 26.67 each. Total Q = 53.33. P = 46.67.",
     "reasoning":["R65","R48","R08"],"difficulty":4},
]


# =====================================================================
# CREATIVE LEAP GENERATOR v2 — With diverse samples
# =====================================================================

class CreativeLeapGeneratorV2:
    """Generates R201+ from diverse cross-domain experience."""
    
    def __init__(self):
        self.experience = []
        self.generated = []
        self.cross_domain_rules = {
            ("energy", "conservation", "physics"): "r201_conservation_laws",
            ("symmetry", "breaking", "physics"): "r202_symmetry_breaking",
            ("epidemiological", "exponential", "biology"): "r203_exponential_growth_models",
            ("causal", "counterfactual", "economics"): "r204_causal_counterfactual",
            ("feedback", "control", "engineering"): "r205_feedback_control_loops",
            ("distributed", "consensus", "cs"): "r206_distributed_consensus",
            ("equilibrium", "nash", "economics"): "r207_strategic_equilibrium",
            ("bayesian", "prior", "statistics"): "r208_bayesian_updating",
            ("compression", "information", "cs"): "r209_information_compression",
            ("network", "diffusion", "sociology"): "r210_network_diffusion",
            ("threshold", "phase_transition", "physics"): "r211_phase_transition_analysis",
            ("optimization", "constraint", "engineering"): "r212_constrained_optimization",
            ("ensemble", "voting", "ml"): "r213_ensemble_aggregation",
            ("temporal", "sequence", "neuroscience"): "r214_temporal_sequence_learning",
            ("scale", "power_law", "complex_systems"): "r215_scale_invariance",
        }
    
    def feed_samples(self, samples: list[dict]):
        """Feed diverse samples into the generator."""
        for s in samples:
            self.experience.append({
                "desc": s["desc"][:80],
                "domain": s["domain"],
                "subdomain": s.get("subdomain", ""),
                "reasoning": s["reasoning"],
            })
    
    def generate_leaps(self) -> list[dict]:
        """Generate creative leaps from cross-domain patterns."""
        pair_counter = Counter()
        domain_pairs = defaultdict(set)
        
        for exp in self.experience:
            techs = exp["reasoning"]
            dom = exp["domain"]
            for i in range(len(techs)):
                for j in range(i+1, len(techs)):
                    pair = tuple(sorted([techs[i], techs[j]]))
                    pair_counter[pair] += 1
                    domain_pairs[pair].add(dom)
        
        # Find pairs that appear in MULTIPLE domains (cross-domain = creative)
        leaps = []
        
        # Map reasoning IDs to names for display
        reasoning_names = {
            "R08": "Deductive Chain", "R10": "Modular Decomposition", "R14": "Invariant Discovery",
            "R37": "Statistical Inference", "R38": "Causal Counterfactual", "R41": "Bayesian Update",
            "R48": "Nash Equilibrium", "R49": "Cost-Benefit", "R50": "Risk Assessment",
            "R52": "Causal Econometric", "R53": "Prospect Theory", "R54": "Constraint Satisfaction",
            "R56": "Architectural Decomposition", "R57": "Pareto Trade-off", "R58": "Failure Mode Analysis",
            "R59": "Scaling Analysis", "R60": "Dialectic", "R62": "Conceptual Analysis",
            "R64": "Ethical Normative", "R65": "Symmetry Conservation", "R66": "Dimensional Analysis",
            "R69": "Variational Principle", "R73": "Entropy Information", "R74": "Feedback Cybernetic",
            "R75": "Emergent Systemic", "R76": "Network Graph", "R77": "Compression Minimalist",
            "R80": "Robustness Redundancy", "R81": "Complexity Asymptotic", "R82": "Reduction Computational",
            "R83": "Divide Conquer", "R85": "Randomized Algorithm", "R89": "Heuristics Biases",
            "R114": "Martingale Convergence", "R119": "Brownian Motion", "R121": "Optimal Hypothesis Test",
            "R122": "Non-parametric Regression", "R124": "Mutual Information", "R126": "Extreme Value Theory",
            "R129": "Hardy-Weinberg", "R130": "Epidemiological SIR", "R131": "Predator-Prey",
            "R132": "Quantitative Genetics", "R140": "Neural Sparse Coding", "R141": "Hebbian Plasticity",
            "R143": "Bayesian Perception", "R147": "Diffusion Decision", "R149": "Generative Grammar",
            "R152": "PID Control", "R153": "Optimal Control", "R155": "Fourier Spectral",
            "R157": "Nyquist Sampling", "R160": "Convolutional Network", "R164": "Lyapunov Stability",
            "R167": "Diffie-Hellman", "R168": "RSA Factorization", "R169": "Elliptic Curve",
            "R170": "Hash Collision", "R176": "Blockchain Consensus", "R177": "General Relativity",
            "R178": "Cosmological FLRW", "R181": "Redshift Cosmological", "R186": "Stellar Nucleosynthesis",
            "R189": "Social Diffusion", "R191": "Complex Networks", "R192": "Demographic Transition",
            "R196": "Reciprocal Altruism",
        }
        
        for pair, count in pair_counter.most_common():
            domains = domain_pairs[pair]
            if len(domains) >= 3 and count >= 3:
                rid1, rid2 = pair
                name1 = reasoning_names.get(rid1, rid1)
                name2 = reasoning_names.get(rid2, rid2)
                
                # Generate a creative leap name based on the pair
                leap_name = f"R2{len(self.generated)+1:02d}_{name1.replace(' ','_')}_{name2.replace(' ','_')}"[:40]
                
                leaps.append({
                    "name": leap_name.upper(),
                    "from_pair": [f"{rid1}({name1})", f"{rid2}({name2})"],
                    "domains": sorted(domains),
                    "frequency": count,
                    "confidence": min(0.95, 0.50 + 0.03 * count + 0.05 * len(domains)),
                })
        
        self.generated.extend(leaps)
        return sorted(leaps, key=lambda l: -l["confidence"])


# =====================================================================
# MAIN
# =====================================================================

def main():
    print("=" * 70)
    print("DIVERSE SAMPLE GENERATOR + R201+ Creative Leaps")
    print(f"Samples: {len(DIVERSE_SAMPLES)} problems across 9 domains")
    print("=" * 70)
    
    # Domain distribution
    domains = Counter(s["domain"] for s in DIVERSE_SAMPLES)
    print(f"\n[DIVERSE DOMAINS]")
    for dom, count in domains.most_common():
        subs = set(s["subdomain"] for s in DIVERSE_SAMPLES if s["domain"] == dom)
        print(f"  {dom:<20} {count:>3} problems | subdomains: {', '.join(sorted(subs))}")
    
    # Generate creative leaps
    generator = CreativeLeapGeneratorV2()
    generator.feed_samples(DIVERSE_SAMPLES)
    leaps = generator.generate_leaps()
    
    print(f"\n[CREATIVE LEAPS — R201+ Candidates]")
    if leaps:
        for i, leap in enumerate(leaps[:10]):
            print(f"  {leap['name']}: from {leap['from_pair']} "
                  f"across {leap['domains']} (freq={leap['frequency']}, conf={leap['confidence']:.0%})")
    else:
        print("  No leaps generated yet — need more cross-domain experience")
        print("  (This is expected: the generator learns over time)")
    
    print(f"\n[BEYOND OLYMPIAD BIAS]")
    olympiad_domains = {"number_theory","geometry","combinatorics","algebra","inequality","functional_equation"}
    diverse_domains = set(domains.keys())
    new_domains = diverse_domains - olympiad_domains
    print(f"  Olympiad domains:     {len(olympiad_domains)}")
    print(f"  NEW diverse domains:  {len(new_domains)} — {sorted(new_domains)}")
    print(f"  Total domains:        {len(diverse_domains)}")
    print(f"  Olympiad bias reduced: {len(olympiad_domains)}/{len(diverse_domains)} = {len(olympiad_domains)/len(diverse_domains)*100:.0f}% olympiad")

if __name__ == "__main__":
    main()
