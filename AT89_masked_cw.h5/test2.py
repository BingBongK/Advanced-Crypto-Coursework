import numpy as np
import h5py
import leak_sim.simulate as sim


def corr_1d(x, y):
    x = x.astype(np.float64)
    y = y.astype(np.float64)

    x = x - np.mean(x)
    y = y - np.mean(y)

    denom = np.sqrt(np.sum(x * x) * np.sum(y * y))
    if denom == 0:
        return 0.0

    return np.sum(x * y) / denom


def recover_one_byte(inputs, traces, byte_idx, window_start, window_end):
    """
    inputs: shape (N,16)
    traces: shape (N,T)
    byte_idx: AES byte index 0..15
    window_start, window_end: trace window for this byte
    """

    state_order = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]
    pt_byte = inputs[:, state_order[byte_idx]]
    #pt_byte = inputs[:, byte_idx]          # shape (N,)
    tw = traces[:, window_start:window_end]  # shape (N,W)

    n_traces, w = tw.shape
    means = np.mean(tw, axis=0)            # mean at each sample across all 2500 traces

    key_scores = np.zeros(256, dtype=np.float64)
    best_pairs = [None] * 256

    for key_guess in range(256):
        # x = plaintext byte xor key guess
        x = np.bitwise_xor(pt_byte, key_guess)

        # sbox(x)
        s = sim.sbox(x)

        # second-order prediction model: HW(x xor S(x))
        pred = sim.HW8[np.bitwise_xor(x, s)].astype(np.float64)

        best_corr_for_key = 0.0
        best_pair_for_key = None

        # try all pairs of points inside the window
        for a in range(w):
            ta = tw[:, a] - means[a]

            for b in range(a + 1, w):
                tb = tw[:, b] - means[b]

                # preprocessing: mean-free product
                z = ta * tb

                c = corr_1d(pred, z)

                if abs(c) > abs(best_corr_for_key):
                    best_corr_for_key = c
                    best_pair_for_key = (window_start + a, window_start + b)

        key_scores[key_guess] = abs(best_corr_for_key)
        best_pairs[key_guess] = best_pair_for_key

    best_key = int(np.argmax(key_scores))
    ranking = np.argsort(-key_scores)

    return {
        "byte_idx": byte_idx,
        "window": (window_start, window_end),
        "best_key": best_key,
        "best_score": float(key_scores[best_key]),
        "best_pair": best_pairs[best_key],
        "ranking": ranking,
        "key_scores": key_scores,
    }


def attack_all_bytes(filename="AT89_masked_cw.h5", start=350, end=1750, margin=10):
    with h5py.File(filename, "r") as f:
        inputs = np.array(f["inputs"], dtype=np.uint8)
        traces = np.array(f["traces"], dtype=np.float64)

    print("inputs shape:", inputs.shape)
    print("traces shape:", traces.shape)

    total_region = end - start
    segment_len = total_region // 16

    recovered = []

    for byte_idx in range(16):
        base_s = start + byte_idx * segment_len
        base_e = start + (byte_idx + 1) * segment_len

        win_s = max(0, base_s - margin)
        win_e = min(traces.shape[1], base_e + margin)

        result = recover_one_byte(inputs, traces, byte_idx, win_s, win_e)

        best = result["best_key"]
        second = int(result["ranking"][1])
        gap = result["key_scores"][best] - result["key_scores"][second]

        recovered.append(best)

        print(
            f"byte {byte_idx:2d} | "
            f"window=({win_s},{win_e}) | "
            f"best=0x{best:02x} score={result['key_scores'][best]:.6f} | "
            f"second=0x{second:02x} score={result['key_scores'][second]:.6f} | "
            f"gap={gap:.6f} | "
            f"pair={result['best_pair']}"
        )

    print("\nRecovered bytes:")
    print([f"0x{k:02x}" for k in recovered])

    return recovered


if __name__ == "__main__":
    attack_all_bytes(filename="AT89_masked_cw.h5", start=350, end=1750, margin=10)