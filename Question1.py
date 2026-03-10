import json
import galois
import numpy

GF = galois.GF(2 ** 8)


def affineShare(x):
    c = a * GF(x) ^ b
    # print(a,b,c)

    return int(c)


def affineAddRoundKey(s, k):
    for i in range(16):
        s[i] = s[i] ^ k[i]
    return s


def affineReconstruct(a, b, c):
    aInverse = GF(a) ** -1
    return int((GF(c) + GF(b)) * aInverse)


with open("test_vectors.txt") as f:
    tests = json.load(f)

for t in tests:
    a = GF(t["a"])
    b = GF(t["b"])
    state = t["state"]
    key = t["key"]
    expected = t["expected"]

    # share state
    c_state = [affineShare(x) for x in state]

    # Reconstruct
    m = [affineReconstruct(a, b, x) for x in c_state]

    # share key
    c_key = [affineShare(x) for x in key]

    # AddRoundKey
    result = affineAddRoundKey(c_state, c_key)

    print("Expected:", expected)
    print("Result:", result)
    print("Match:", result == expected)
    print("Reconstruct:", m == state)
    print()