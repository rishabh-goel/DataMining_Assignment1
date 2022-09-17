import sys

transactions = []
items = set()
MS = {}
SDC = 0
F = {}
item_counts = {}
n = 0


def parse_data(data):
    with open(data) as f:
        content = f.readlines()

    for line in content:
        list1 = []
        str_list = line.split(",")
        for number in str_list:
            number = int(number.strip())
            list1.append(number)
            items.add(number)
        transactions.append(list1)

    n = len(transactions)


def parse_parameters(parameters):
    with open(parameters) as f:
        content = f.readlines()

    for line in content:
        key, value = line.split("=")

        key = key.split("(")[-1].split(")")[0]

        if key == "SDC":
            SDC = float(value)
        elif key == "rest":
            for num in items:
                if num not in MS:
                    MS[num] = float(value)
        else:
            MS[key] = float(value)


def init_pass(M, T):
    for t in T:
        for item in t:
            if item in item_counts.keys():
                item_counts[item] += 1
            else:
                item_counts[item] = 1

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


def calculate_f1(l):
    F1 = set()
    for item in l:
        if MS[item] <= item_counts[item]/n:
            F1.add(item)

    return F1


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


def ms_candidate_generate(fk_minus_one, sdc):
    candidate_set = []

    for i in range(len(fk_minus_one)-1):
        for j in range(len(fk_minus_one)):
            list1 = fk_minus_one[i][:len(fk_minus_one[i])-1]
            list2 = fk_minus_one[j][:len(fk_minus_one[j])-1]

            if list1 != list2:
                break
            else:
                last_item_of_i = fk_minus_one[i][len(fk_minus_one[i])-1]
                last_item_of_j = fk_minus_one[j][len(fk_minus_one[j])-1]

                support_last_item_of_i = item_counts[last_item_of_i]/n
                support_last_item_of_j = item_counts[last_item_of_j]/n

                if abs(support_last_item_of_j - support_last_item_of_i) <= sdc:
                    if last_item_of_i < last_item_of_j:
                        list1 = list1.append(last_item_of_i).append(last_item_of_j)
                    else:
                        list1 = list1.append(last_item_of_j).append(last_item_of_i)

                    candidate_set.append(list1)

    valid_set = []
    # TODO: Generate subset and deletion from candidate_set

    return valid_set


if __name__ == '__main__':
    data_file = sys.argv[1]
    parameter_file = sys.argv[2]
    parse_data(data_file)
    parse_parameters(parameter_file)

    M = [x[0] for x in sorted(MS.items(), key=lambda item: item[1])]  # sort keys according to MS(i) values
    L = init_pass(M, transactions)
    F_one = calculate_f1(L)
    k = 1

    F[k] = F_one

    if len(F_one) != 0:
        with open("file.txt", "a") as f:
            f.write(F_one)

        k += 1

        while len(F[k-1]) != 0:
            if k == 2:
                Ck = level2_candidate_generate(L, SDC)
            else:
                Ck = ms_candidate_generate(F[k-1], SDC)


