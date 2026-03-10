import numpy as np
import leak_sim.simulate as sim
import h5py
import matplotlib.pyplot as plt

def byte_correlation(inputs, traces):
    # iterate over all the 256 values that a key byte can take
    trace_len = traces.shape[1]
    dist = np.zeros((256, trace_len))
    for key_guess in range(256):
        # calculate the target
        ark = np.bitwise_xor(inputs, key_guess)
        sb = sim.sbox(ark)
        # apply a Hamming weight leakage model
        #pred_leak = sim.HW8[sb]
        #pred_leak = getLSB(sb)
        pred_leak = sim.HW8[ark]
        chunksize = 50
        for chunk in range(0, trace_len, chunksize):
            cor = np.corrcoef(pred_leak.T, traces[:, chunk:chunk+chunksize], rowvar=False)
            dist[key_guess, chunk:chunk+chunksize] = cor[0, 1:]
    return dist

def TaskA():
    # fix a key (default is the one from FIPS 197)
    # determine how many traces should be generated
    # and produce inputs for the simulation
    print(f"[+] Processing Task A.")
    save_data =1
    rk=[0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6, 0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c]
    num_traces =30000
    rng = np.random.default_rng()
    inputs= rng.integers(low=0, high=256, size=[num_traces, 16])

    # determine the length of a trace by running the simulator over a single input
    single = sim.simulate_partial_AES_round(inputs[0,:], rk)
    traces = np.empty([num_traces, single.trace.size])
    len_traces = single.trace.size
    for i in range(0,num_traces):
        tr = sim.simulate_partial_AES_round(inputs[i,:], rk)
        traces[i, :]=tr.trace

    # if you wish to save your dataset for future/repeat analysis then use this piece of code
    if (save_data):
        f = h5py.File("TaskA.h5", "w")
        f.create_dataset("inputs", data= inputs)
        f.create_dataset("traces", data =traces)
        f.create_dataset("keybytes", data = rk)
        print(f"[+] Saving dataset for Task A. It consists of:")
        print(f"[+] {list(f.keys())}.") # display what is in the file Task1.h5
        f.close()

    # an attack on the first key byte using the previously simulated data
    print(f"[+] Correct 0th key byte has value {rk[0]}. ")
    print(f"[+] Running a correlation based attack using {num_traces} differential inputs. ")
    distinguisher_vals = byte_correlation(inputs[:,0], traces)
    # find max value and return as key index
    key_ind = np.unravel_index(np.argmax(np.absolute(distinguisher_vals)), distinguisher_vals.shape)
    print(f"[+] Highest correlation occurs for key {key_ind[0]} at time index {key_ind[1]}.")
    # plot the Corr results
    fig, ax = plt.subplots()
    ax.set_xlabel('Time index')
    ax.set_ylabel('Correlation value')

    x = np.arange(len_traces)
    for i in range(256):
        ax.plot(x, distinguisher_vals[i, :], color='silver')
    ax.plot(x, distinguisher_vals[key_ind[0], :], color='black')
    ax.set_title('Correlation results: best key is {:d},\n correct key is {:d}, using {:d} differential inputs.'.format(key_ind[0], rk[0],num_traces))
    fig.savefig("TaskA.png")

def TaskB():
    # load data from WS1 data set
    print(f"[+] Processing Task B.")
    f = h5py.File('WS1.h5')
    dset = f['WS1Data']
    inputs = np.array(dset[:, 0], dtype='int')
    len_traces = 5000
    traces = dset[:, 1:len_traces+1]
    num_traces = traces.shape[0]

    f.close()

    print(f"[+] Running a correlation based attack using {num_traces} differential inputs. ")
    distinguisher_vals = byte_correlation(inputs, traces)
    # find max value and return as key index
    key_ind = np.unravel_index(np.argmax(np.absolute(distinguisher_vals)), distinguisher_vals.shape)
    print(f"[+] Highest correlation occurs for key {key_ind[0]} at time index {key_ind[1]}.")
    # plot the Corr results
    fig, ax = plt.subplots()
    ax.set_xlabel('Time index')
    ax.set_ylabel('Correlation value')

    x = np.arange(len_traces)
    for i in range(256):
        ax.plot(x, distinguisher_vals[i, :], color='silver')
    ax.plot(x, distinguisher_vals[key_ind[0], :], color='black')
    ax.set_title('Correlation results: best key is {:d},\n correct key is {:d}, using {:d} traces'.format(key_ind[0], 43, num_traces))
    fig.savefig("TaskB.png")



if __name__ == '__main__':

    doTaskA= 0
    doTaskB = 1

    if doTaskA:
        TaskA()

    if doTaskB:
        TaskB()