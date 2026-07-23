# UCCSD: Classical vs. Quantum, and Why H2/STO-3G Doesn't Show the Difference

## Direct answer

UCCSD (Unitary Coupled Cluster Singles and Doubles) is the quantum analog of classical CCSD, built on the same excitation operators but exponentiated differently: classical CCSD uses e^T with T non-unitary and truncated, while UCCSD uses e^(T-T dagger) which is exactly unitary by construction. That unitarity is what makes it implementable as a quantum circuit, since quantum gates must be unitary, but it comes at a real cost: the UCCSD wavefunction cannot be evaluated in closed form the way CCSD can, so its energy has to be measured on a quantum computer (or simulated by exponentiating a matrix, which is exact but doesn't scale). For H2 in STO-3G, this whole distinction is invisible in the numbers, because with only 2 electrons in 2 spatial orbitals, both classical CCSD and UCCSD are mathematically exact and reduce to full CI. The interesting differences between the two methods, and the reason UCCSD is worth the trouble, only show up once the system is big enough that CCSD stops being exact and the two methods start disagreeing.

## Why this matters

The H2 bond-stretching curve (Phase 4, `02_h2_energy_curve.ipynb`) showed VQE matching exact diagonalization to machine precision (1e-16 to 1e-14 Ha) at every one of 13 geometries from 0.4 to 3.0 Angstrom, including the stretched region where single-reference methods typically struggle. That result is correct, but it is not evidence that UCCSD handles strong correlation well in general. It is a consequence of the system being too small for the approximation to matter. Understanding why is the difference between reading that flat error curve as "UCCSD works" versus "UCCSD hasn't been tested yet." Phase 5 (LiH or H2O) is where the test actually starts.

## Classical analogy

In classical single-reference coupled cluster theory, CCSD writes the wavefunction as e^T acting on a Hartree-Fock reference, where T = T1 + T2 contains single and double excitation amplitudes. CCSD truncates T at doubles and solves a set of non-linear amplitude equations. For most systems this is an approximation: T3, T4, and higher excitations are dropped, and near a bond-breaking region where static correlation grows, that truncation increasingly fails until CCSD amplitudes can even diverge.

UCCSD keeps the same T1 and T2 excitation operators but exponentiates the antihermitian combination sigma = T - T-dagger instead of T alone. exp(sigma) is unitary for any antihermitian sigma, which is the entire reason this formulation exists: a unitary operator can be built out of quantum gates and applied to a qubit register, while the non-unitary e^T from classical CC cannot. The tradeoff is that e^sigma does not truncate the same way. Even restricted to single and double excitation generators, the Baker-Campbell-Hausdorff expansion of e^sigma contains contributions at all orders when multiplied out, so evaluating the energy in closed form the way classical CCSD does is not tractable. On a real quantum device the state e^sigma times HF-reference is prepared directly by the circuit and the energy is measured, not expanded. In simulation (as in this project so far), the unitary is built as an explicit matrix exponential, which is exact but scales exponentially with system size, the same barrier that makes running this on an actual quantum processor eventually necessary.

Practically: CCSD is a good, well-tested, cheap approximation for most single-reference classical chemistry, exact only in the small-system limit. UCCSD is a formulation designed for the constraint of quantum hardware, unitary rather than a target of accuracy in itself, and only becomes an approximation to full CI once the excitation space it's built from stops spanning the full space.

## Math details

For 2 electrons in 2 spatial orbitals (4 spin orbitals, the H2/STO-3G case), the full CI space has dimension 3 in the singlet sector: the HF determinant, and doubly-excited determinants from each occupied spin orbital pair into the corresponding virtual pair. There is exactly one spatial double excitation available (bonding pair to antibonding pair). UCCSD's T2 operator generates precisely that excitation. So the UCCSD ansatz, HF-reference acted on by e^sigma with sigma built from that single T2 term (plus T1 terms that vanish by symmetry for a closed-shell singlet at the RHF reference), spans the same 2-dimensional variational space that FCI does. There is no truncation error because there is nothing left to truncate. This is why the notebook's 3-parameter ansatz reproduces exact diagonalization to floating-point precision at every bond length: the ansatz and the exact solution live in the same space at every geometry, not just near equilibrium.

For LiH (6 electrons, more virtuals depending on active space) or H2O (10 electrons), the number of possible double (and higher) excitations grows combinatorially, and full CI space grows much faster than the UCCSD ansatz does. UCCSD truncated at singles and doubles then represents a genuine subspace of full CI, not the whole thing, exactly like classical CCSD misses T3 and higher. The gap between UCCSD energy and FCI energy in that regime is a real approximation error, and it is expected to grow as static correlation increases (stretched bonds, near-degenerate configurations), the same failure mode classical CCSD has, inherited because UCCSD is built from the same truncated excitation operators.

## Minimal example

H2/STO-3G at 3.0 Angstrom (near dissociation) from the Phase 4 scan: VQE energy -0.9336318446 Ha versus exact diagonalization at the same value to 10 decimal places. Twice the STO-3G single-hydrogen-atom energy (the true dissociation limit) is close to -0.9332 Ha, so this point is converging toward the correct asymptote from below, consistent with 3.0 Angstrom being close to but not fully at dissociation. If UCCSD were behaving like a truncated approximation here the way classical CCSD does near dissociation, this is exactly where error would appear. It doesn't, because the 2-electron/2-orbital system never leaves the space UCCSD spans.

## What can go wrong

Reading "UCCSD equals FCI to machine precision" on a small toy system as general evidence that UCCSD is highly accurate. It's a statement about this system's dimensionality, not about the method's approximation quality. The failure mode to watch for going into Phase 5: an LiH or H2O result that unexpectedly matches FCI to machine precision at a stretched geometry probably indicates the active space was chosen too small (effectively collapsing back to a 2-electron problem) rather than confirms UCCSD is exact there.

## Questions to investigate

- At what active space size does UCCSD-FCI error become numerically visible (above 1e-6 Ha) for LiH, and does that error grow monotonically with bond stretching the way classical CCSD error does?
- Does freezing the core on LiH change whether UCCSD remains exact, since a frozen-core LiH active space may still be small enough to be exact for the wrong reason?
- How does UCCSD's parameter count scale with active space size compared to classical CCSD's amplitude count, since they are built from the same excitation operators, and where does that make the quantum circuit intractable to simulate classically before it becomes intractable to run on hardware?

## References

Notebook 01 (`01_h2_vqe_qiskit_nature.ipynb`) and Notebook 02 (`02_h2_energy_curve.ipynb`), this repository. Equilibrium and dissociation reference values checked against standard RHF/FCI STO-3G textbook results (Szabo and Ostlund conventions).
