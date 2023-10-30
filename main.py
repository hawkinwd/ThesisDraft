import ballstrikecount as bsc
import itertools
import os

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

def write_dict_to_file(keys, d, filename):
    """
    Write a dictionary to a file, with each line in the format "key1, key2, ..., keyn, value"
    """
    with open(filename, 'a') as f:
        for key, value in d.items():
            if isinstance(value, dict):
                # Recursively write nested dictionaries
                write_dict_to_file(key, value, filename)
            else:
                # Write the key-value pair to the file
                keys_list = [keys] + [str(k) for k in key]
                line = ','.join(keys_list) + ',' + str(value) + '\n'
                f.write(line)

data_dir = "data"
output_file = "ballstrikevalueoncount.txt"
if os.path.exists(output_file):
    os.remove(output_file)

counts = {}
totals = []
for filename in os.listdir(data_dir):
    filepath = os.path.join(data_dir, filename)
    if os.path.isfile(filepath) & (filepath.endswith(".EVA") | filepath.endswith(".EVN")):

        # do something with the file
        # print("Getting counts from " + filename)
        temp_counts, total = bsc.getCountNums(filepath)
        counts = combine_dicts(counts, temp_counts)
        totals.append(total)
write_dict_to_file('', counts, output_file)
