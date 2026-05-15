import qiskit
import qiskit_nature
import pyscf
import matplotlib
import numpy
import scipy
import pandas


def main():
    print("Environment verification")
    print("------------------------")
    print(f"qiskit: {qiskit.__version__}")
    print(f"qiskit_nature: {qiskit_nature.__version__}")
    print(f"pyscf: {pyscf.__version__}")
    print(f"matplotlib: {matplotlib.__version__}")
    print(f"numpy: {numpy.__version__}")
    print(f"scipy: {scipy.__version__}")
    print(f"pandas: {pandas.__version__}")
    print("Environment verification passed.")


if __name__ == "__main__":
    main()