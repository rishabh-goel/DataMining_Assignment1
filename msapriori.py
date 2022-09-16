import sys

transactions = []
items = set()
MIS = {}
SDC = 0
F = set()


def parse_data(data):
    with open(data) as f:
        content = f.readlines()

    for line in content:
        list1 = []
        str_list = line.split(",")
        for number in str_list:
            list1.append(number.strip())
            items.add(number.strip())
        transactions.append(list1)


def parse_parameters(parameters):
    with open(parameters) as f:
        content = f.readlines()

    for line in content:
        key, value = line.split("=")

        key = key.split("(")[-1].split(")")[0]

        if key == "SDC":
            SDC = float(value)
        else:
            MIS[key] = float(value)


# for assignment, we start with the list
# init_pass: Compute counts for each item and store in ordered dictionary
def init_pass(M, T):
    item_counts = {}
    F1 = set()
    for t in T:
        # print("Transactions")
        # print(t)

        for item in t:
            if item in item_counts.keys():
                item_counts[item] += 1
            else:
                item_counts[item] = 1
            # print("Item")
            # print(item)

    for item in item_counts:
        if item in MIS.keys():
            if MIS[item] <= item_counts[item]/len(T):
                F1.add(item)
        else:
            if MIS["rest"] <= item_counts[item]/len(T):
                F1.add(item)

    return item_counts, F1


def level2_candidate_generate():

    return 0


if __name__ == '__main__':
    data_file = sys.argv[1]
    parameter_file = sys.argv[2]
    parse_data(data_file)
    parse_parameters(parameter_file)

    M = [x[0] for x in sorted(MIS.items(), key=lambda item: item[1])]  # sort keys according to MS(i) values
    L, F1 = init_pass(MIS, transactions)
    with open("file.txt", "w") as f:
        f.write("")
    if len(F1) != 0:
        with open("file.txt", "a") as f:
            f.write(F1)

        F2 = level2_candidate_generate(L)
