import csv

def getCountNums(filename):
    counts = {}
    total = 0
    error = False
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if error:
                error = False
                print("ERROR: ", row)
            if row[0] == 'play':
                total += 1
                currStrikes = 0
                currBalls = 0
                pitchSeq = row[5]
                if len(pitchSeq) > 0 and pitchSeq[-1] == 'N':
                    # print('Skipping play: ', row)
                    continue
                for pitch in pitchSeq:
                    if pitch in ['+', '*', '.', '1', '2', '3', '>']:
                        continue
                    if currStrikes >= 3:
                        # print("ERROR: 3+ STRIKES: ", row)
                        error = True
                    if currBalls >= 4:
                        # print("ERROR: 4+ BALLS: ", row)
                        error = True
                    key = str(currBalls) + '-' + str(currStrikes)
                    if not key in counts:
                        counts[key] = {}
                        counts[key][pitch] = 1
                    else:
                        if not pitch in counts[key]:
                            counts[key][pitch] = 1
                        else:
                            counts[key][pitch] += 1
                    if pitch in ['A', 'C', 'K', 'L', 'M', 'O', 'Q', 'S', 'T']:
                        currStrikes += 1
                    elif pitch in ['B', 'I', 'P', 'V']:
                        currBalls += 1
                    elif pitch in ['F', 'R']:
                        if currStrikes < 2:
                            currStrikes += 1
                    elif pitch in ['H', 'N', 'U', 'X', 'Y']:
                        pass
                    else:
                        print('ERROR: Unrecognized pitch type: ' + pitch)
    # print("total = ", total)
    return [counts, total]

# def getCountNumsByRow(row, prevCount):
#     currStrikes = prevCount[2]
#     currBalls = prevCount[0]
#     pitchSeq = row[5]
#     if len(pitchSeq) > 0 and pitchSeq[-1] == 'N':
#         # print('Skipping play: ', row)
#         continue
#     for pitch in pitchSeq:
#         if pitch in ['+', '*', '.', '1', '2', '3', '>']:
#             continue
#         if currStrikes >= 3:
#             # print("ERROR: 3+ STRIKES: ", row)
#             error = True
#         if currBalls >= 4:
#             # print("ERROR: 4+ BALLS: ", row)
#             error = True
#         key = str(currBalls) + '-' + str(currStrikes)
#         if not key in counts:
#             counts[key] = {}
#             counts[key][pitch] = 1
#         else:
#             if not pitch in counts[key]:
#                 counts[key][pitch] = 1
#             else:
#                 counts[key][pitch] += 1
#         if pitch in ['A', 'C', 'K', 'L', 'M', 'O', 'Q', 'S', 'T']:
#             currStrikes += 1
#         elif pitch in ['B', 'I', 'P', 'V']:
#             currBalls += 1
#         elif pitch in ['F', 'R']:
#             if currStrikes < 2:
#                 currStrikes += 1
#         elif pitch in ['H', 'N', 'U', 'X', 'Y']:
#             pass
#         else:
#             print('ERROR: Unrecognized pitch type: ' + pitch)