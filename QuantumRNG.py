class quantumRNG: 
    """
    For an upper bound defined by x, it picks enough qubits (log base 2 of x, rounded up) and fills all the quantum states from 000 to the maximum required such as
    each quantum state has a probability of 1/sqrt(x), and therefore, the squared sum of all probabilities is 1
    """

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit import transpile
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_histogram, plot_state_city

from sortedcontainers import SortedDict

import math
import argparse
import matplotlib.pyplot as plt

def equal_probability(x):
  return 1/math.sqrt(x)

def fillAmps(amplitudeList,size):
    for x in range(size):
        amplitudeList[x] = equal_probability(size)
    return amplitudeList


parser = argparse.ArgumentParser(description = 'For an upper bound defined by x, it picks enough qubits (log base 2 of x, rounded up) and fills all the quantum states from 000 to the maximum required, and assigns to each meaningful quantum state a probability of 1/sqrt(x), and therefore, the squared sum of all probabilities is 1. The program launches y shots')
parser.add_argument('--shots', nargs='?', const=100, type=int ,help='Amount of shots launched. Must be greater than 0. Default=100')
parser.add_argument('--limit', nargs='?', const=6, type=int, help='Determines the upper bound (included). Must be greater than 1. Default=6, so it needs 3 qubits and prints states from 000 to 101')
parser.add_argument('--memory', nargs='?', const=False, type=bool, help='Determines whether all the shots are shown. Default=False')
parser.add_argument('--histogram', nargs='?', const=False, type=bool, help='Determines if the histogram is printed. Default=False')
args = parser.parse_args()

shots = int(args.shots or 100)
if shots < 1:
  raise Exception("Amount of shots must be positive")

limit = int(args.limit or 6)
if limit < 2:
  raise Exception("Limit must be strictly bigger than one")

memory = bool(args.memory or False)

histogram = bool(args.histogram or False)

print("Shots:",shots,"\tUpper limit:",limit,"\tAverage shots per quantum state expected: ",int(shots/limit))

qubits = int(math.ceil(math.log2(limit)))
listOfAmps = fillAmps([0] * int(math.pow(2,qubits)),limit)
qubitDefinitionList = list(range(qubits))

qc = QuantumCircuit(qubits, qubits)
qc.initialize(listOfAmps, qubitDefinitionList)
qc.measure(qubitDefinitionList, qubitDefinitionList)
qc.save_statevector() 


sim = AerSimulator()
compiled = transpile(qc, sim)
result = sim.run(compiled, shots=shots,memory=True).result() if memory else sim.run(compiled, shots=shots).result()
counts = result.get_counts()
counts = SortedDict(counts)
n = len(qubitDefinitionList)

for i in range(1 << n):
    key = format(i, f"0{n}b")
    count_val = counts.get(key, 0)
    print("|", key, ">\t", count_val)

if(memory == True): print(result.get_memory(qc))

if(histogram == True) :
    plot_histogram(counts, title="State counts")
    plt.show()


