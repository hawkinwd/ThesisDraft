import ballstrikecount as bsc
import eventparser as ep
import matrix as mtix
import matrix25 as mtix25
import matrixMult25 as mm25
import matrixMult as mm
import os
import numpy as np

data_dir = "data"

def combine_dicts(d1, d2):
    """
    Combine two dictionaries, including all keys in both and summing the entries if a key exists in both dicts.
    """
    for key, value in d2.items():
        if isinstance(value, dict):
            # Recursively combine nested dictionaries
            d1[key] = combine_dicts(d1.get(key, {}), value)
        else:
            d1[key] = d1.get(key, 0) + value
    return d1

def sort_dict(dict):
    keys = list(dict.keys())
    keys.sort()
    return {i: dict[i] for i in keys}

def write_dict_to_file(keys, d, filename):
    """
    Write a dictionary to a file, with each line in the format "key1, key2, ..., keyn, value"
    """
    with open(filename, 'a') as f:
        for key, value in d.items():
            if isinstance(value, dict):
                # Recursively write nested dictionaries
                sorted_value = sort_dict(value)
                write_dict_to_file(key, sorted_value, filename)
            else:
                # Write the key-value pair to the file
                keys_list = [keys] + [str(k) for k in key]
                line = ','.join(keys_list) + ',' + str(value) + '\n'
                f.write(line)

data_dir = "data"
output_file = "ballstrikevalueoncount.txt"
if os.path.exists(output_file):
    os.remove(output_file)

# counts = {}
# totals = []
# for filename in os.listdir(data_dir):
#     filepath = os.path.join(data_dir, filename)
#     if os.path.isfile(filepath) & (filepath.endswith(".EVA") | filepath.endswith(".EVN")):

#         # print("Getting counts from " + filename)
#         temp_counts, total = bsc.getCountNums(filepath)
#         counts = combine_dicts(counts, temp_counts)
#         totals.append(total)

#         ep.getEvents(filepath, False)  #Update False if playoff games
# counts = sort_dict(counts)
# write_dict_to_file('', counts, output_file)

# trans_matrix = mtix.buildMatrix(data_dir)
# print(trans_matrix[87][0])
# zero = sum(element == 0 for row in trans_matrix for element in row)
# print('there are ', zero, ' elements that are zero')
# mm.multMatrix(trans_matrix)
# mm.calcAvgRuns(trans_matrix)
# mtix.createTeamMatrices()
mm.calcTeamAvgRuns()
# mm.createRunMatrix()

# trans_matrix_25 = mtix25.buildMatrix(data_dir)
# mm25.multMatrix(trans_matrix_25)
# mm25.calcAvgRuns(trans_matrix_25)
# mtix25.createTeamMatrices()
mm25.calcTeamAvgRuns()
