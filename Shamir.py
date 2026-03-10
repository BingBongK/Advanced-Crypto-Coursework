import numpy as np
import random
import ast

from sympy.solvers.diophantine.diophantine import reconstruct

# a class or function that implements a client (i.e. including the share function)
# a class or function that implements a server (i.e. aggregation, and reconstruct)
# a class or function that implements the “sending of shares” (by virtue of writing to the file “task1_shares.txt”)
# a class or function that implements a random selection from the parties 2, 3 for reconstruct
# a class or function that triggers reconstruct; i.e. the headquarters gets shares from the selected party, and writes the final result into “task1_sum.txt”.



p = 31
t = 2


class Client:
    #Recieve data from task1_clients
    #Split data into 3 shares

    #Initialise
    def __init__(self, clientID, value):
        self.clientID= clientID
        self.value = value

    def __repr__(self):
        return f"Client(id={self.clientID}, value={self.value})"

    def MakeShares(self):
        a = random.randrange(p)
        #print(a)



        return [(self.value + a*1) % p,
                (self.value + a*2) % p,
                (self.value + a*3) % p
                ]

class Server:

    def __init__(self, partyID):
        self.partyID = partyID
        self.totalShare = 0

    def add_share(self, share):
        self.totalShare = (self.totalShare + share) % p

    def Lagrange(self, b):
        return ((0 - b.partyID) / (self.partyID-b.partyID)% p)

#Read from data file
def read_clients(filename):
    with open(filename, "r") as f:
        data = f.read().strip()

    values = [int(x) for x in data.split(",")]
    clients = []

    for i, value in enumerate(values, start=1):
        clients.append(Client(i, value))

    return clients

def SendShares(clients, filename):

    shareList = []
    #Make shares
    for client in clients:
        shares = client.MakeShares()
        shareList.extend(shares)

    with open(filename, "w") as f:
        f.write(",".join(map(str, shareList)))

def DistributeShares(filename, s1, s2, s3):
    t = 0
    with open(filename, "r") as f:
        shares = list(map(int, f.read().split(",")))

        for i in range(0, len(shares), 3):
            s1.add_share(shares[i])
            s2.add_share(shares[i + 1])
            s3.add_share(shares[i + 2])
            #t += shares[i]
            #print(s1.totalShare, s2.totalShare, s3.totalShare)

def ChooseServer():
    chosen_server = random.choice([server2, server3])
    print("Chosen server:", chosen_server.partyID)
    return chosen_server

# def Lagrange(a,b):
#     print("Lagrange:", a.partyID, b.partyID)
#
#     return ((0-b.partyID) / (a.partyID - b.partyID) % p)

def Reconstruct(filename, s1, s2,l1, l2):
    temp = ((s1.totalShare*l1) + (s2.totalShare*l2)) % p

    # Make shares

    with open(filename, "w") as f:
        f.write(str(temp))



clients = read_clients("task1_clients.txt")
#print(clients)
#Create servers
HQ = Server(1)
server2 = Server(2)
server3 = Server(3)

#Write shares to txt file
SendShares(clients, "task1_shares.txt")

#Distribute shares to each server
DistributeShares("task1_shares.txt", HQ, server2, server3)
print(HQ.totalShare,server2.totalShare,server3.totalShare)

#Choose server
chosenServer = ChooseServer()
#HQ reconstructs with chosen server
print(HQ.Lagrange(chosenServer))
print(chosenServer.Lagrange(HQ))
#reconstruct
#t = Reconstruct(HQ,chosenServer,HQ.Lagrange(chosenServer), chosenServer.Lagrange(HQ))
#print(t)
Reconstruct("task1_sum.txt", HQ,chosenServer,HQ.Lagrange(chosenServer), chosenServer.Lagrange(HQ))