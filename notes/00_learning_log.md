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

## 2026-07-20 — H2/STO-3G VQE: first end-to-end run

**What I did**

Got `01_h2_vqe_qiskit_nature` running end-to-end: H2 in STO-3G (4 spin
orbitals → 4 qubits), Jordan-Wigner mapping, HF + UCCSD ansatz (3
parameters), noiseless statevector simulation optimized with SciPy
SLSQP. VQE energy agrees with exact diagonalization to ~4e-14 Hartree.

**What I actually learned, not just what ran**

- Jordan-Wigner is bookkeeping, not physics. The physics (which spin
  orbitals are occupied, and the fermionic sign structure that keeps
  the wavefunction antisymmetric) doesn't change. JW just re-expresses
  that structure in a basis of qubit operators, using Z-strings to
  carry the antisymmetry information that used to live implicitly in
  how I ordered a Slater determinant.
- UCCSD on a quantum computer is CCSD's unitary sibling. Classically,
  CCSD's e^T isn't unitary and that's fine — I never needed it to be,
  since I'm just building an energy expectation value classically.
  Quantum gates *must* be unitary, so UCCSD swaps in e^(T−T†). Same
  cluster operator idea, different constraint driving the choice of
  exponential.
- The 4e-14 Ha agreement is not a victory over exact diagonalization —
  it's confirmation the code is wired correctly. With 2 electrons in 2
  spatial orbitals, UCCSD's excitation manifold *is* the full FCI
  space. There's no truncation for it to be inexact about yet. The
  real test of whether this method is doing anything approximate
  starts at LiH/H2O (Phase 5).
- VQE's loop is the classical-quantum handoff I'll need to keep
  straight going forward: state prep on the quantum side, expectation
  value measurement on the quantum side, parameter update on the
  classical side (SLSQP here), repeat. Nothing about the physics
  changes across that loop — it's a different way of finding the same
  ground-state energy I'd get from a classical eigensolver, just with
  the state stored on qubits instead of in a CI vector.

**Where this sits in the bigger picture**

This is the "does the pipeline work" milestone, not the "does the
approximation hold up" milestone. That's Phase 5's job. Phase 4 (bond
stretching) is next — same exact-for-this-system caveat applies, but
it'll be useful for seeing how VQE behaves away from equilibrium
geometry, and as a warm-up for interpreting energy curves before UCCSD
stops being exact.

**Open questions carried forward**

- How much of UCCSD's cost (circuit depth, gate count) scales when
  moving from H2 to LiH — is this something I should benchmark before
  committing to LiH as the Phase 5 target?
- At what system size does JW's qubit overhead (relative to more
  efficient fermion-to-qubit mappings, e.g. Bravyi-Kitaev) start to
  matter in practice?
