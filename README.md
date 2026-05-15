# quantum-chemistry-on-qubits

A learning and research repository for transitioning from classical ab initio quantum chemistry to quantum computing for molecular simulation.

## Initial goals

1. Set up Git, GitHub, Python, and a clean repository.
2. Build the electronic-structure-to-qubit pipeline:
   geometry -> basis -> integrals -> fermionic Hamiltonian -> qubit mapping -> Pauli strings -> ansatz -> circuit -> measurement -> optimizer -> energy.
3. Run H2/STO-3G VQE first.
4. Extend to the H2 energy curve.
5. Document fermion-to-qubit mappings, VQE vs QPE, UCCSD vs classical CCSD, active spaces, and measurement scaling.

## Repository structure

- notebooks/: Jupyter notebooks for calculations and demonstrations.
- notes/: Conceptual and technical notes.
- scripts/: Reusable Python scripts.
- figures/: Generated plots and diagrams.
- data/: Small generated data files.
- references/: Papers, links, and bibliographic notes.

## First computational milestone

Create a working H2/STO-3G VQE notebook reporting:

- molecule
- basis
- spin orbitals
- qubits
- mapping
- ansatz
- optimizer
- classical reference energy
- VQE energy
- error
- limitations