import json
import galois
import numpy
import numpy as np

GF = galois.GF(2 ** 8)


def AffineShare(a,b,x):
    c = a * GF(x) ^ b
    # print(a,b,c)

    return int(c)


def AffineAddRoundKey(s, k):
    for i in range(16):
        s[i] = s[i] ^ k[i]
    return s


def AffineReconstruct(a, b, c):
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
    c_state = [AffineShare(a,b,x) for x in state]

    # Reconstruct
    m = [AffineReconstruct(a, b, x) for x in c_state]

    # share key
    c_key = [AffineShare(a,b,x) for x in key]

    # AddRoundKey
    result = AffineAddRoundKey(c_state, c_key)

    print("Expected:", expected)
    print("Result:", result)
    print("Match:", result == expected)
    print("Reconstruct:", m == state)
    print()

#1c

a = GF(5)
b = GF(9)

s = GF(12)
k = GF(7)

# shares
cS = a*s + b
cK = a*k + b

# insecure AddRoundKey
cOut = cS + cK

print("state share:", cS)
print("key share:", cK)
print("AddRoundKey output:", cOut)
print("Expected a*(s XOR k):", a*(s + k))

#Do affine add round key but with a remask of b
def AffineAddRoundKeyRewrite(s, k):
    b2 = GF.Random()

    output = []
    for i in range(16):
        x = GF(s[i]) ^ GF(k[i])
        output.append(int(x + b2))

    return (output, b2)


c_state, b = AffineAddRoundKeyRewrite(c_state, c_key)
print("\n")
print(c_state)


#1d Simulation on leak
#Purpose of adding back a
def OneCARK(s, k, p ):

    x = GF(s) ^ GF(k)
    x+=p

    return x
k = GF.Random() #Key attacker is looking for
print("k:", int(k))
a = GF.Random()
#Leak a
with open("Leak.txt", "w") as f:
    f.write(str(a) + "\n")

state = GF.Random()
#Leak state
with open("Leak.txt", "a") as f:
    f.write(str(state)+ "\n")

#Leak affine share state value
c = AffineShare(a,a,state)
with open("Leak.txt", "a") as f:
    f.write(str(c)+ "\n")

#Leak affine share key value
ks = AffineShare(a,a,k)
with open("Leak.txt", "a") as f:
    f.write(str(ks)+ "\n")

final = OneCARK(c,ks,a)
with open("Leak.txt", "a") as f:
    f.write(str(final))

###Attacker###
#Probe from leaked values (in this case read from txt file) the 1st and 4th leak
with open("Leak.txt", "r") as f:
    lines = f.readlines()

#This gives values of a and (a*(k xor a))
leak1 = GF(int(lines[0].strip()))
leak4 = GF(int(lines[3].strip()))

def Attack (l1, l2):
    l1Inverse = GF(l1) ** -1
    return (l1Inverse * (l2 ^ l1))
print(Attack(leak1,leak4))
