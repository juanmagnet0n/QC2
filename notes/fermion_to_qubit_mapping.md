# Fermion-to-qubit mapping notes

## Jordan-Wigner: concrete numbers from H2/STO-3G

Source: `notebooks/01_h2_vqe_qiskit_nature.ipynb` and
`notebooks/02_h2_energy_curve.ipynb`.

H2 in the STO-3G basis has 2 spatial orbitals, i.e. 4 spin orbitals. Jordan-Wigner
maps each spin orbital directly to one qubit, so this system needs exactly
4 qubits with no reduction. This holds at every bond distance tested
(0.4 A to 3.0 A) — the qubit count is set by the basis set size, not the
geometry.

**Fermionic Hamiltonian (second quantization):** 36 terms, built from one-
and two-body integrals over the 4 spin orbitals (single-particle terms like
`+_0 -_0` and two-particle terms like `+_0 +_1 -_1 -_0`).

**After Jordan-Wigner mapping:** 15 Pauli terms, constant across the whole
0.4-3.0 A bond-distance grid in notebook 02 (only the numeric coefficients
change with geometry, not which Pauli strings appear). At the equilibrium
bond length (0.735 A):

```
SparsePauliOp(
    ['IIII', 'IIIZ', 'IIZI', 'IIZZ', 'IZII', 'IZIZ', 'ZIII', 'ZIIZ',
     'YYYY', 'XXYY', 'YYXX', 'XXXX', 'IZZI', 'ZIZI', 'ZZII'],
    coeffs=[-0.81054798, 0.17218393, -0.22575349, 0.12091263,
             0.17218393, 0.16892754, -0.22575349, 0.16614543,
             0.0452328,  0.0452328,  0.0452328,  0.0452328,
             0.16614543, 0.17464343, 0.12091263]
)
```

Notes on this specific example:

- The 8 single-`Z`/`ZZ`/identity terms come from one- and two-body number
  operators (`n_p`, `n_p n_q`); their diagonal-only Pauli strings are a
  direct fingerprint of Jordan-Wigner's occupation-number encoding.
- The 4 equal-coefficient `XXYY`-type terms (`YYYY`, `XXYY`, `YYXX`, `XXXX`,
  all with coefficient 0.0452328) come from the double-excitation term that
  the UCCSD ansatz's single two-qubit-pair excitation directly targets.
- 15 Pauli terms from 36 fermionic terms reflects real cancellation/grouping
  under the mapping, not just a 1:1 term count — expect the ratio between
  fermionic-term count and Pauli-term count to shift for larger active
  spaces.

## Why UCCSD is exact here, at every geometry

H2/STO-3G has exactly one occupied and one virtual spatial orbital, so
UCCSD's only possible excitation is the single double excitation between
them (3 variational parameters total). That single excitation already spans
the full correlation space available in this system, so UCCSD equals full
CI (exact diagonalization) at every bond distance, not only at equilibrium.
Notebook 02 confirms this numerically: absolute VQE error stayed at
floating-point round-off (~1e-16 to ~1e-14 Hartree) across the entire
0.4-3.0 A sweep, with no growth as static correlation increased at longer
bond lengths. This is a property of this specific minimal 2-orbital system,
not a general feature of UCCSD — it will not hold once there is more than
one occupied/virtual orbital pair (e.g. LiH or H2O), which is the planned
next step.

## Open questions / not yet covered

- VQE vs QPE tradeoffs.
- UCCSD vs classical CCSD in more detail (beyond the exact-for-H2 case above).
- Active-space selection for larger molecules.
- Measurement/shot scaling (everything so far has used exact statevector
  expectation values, not sampled measurements).
- Parity or Bravyi-Kitaev mappings, and whether qubit-count reduction
  (e.g. via symmetry tapering) is worth using once systems get bigger than H2.
