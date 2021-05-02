# PRNG with Pseudo Quantum Error
# 2021 Â© Aaron Campbell


from os import environ
import math
from qiskit import *
from qiskit.tools.monitor import job_monitor
from qiskit.tools.visualization import plot_histogram
from qiskit.providers.ibmq import least_busy


#IBM setup
if environ.get("FLASK_ENV") == "production":
    ibm_token = environ.get("IBM_TOKEN") # TODO: test whether .env is compiled into --onefile
    IBMQ.enable_account(ibm_token)
else:
    IBMQ.load_account()


def generate_seeds():
    #
    # Global var definitions
    #

    starting_seed = 12345
    number_of_seeds = 20
    # number_of_qbits = 4 # this value depends ont the hardware used. 4 is a safe value
    max_number_of_digits = 3 # ideally no more than 6
    # multiplier
    a = 1664525
    # increment
    c = 1013904223
    # modulus
    m = math.pow(2,32)

    provider = IBMQ.get_provider('ibm-q')
    qcomp = least_busy(provider.backends(simulator=False, operational=True))
    number_of_qbits = len(qcomp.properties().qubits)
    print(f"Using a qcomp with {number_of_qbits} qubits")
    # set up the quantum circuit
    qr = QuantumRegister(number_of_qbits)
    cr = ClassicalRegister(number_of_qbits)
    circuit = QuantumCircuit(qr,cr)

    # put the first qbit into a superposition
    circuit.h(qr[0])
    # define the second qbits value based on the first's
    for i in range(number_of_qbits-1):
        circuit.cx(qr[0],qr[i+1])
    # prepare to measure the state of the circuit
    circuit.measure(qr,cr)

    # run the job and produce a list of cuttoff percentages
    job = execute(circuit, backend=qcomp)
    job_monitor(job)
    results = job.result().get_counts(circuit)
    # plot_histogram(results)

    # creates a list "counts" with the form [a,b,c,d] which represents the dictionary
    # ['00': a*1000, '01': b*1000, '10': c*1000, '11': d*1000]
    # where each key represents the pair of qbits
    # this is used later as a cuttoff frequency to determin if the value of a bit
    # would be switched by this circuit (based on the decimal portion of the seed)
    counts = [*results.values()]
    counts_list = [counts[:len(counts)//2],counts[len(counts)//2:]]
    for val in counts_list:
        for i in range(len(val)-1):
            val[i+1] += val[i]
        for i in range(len(val)):
            val[i] /= val[len(val)-1]
    print("counts: ".format(counts_list))

    #
    # NOTE: do not proceed until you see "Job Status: job has successfully run" below and see the value of counts
    #

    #
    # Function definitions
    #

    # convert a base 10 int to its binary representation as a string
    def decimalToBinary(n):
        return bin(n).replace("0b", "")

    # convert a binary string into its base 10 representation as an int
    def binaryToDecimal(n):
        return int(n,2)

    # takes 2 parameters:
    #    v: single binary digit as a string
    #    f: float value < 0
    # returns a single binary digit as a string which has been changed based on the cuttoffs in the count list based on the float value
    def quantumError(v,f):
        index = 0
        current_counts = counts_list[int(v,10)]
        for i in range(len(current_counts)):
            if(f>current_counts[i]):
                index+=1
        if(v=='1'):
            return "{:d}".format(index%2)
        else:
            return "{:d}".format(index%2)

    # given a float n, returns the float with the part of the value > 0 affected by the quantum circuit
    def magic(n):
        n_s = [*decimalToBinary(int(n))]
        # print("\nclassical_seed_binary:\t\t\t{:s}".format(''.join(n_s)))
        f = toBoundsFloat(n)-int(toBoundsFloat(n))
        for i in range(len(n_s)):
            n_s[i] = quantumError(n_s[i],f)
            f*=100
            f-=int(f)
        # print("seed_after_simulated_quantum_error:\t{:s}".format(''.join(n_s)))
        return binaryToDecimal(''.join(n_s)) + n-int(n)

    # returns the next seed according to the Linear Congruent Classic PRNG
    def newSeed(seed):
        ret = (a * seed + c) % m
    #     print("classically_generated_seed = {:f}".format(ret))
        ret_dec = ret-int(ret)
        ret = magic(ret/100)*100 + ret_dec
    #     print("seed_after_simulated_quantum_error = {:f}".format(ret))
        return ret

    # scales seed to be within the predefined bounds for a seed
    def toBoundsFloat(seed):
        return seed / m * int("9"*max_number_of_digits)

    #
    # Seed generation
    #

    # initialize the starting value
    seed = starting_seed

    # print the desired number of seeds
    seeds = []
    for i in range(number_of_seeds):
        seed = newSeed(seed)
        seeds.append(int(toBoundsFloat(seed)))
    return seeds
