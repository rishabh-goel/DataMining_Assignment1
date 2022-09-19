import itertools
import sys
from collections import Counter

transactions = []
items = []
MS = {}
SDC = 0
F = {}
item_counts = {}
n = 0
c_support_count = {}


# Method to parse data file
def parse_data(data):
    global n
    with open(data) as f:
        content = f.readlines()

    for line in content:
        list1 = []
        str_list = line.split(",")
        for number in str_list:
            number = int(number.strip())
            list1.append(number)
            if number not in items:
                items.append(number)
        transactions.append(list1)

    n = len(transactions)


# Method to parse parameter file
def parse_parameters(parameters):
    global SDC
    with open(parameters) as f:
        content = f.readlines()

    for line in content:
        key, value = line.split("=")

        key = key.split("(")[-1].split(")")[0].strip()

        # Parameter files has SDC, min item support for the transactions
        if key == 'SDC':
            SDC = float(value)
        elif key == 'rest':
            for num in items:
                if num not in MS:
                    MS[num] = float(value)
        else:
            MS[int(key)] = float(value)


# Method for the initial pass over all the transactions
def init_pass(M, T):
    global item_counts
    item_list = []
    for t in T:
        for item in t:
            item_list.append(item)

    item_counts = Counter(item_list)
    l = []
    found_first_item = False
    for item in M:
        if found_first_item:
            if first_item <= item_counts[item]/n:
                l.append(item)
        else:
            if MS[item] <= item_counts[item]/n:
                first_item = MS[item]
                found_first_item = True
                l.append(item)

    return l


# Method to calculate first level frequent item set (F1)
def calculate_f1(l):
    F1 = []
    for item in l:
        if MS[item] <= item_counts[item]/n:
            F1.append(item)

    return F1


# Method to generate level 2 candidates
def level2_candidate_generate(l, sdc):
    level2_candidates = []

    for i in range(len(l)-1):
        support_i = item_counts[l[i]]/n

        if MS[l[i]] <= support_i:
            for j in range(i+1, len(l)):
                support_j = item_counts[l[j]]/n

                if MS[l[i]] <= support_j and abs(support_j - support_i) <= sdc:
                    level2_candidates.append([l[i], l[j]])

    return level2_candidates


# Method to generate candidate sets for other levels
def ms_candidate_generate(fk_minus_one, sdc):
    candidate_set = []

    # Generate all itemsets
    for i in range(len(fk_minus_one)):
        for j in range(len(fk_minus_one)):
            list1 = fk_minus_one[i][:len(fk_minus_one[i]) - 1]
            list2 = fk_minus_one[j][:len(fk_minus_one[j]) - 1]

            if list1 != list2:
                break
            else:
                last_item_of_i = fk_minus_one[i][len(fk_minus_one[i]) - 1]
                last_item_of_j = fk_minus_one[j][len(fk_minus_one[j]) - 1]

                support_last_item_of_i = item_counts[last_item_of_i]/n
                support_last_item_of_j = item_counts[last_item_of_j]/n

                if last_item_of_i < last_item_of_j and abs(support_last_item_of_j - support_last_item_of_i) <= sdc:
                    list1.extend([last_item_of_i, last_item_of_j])
                    candidate_set.append(list1)

    valid_set = []
    flag = {}

    # Find valid itemsets from the list of all candidate sets
    for i in range(len(candidate_set)):
        combinations_list = list(itertools.combinations(candidate_set[i], len(candidate_set[i]) - 1))
        for combination in combinations_list:
            subset = list(combination)

            if candidate_set[i][0] in subset or MS[candidate_set[i][1]] == MS[candidate_set[i][0]]:
                if subset not in fk_minus_one:
                    flag[i] = 1

    for i in range(len(candidate_set)):
        if i not in flag:
            valid_set.append(candidate_set[i])

    return valid_set


# Method to generate output
def display_output():
    result = ""
    for key, value in F.items():
        result += f"(Length-{key} {len(value)}\n"
        if key == 1:
            for num in value:
                result += f"({num})\n"
        else:
            for num in value:
                result += "(" + " ".join(list(map(str, num))) + ")\n"

        result += ")\n"

    print(result)


if __name__ == '__main__':
    # Read data and parameter file and parse them from command line
    data_file = sys.argv[1]
    parameter_file = sys.argv[2]
    parse_data(data_file)
    parse_parameters(parameter_file)

    # Sort keys according to MS(i) values
    M = [x[0] for x in sorted(MS.items(), key=lambda item: item[1])]

    L = init_pass(M, transactions)
    F_one = calculate_f1(L)
    k = 1

    # Store output of each level in a dictionary of lists
    F[k] = list(F_one)

    if len(F_one) != 0:
        k += 1

        # Generate itemsets till the itemsets are generated in previous level
        while len(F[k-1]) != 0:
            if k == 2:
                Ck = level2_candidate_generate(L, SDC)
            else:
                Ck = ms_candidate_generate(F[k - 1], SDC)

            # Count the occurrences of all candidates in the transactions
            for t in transactions:
                for c in Ck:
                    check = all(item in t for item in c)
                    if check:
                        if tuple(c) in item_counts:
                            item_counts[tuple(c)] += 1
                        else:
                            item_counts[tuple(c)] = 1

            # Prune the candidate if condition not satisfied
            fk = []
            for c in Ck:
                if tuple(c) in item_counts:
                    if item_counts[tuple(c)]/n >= MS[c[0]]:
                        fk.append(c)

            F[k] = fk
            k += 1

        # Popping the last empty itemset
        F.popitem()

        display_output()

    else:
        print("No frequent itemset!!!")
