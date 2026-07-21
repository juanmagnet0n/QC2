# Learning log

## 2026-07-21 — H2/STO-3G bond-stretching energy curve (notebook 02)

**What was built**

`notebooks/02_h2_energy_curve.ipynb` extends the H2/STO-3G VQE pipeline from
notebook 01 into a full H-H bond-stretching energy curve. The same
per-geometry pipeline (PySCF driver -> fermionic Hamiltonian -> Jordan-Wigner
mapping -> Hartree-Fock + UCCSD ansatz -> manual SciPy SLSQP VQE loop on a
noiseless statevector -> exact diagonalization reference) was wrapped in a
helper function and run at 13 H-H distances from 0.4 A to 3.0 A. Results
(bond distance, spin orbitals, qubits, Pauli-term count, exact energy, VQE
energy, absolute error, optimized parameters, optimizer success/message,
function-evaluation count) were collected into a pandas table, printed, and
plotted. The comparison plot plus a log-scale absolute-error plot were saved
to `figures/h2_energy_curve.png`.

**What worked**

- The project's `.venv` was missing `qiskit-nature`, `qiskit-algorithms`,
  `pyscf`, and `pandas` even though they're listed in `requirements.txt`;
  installing from `requirements.txt` picked up compatible current versions
  (qiskit-nature 0.8.0, qiskit-algorithms 0.4.0, pyscf 2.14.0) alongside the
  existing qiskit 2.5.0 with no conflicts.
- The notebook ran end-to-end via `jupyter nbconvert --execute` with no
  errors, and the optimizer reported `success=True` at all 13 bond distances.
- One path gotcha: a Jupyter kernel's working directory defaults to the
  notebook's own directory (`notebooks/`), not the repo root, so the figure
  save path had to be `../figures/h2_energy_curve.png` rather than
  `figures/h2_energy_curve.png` for the file to land in the repo-level
  `figures/` directory in normal use.

**What was learned**

The VQE energy tracked the exact diagonalization energy essentially
perfectly across the *entire* curve, not just near equilibrium: absolute
error stayed at the level of floating-point round-off (roughly
2e-16 to 1e-14 Hartree) at every one of the 13 bond distances, with no
growth trend as the bond was stretched. The number of Pauli terms in the
qubit Hamiltonian after Jordan-Wigner mapping was constant at 15 across the
whole grid (qubit count and spin-orbital count are fixed by the basis set,
not the geometry).

This is expected, not a bug: H2/STO-3G has only one occupied and one virtual
spatial orbital, so the only possible correlating excitation is the single
double excitation between them. UCCSD with that one double excitation is
therefore mathematically equivalent to full CI (exact diagonalization) at
*every* geometry for this system, not just at equilibrium. Bond stretching
increases the true amount of static correlation in the wavefunction, but it
doesn't create an approximation gap here because the ansatz already spans
the full relevant Hilbert space.

**What changed / became interesting as the bond stretched**

Nothing changed in the VQE-vs-exact agreement — it stayed exact throughout,
which is itself the interesting/informative result. What *did* change was
the shape of the energy curve itself: a minimum near the equilibrium bond
length (~0.735 A) with correct dissociation-curve behavior toward larger
distances, confirming the pipeline correctly captures how Hartree-Fock
becomes a progressively worse zero-order reference as the bond stretches,
even though UCCSD fully compensates for it in this minimal system.

**Next step**

Move to a molecule with more than one occupied/virtual orbital pair, such as
LiH or H2O, where UCCSD becomes a genuine approximation to full CI rather
than an exact match. That's where bond stretching should start to reveal
real UCCSD error growth as static correlation increases, and where active-space
choices and circuit depth start to matter in a way they don't for H2/STO-3G.
See also `notes/fermion_to_qubit_mapping.md` for concrete Jordan-Wigner
qubit/Pauli-term counts from this system.
