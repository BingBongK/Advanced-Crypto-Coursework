import numpy as np
import h5py
import matplotlib.pyplot as plt


def load_h5_data(filename):
    with h5py.File(filename, "r") as f:
        print("[+] Keys in file:", list(f.keys()))

        inputs = np.array(f["inputs"], dtype=np.uint8)
        traces = np.array(f["traces"], dtype=np.float64)

    print("[+] inputs shape :", inputs.shape)
    print("[+] traces shape :", traces.shape)
    return inputs, traces


def plot_single_trace(traces, trace_idx=0):
    plt.figure(figsize=(12, 4))
    plt.plot(traces[trace_idx])
    plt.xlabel("Time index")
    plt.ylabel("Power")
    plt.title(f"Single power trace (trace {trace_idx})")
    plt.tight_layout()
    plt.show()


def plot_multiple_traces(traces, num_traces=20):
    plt.figure(figsize=(12, 4))
    for i in range(min(num_traces, traces.shape[0])):
        plt.plot(traces[i], alpha=0.6)
    plt.xlabel("Time index")
    plt.ylabel("Power")
    plt.title(f"First {min(num_traces, traces.shape[0])} power traces")
    plt.tight_layout()
    plt.show()


def plot_mean_trace(traces):
    mean_trace = np.mean(traces, axis=0)

    plt.figure(figsize=(12, 4))
    plt.plot(mean_trace, color="black")
    plt.xlabel("Time index")
    plt.ylabel("Average power")
    plt.title("Mean power trace")
    plt.tight_layout()
    plt.show()


def plot_trace_with_byte_regions(traces, base_start=350, base_end=1750):
    """
    Draw one trace and split the main repeated region into 16 approximate byte windows.
    Adjust base_start/base_end if needed.
    """
    trace = traces[0]
    seg_len = (base_end - base_start) // 16

    plt.figure(figsize=(14, 4))
    plt.plot(trace)

    plt.axvline(base_start, color="red", linestyle="--", label="start/end region")
    plt.axvline(base_end, color="red", linestyle="--")

    for i in range(17):
        x = base_start + i * seg_len
        plt.axvline(x, color="gray", alpha=0.4)

    for i in range(16):
        mid = base_start + i * seg_len + seg_len // 2
        plt.text(mid, np.max(trace), str(i), ha="center", va="bottom", fontsize=8)

    plt.xlabel("Time index")
    plt.ylabel("Power")
    plt.title("Single trace with approximate 16 byte regions")
    plt.tight_layout()
    plt.show()


def main():
    filename = "AT89_masked_cw.h5"

    inputs, traces = load_h5_data(filename)

    # Show example values
    print("\n[+] First plaintext block:")
    print(inputs[0])

    print("\n[+] First 20 samples of trace 0:")
    print(traces[0][:20])

    # Plots
    plot_single_trace(traces, trace_idx=0)
    plot_multiple_traces(traces, num_traces=20)
    plot_mean_trace(traces)
    plot_trace_with_byte_regions(traces, base_start=350, base_end=1750)


if __name__ == "__main__":
    main()