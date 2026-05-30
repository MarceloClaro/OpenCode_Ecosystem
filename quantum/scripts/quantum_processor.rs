use std::f64::consts::PI;

/// Representa um estado quântico simplificado para processamento pesado.
struct QuantumState {
    amplitudes: Vec<(f64, f64)>, // (real, imag)
}

impl QuantumState {
    fn new(n_qubits: u32) -> Self {
        let size = 2_usize.pow(n_qubits);
        let mut amplitudes = vec![(0.0, 0.0); size];
        amplitudes[0] = (1.0, 0.0); // Estado inicial |0...0>
        QuantumState { amplitudes }
    }

    /// Aplica uma rotação de fase em paralelo (conceitual).
    fn apply_phase_shift(&mut self, phi: f64) {
        for amp in self.amplitudes.iter_mut() {
            let (r, i) = *amp;
            let cos_phi = phi.cos();
            let sin_phi = phi.sin();
            *amp = (r * cos_phi - i * sin_phi, r * sin_phi + i * cos_phi);
        }
    }

    /// Calcula a fidelidade entre dois estados (simplificado).
    fn calculate_fidelity(&self, other: &QuantumState) -> f64 {
        let mut sum_re = 0.0;
        let mut sum_im = 0.0;
        for (a, b) in self.amplitudes.iter().zip(other.amplitudes.iter()) {
            sum_re += a.0 * b.0 + a.1 * b.1;
            sum_im += a.0 * b.1 - a.1 * b.0;
        }
        sum_re * sum_re + sum_im * sum_im
    }
}

fn main() {
    let n_qubits = 10;
    println!("Iniciando processamento quântico de alta performance em Rust para {} qubits...", n_qubits);
    
    let mut state1 = QuantumState::new(n_qubits);
    let mut state2 = QuantumState::new(n_qubits);
    
    state1.apply_phase_shift(PI / 4.0);
    state2.apply_phase_shift(PI / 4.01);
    
    let fidelity = state1.calculate_fidelity(&state2);
    println!("Processamento concluído com sucesso!");
    println!("Fidelidade calculada: {:.6}", fidelity);
}
