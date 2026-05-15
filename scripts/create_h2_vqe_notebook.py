import json
from pathlib import Path

notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# H2/STO-3G VQE with Qiskit Nature\n",
                "\n",
                "Goal: build the complete electronic-structure-to-qubit pipeline for H2 in STO-3G.\n",
                "\n",
                "Pipeline:\n",
                "\n",
                "1. Define molecular geometry and basis.\n",
                "2. Use PySCF through Qiskit Nature to obtain the electronic-structure problem.\n",
                "3. Build the second-quantized fermionic Hamiltonian.\n",
                "4. Map the fermionic Hamiltonian to qubits using Jordan-Wigner.\n",
                "5. Build a Hartree-Fock initial state and UCCSD ansatz.\n",
                "6. Run VQE with a classical optimizer.\n",
                "7. Compare against an exact classical eigensolver reference.\n"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import importlib.metadata as metadata\n",
                "\n",
                "packages = [\n",
                "    'qiskit',\n",
                "    'qiskit-nature',\n",
                "    'qiskit-algorithms',\n",
                "    'pyscf',\n",
                "    'numpy',\n",
                "]\n",
                "\n",
                "for package in packages:\n",
                "    try:\n",
                "        print(f'{package}: {metadata.version(package)}')\n",
                "    except metadata.PackageNotFoundError:\n",
                "        print(f'{package}: NOT INSTALLED')\n"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 1. Define molecule, basis, charge, and spin\n",
                "\n",
                "We start with neutral singlet H2 at a fixed bond distance. This is the smallest useful electronic-structure problem because STO-3G H2 has two spatial orbitals, four spin orbitals, and therefore four Jordan-Wigner qubits before any symmetry reduction."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "from qiskit_nature.second_q.drivers import PySCFDriver\n",
                "from qiskit_nature.units import DistanceUnit\n",
                "\n",
                "bond_length_angstrom = 0.735\n",
                "basis = 'sto3g'\n",
                "\n",
                "driver = PySCFDriver(\n",
                "    atom=f'H 0 0 0; H 0 0 {bond_length_angstrom}',\n",
                "    unit=DistanceUnit.ANGSTROM,\n",
                "    charge=0,\n",
                "    spin=0,\n",
                "    basis=basis,\n",
                ")\n",
                "\n",
                "problem = driver.run()\n",
                "\n",
                "print('Molecule: H2')\n",
                "print(f'Bond length: {bond_length_angstrom} angstrom')\n",
                "print(f'Basis: {basis}')\n",
                "print(f'Charge: {problem.molecule.charge}')\n",
                "print(f'Spin multiplicity parameter, 2S: {problem.molecule.multiplicity - 1}')\n",
                "print(f'Number of spatial orbitals: {problem.num_spatial_orbitals}')\n",
                "print(f'Number of spin orbitals: {2 * problem.num_spatial_orbitals}')\n",
                "print(f'Number of particles, alpha/beta: {problem.num_particles}')\n"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. Build the fermionic Hamiltonian\n",
                "\n",
                "Qiskit Nature represents the electronic Hamiltonian in second quantization. Conceptually, this is the molecular electronic Hamiltonian expressed in creation and annihilation operators over spin orbitals."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "fermionic_op = problem.hamiltonian.second_q_op()\n",
                "\n",
                "print(type(fermionic_op))\n",
                "print(f'Number of fermionic terms: {len(fermionic_op)}')\n",
                "print()\n",
                "print(fermionic_op)\n"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 3. Map fermions to qubits using Jordan-Wigner\n",
                "\n",
                "Jordan-Wigner gives the most direct conceptual mapping: each spin orbital occupation maps to one qubit. For H2/STO-3G, four spin orbitals become four qubits."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "from qiskit_nature.second_q.mappers import JordanWignerMapper\n",
                "\n",
                "mapper = JordanWignerMapper()\n",
                "qubit_op = mapper.map(fermionic_op)\n",
                "\n",
                "print(type(qubit_op))\n",
                "print(f'Number of qubits: {qubit_op.num_qubits}')\n",
                "print(f'Number of Pauli terms: {len(qubit_op)}')\n",
                "print()\n",
                "print(qubit_op)\n"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 4. Classical exact reference\n",
                "\n",
                "For this toy system, we can diagonalize the qubit Hamiltonian exactly. This is not scalable, but it gives a reference energy for checking VQE."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "from qiskit_algorithms.minimum_eigensolvers import NumPyMinimumEigensolver\n",
                "from qiskit_nature.second_q.algorithms import GroundStateEigensolver\n",
                "\n",
                "exact_solver = NumPyMinimumEigensolver()\n",
                "exact_calc = GroundStateEigensolver(mapper, exact_solver)\n",
                "exact_result = exact_calc.solve(problem)\n",
                "\n",
                "exact_energy = float(exact_result.total_energies[0].real)\n",
                "\n",
                "print(exact_result)\n",
                "print()\n",
                "print(f'Exact total ground-state energy: {exact_energy:.12f} Hartree')\n"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 5. Build Hartree-Fock initial state and UCCSD ansatz\n",
                "\n",
                "This is the direct connection to classical quantum chemistry. Classical CCSD applies an exponential cluster operator to a reference determinant. Quantum UCCSD uses a unitary form of the cluster operator, usually starting from a Hartree-Fock reference state."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "from qiskit_nature.second_q.circuit.library import HartreeFock, UCCSD\n",
                "\n",
                "initial_state = HartreeFock(\n",
                "    num_spatial_orbitals=problem.num_spatial_orbitals,\n",
                "    num_particles=problem.num_particles,\n",
                "    qubit_mapper=mapper,\n",
                ")\n",
                "\n",
                "ansatz = UCCSD(\n",
                "    num_spatial_orbitals=problem.num_spatial_orbitals,\n",
                "    num_particles=problem.num_particles,\n",
                "    qubit_mapper=mapper,\n",
                "    initial_state=initial_state,\n",
                ")\n",
                "\n",
                "print(f'Ansatz: {ansatz.__class__.__name__}')\n",
                "print(f'Number of qubits in ansatz: {ansatz.num_qubits}')\n",
                "print(f'Number of variational parameters: {ansatz.num_parameters}')\n",
                "print(f'Circuit depth: {ansatz.decompose().depth()}')\n",
                "\n",
                "ansatz.decompose().draw('text')\n"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 6. Run VQE\n",
                "\n",
                "VQE minimizes the expectation value of the qubit Hamiltonian with respect to ansatz parameters. Here we use a statevector estimator, so this is an ideal noiseless simulation, not a shot-based hardware run."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import numpy as np\n",
                "\n",
                "from qiskit.primitives import StatevectorEstimator\n",
                "from qiskit_algorithms.minimum_eigensolvers import VQE\n",
                "from qiskit_algorithms.optimizers import SLSQP\n",
                "\n",
                "history = []\n",
                "\n",
                "def callback(eval_count, parameters, mean, metadata):\n",
                "    history.append((eval_count, float(mean)))\n",
                "\n",
                "estimator = StatevectorEstimator()\n",
                "optimizer = SLSQP(maxiter=1000, ftol=1e-12)\n",
                "initial_point = np.zeros(ansatz.num_parameters)\n",
                "\n",
                "vqe_solver = VQE(\n",
                "    estimator=estimator,\n",
                "    ansatz=ansatz,\n",
                "    optimizer=optimizer,\n",
                "    initial_point=initial_point,\n",
                "    callback=callback,\n",
                ")\n",
                "\n",
                "vqe_calc = GroundStateEigensolver(mapper, vqe_solver)\n",
                "vqe_result = vqe_calc.solve(problem)\n",
                "\n",
                "vqe_energy = float(vqe_result.total_energies[0].real)\n",
                "error_hartree = vqe_energy - exact_energy\n",
                "\n",
                "print(vqe_result)\n",
                "print()\n",
                "print(f'VQE total ground-state energy: {vqe_energy:.12f} Hartree')\n",
                "print(f'Exact total ground-state energy: {exact_energy:.12f} Hartree')\n",
                "print(f'Error: {error_hartree:.12e} Hartree')\n",
                "print(f'Number of objective evaluations: {len(history)}')\n"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 7. Summary\n",
                "\n",
                "This cell collects the required milestone outputs."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "summary = {\n",
                "    'molecule': 'H2',\n",
                "    'bond_length_angstrom': bond_length_angstrom,\n",
                "    'basis': basis,\n",
                "    'charge': problem.molecule.charge,\n",
                "    'spin_2S': problem.molecule.multiplicity - 1,\n",
                "    'spatial_orbitals': problem.num_spatial_orbitals,\n",
                "    'spin_orbitals': 2 * problem.num_spatial_orbitals,\n",
                "    'particles_alpha_beta': problem.num_particles,\n",
                "    'mapping': mapper.__class__.__name__,\n",
                "    'qubits': qubit_op.num_qubits,\n",
                "    'pauli_terms': len(qubit_op),\n",
                "    'ansatz': ansatz.__class__.__name__,\n",
                "    'ansatz_parameters': ansatz.num_parameters,\n",
                "    'optimizer': optimizer.__class__.__name__,\n",
                "    'classical_reference_energy_hartree': exact_energy,\n",
                "    'vqe_energy_hartree': vqe_energy,\n",
                "    'error_hartree': error_hartree,\n",
                "}\n",
                "\n",
                "for key, value in summary.items():\n",
                "    print(f'{key}: {value}')\n"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Limitations\n",
                "\n",
                "1. This is an ideal statevector simulation, not a hardware calculation.\n",
                "2. No sampling noise is included.\n",
                "3. No device noise, decoherence, readout error, or transpilation constraints are included.\n",
                "4. H2/STO-3G is too small to demonstrate quantum advantage.\n",
                "5. Exact diagonalization is possible here only because the Hilbert space is tiny.\n",
                "6. Jordan-Wigner is conceptually simple but not always the most resource-efficient mapping.\n",
                "7. UCCSD is chemically motivated, but circuit depth becomes a serious issue for larger active spaces."
            ]
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "pygments_lexer": "ipython3"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

path = Path("notebooks/01_h2_vqe_qiskit_nature.ipynb")
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(notebook, indent=2), encoding="utf-8")

print(f"Wrote {path}")
