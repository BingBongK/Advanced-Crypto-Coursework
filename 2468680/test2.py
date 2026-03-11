import numpy as np
import h5py
import leak_sim.simulate as sim


def Correlation(x, y):
    x = x.astype(np.float64)
    y = y.astype(np.float64)

    x = x - np.mean(x)
    y = y - np.mean(y)

    denom = np.sqrt(np.sum(x * x) * np.sum(y * y))
    if denom == 0:
        return 0.0

    return np.sum(x * y) / denom


def AttackOneByte(inputs, traces, byteNum, windowStart, windowEnd):

    state_order = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]
    pt_byte = inputs[:, state_order[byteNum]]
    tw = traces[:, windowStart:windowEnd]

    n_traces, w = tw.shape
    means = np.mean(tw, axis=0)            # mean at each sample across all 2500 traces

    keyScore = np.zeros(256, dtype=np.float64)
    bestPairs = [None] * 256

    #Compare to all possible values and find best one

    for key in range(256):
        x = np.bitwise_xor(pt_byte, key)
        # sbox(x)
        s = sim.sbox(x)
        pred = sim.HW8[np.bitwise_xor(x, s)].astype(np.float64)

        bestCorrelation = 0.0
        bestPair = None

        # try all pairs of points inside the window
        for i in range(w):
            ta = tw[:, i] - means[i]

            for j in range(i + 1, w):
                tb = tw[:, j] - means[j]

                # preprocessing: mean-free product
                z = ta * tb

                c = Correlation(pred, z)

                if abs(c) > abs(bestCorrelation):
                    bestCorrelation = c
                    bestPair = (windowStart + i, windowStart + j)

        keyScore[key] = abs(bestCorrelation)
        bestPairs[key] = bestPair

    best_key = int(np.argmax(keyScore))

    return {
        "byte": byteNum,
        "window": (windowStart, windowEnd),
        "key": best_key,
        "pair": bestPairs[best_key],


    }


def AttackAllBytes(filename, start, end):
    with h5py.File(filename, "r") as f:
        inputs = np.array(f["inputs"], dtype=np.uint8)
        traces = np.array(f["traces"], dtype=np.float64)

    total = end - start
    segment = total // 16

    recovered = []

    for byte in range(16):
        byteStart = start + byte * segment
        byteEnd = start + (byte + 1) * segment

        windowStart = max(0, byteStart)
        windowEnd = min(traces.shape[1], byteEnd)

        result = AttackOneByte(inputs, traces, byte, windowStart, windowEnd)

        best = result["key"]
        recovered.append(best)

        print(
            f"Byte {byte:2d} | "
            f"Window=({windowStart},{windowEnd}) | "
            f"Best=0x{best:02x} | "
            f"Pair={result['pair']}"
        )

    print("\nRecovered bytes:")
    print([f"0x{k:02x}" for k in recovered])

    return recovered


if __name__ == "__main__":
    AttackAllBytes("AT89_masked_cw.h5", 400, 1700)

#Recovered bytes:
#['0x0b', '0x8e', '0x9f', '0x26', '0x74', '0xc5', '0x5c', '0xfc', '0xa5', '0x82', '0xd4', '0xc4', '0xce', '0x48', '0x9b', '0xb4']