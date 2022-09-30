import itertools
import sys
from collections import OrderedDict


# Method to parse data and parameter file
def parse_data(datapath, mispath):
    T = []
    MIS = {}
    item_counts = {}

    with open(datapath, "r") as f:
        i = 0
        for line in f.readlines():
            item_list = set()
            line = line.strip()
            if len(line) > 0:
                for item in line.split(","):
                    item = item.strip()
                    if len(item) > 0:
                        item = int(item.strip())
                        if item not in MIS.keys():
                            MIS[item] = -1  # Initializing all MIS value with -1
                        if item in item_counts:
                            item_counts[item] += 1
                        else:
                            item_counts[item] = 1
                        item_list.add(item)
            if len(item_list) > 0:
                T.append(item_list)

    rest, SDC = 0, 0

    with open(mispath, "r") as f:
        for line in f.readlines():
            key, value = line.split("=")
            key = key.split("(")[-1].split(")")[0].strip()

            # Parameter files has SDC, min item support for the transactions
            if key == 'SDC':
                SDC = float(value)
            elif key == 'rest':
                rest = float(value)
            else:
                MIS[int(key)] = float(value)

        for item in item_counts.keys():
            if MIS[item] == -1:
                MIS[item] = rest

    # sort keys according to MIS(i) values and maintain in ordered dictionary
    MIS = OrderedDict((x[0], x[1]) for x in sorted(MIS.items(), key=lambda item: item[1]))
    return T, MIS, item_counts, SDC


# Count occurrences of a subset in all the transactions
def compute_count(X, T):
    count = 0
    X = set(X)
    for t in T:
        # t = set(t) #or read data as set of lists
        if X.issubset(t):
            count = count + 1
    return count


# Calculate the support of a subset
def get_support(X, T):
    return compute_count(X, T) / len(T)


# Compute counts for each item and store in ordered dictionary
def init_pass(MS, item_counts, n):
    F = set()
    # prune based on MS
    for item in item_counts:
        if MS[item] <= item_counts[item] / n:
            F.add(item)
    return F


# Method to generate output
def display_output(frequent_items, outfilepath):
    result = ""
    for key, value in frequent_items.items():
        result += f"(Length-{key} {len(value)}\n"
        if key == 1:
            for num in value:
                result += 8 * " " + f"({num})\n"
        else:
            for num in value:
                result += 8 * " " + "(" + " ".join(list(map(str, num))) + ")\n"

        result += ")\n"
    result += "75"
    with open(outfilepath, "w") as f:
        f.write(result)


# Method to generate level-2 candidate sets
def candidate_2_gen(item_counts, MS, T, SDC):
    C = set()  # set of tuples: ordered pairs

    M = list(MS.keys())
    for i in range(len(M)):
        l = M[i]
        if item_counts[l] / len(T) >= MS[l]:
            for h in M[i + 1:]:
                if item_counts[h] / len(T) >= MS[l] and abs(item_counts[h] - item_counts[l]) / len(T) <= SDC:
                    C = C.union({(l, h)})

    # Prune C based on item_counts and MIS, construct frequent two-itemset: F
    F = set()
    if len(C) > 0:
        for c in C:
            if MS[c[0]] <= get_support(c, T):
                F.add(c)
    return F  # set of tuples


# Method to candidate sets for levels > 2
def MScandidate_gen(F, item_counts, MS, T, SDC):
    C = []  # set of ordered n-1 tuples
    M = list(MS.keys())
    # Generate candidate sets
    for f1, f2 in list(itertools.permutations(F, 2)):
        # check if f1 and f2 differ only in the last item f1 = (i1, … , ik-2, ik-1) and f2 = {i1, … , ik-2, i’k-1}
        if f1[:-1] == f2[:-1] and M.index(f1[-1]) <= M.index(f2[-1]) and abs(
                item_counts[f1[-1]] - item_counts[f2[-1]]) / len(T) <= SDC:
            c = f1 + (f2[-1],)  # join the two itemsets f1 and f2
            flag = True
            for j in range(len(c)):
                s = [x for i, x in enumerate(c) if i != j]
                # for s in set(itertools.permutations(c, len(c)-1)): #(k-1) length subset s of c
                if (c[0] in s) or (MS[c[1]] == MS[c[0]]):
                    if tuple(s) not in F:
                        flag = False
                        break
            if flag:
                C.append(c)

    F = set()
    if len(C) > 0:
        # Prune based on MIS and support
        for c in C:
            if MS[c[0]] <= get_support(c, T):
                F.add(c)

    return F


# Method which calculates frequent itemsets based on all the transactions
def MS_Apriori(MS, T, SDC, item_counts):  # MIS stores all I:MIS values as dictionary
    frequent_items = {}
    F = init_pass(MS, item_counts, len(T));
    k = 1
    while len(F) > 0 and k < len(MS):
        frequent_items[k] = F
        k += 1
        if k == 2:
            F = candidate_2_gen(item_counts, MS, T, SDC)  # item_counts, MS, T, SDC
        else:
            F = MScandidate_gen(F, item_counts, MS, T, SDC)  # F, item_counts, M, T, SDC
    return frequent_items  # set of tuples


# System arguments to read data file, parameter file and specify output file
datapath = sys.argv[1]
mispath = sys.argv[2]
outpath = sys.argv[3]

# Calling the methods
(T, MS, item_counts, SDC) = parse_data(datapath, mispath)
frequent_items = MS_Apriori(MS, T, SDC, item_counts)
display_output(frequent_items, outpath)
