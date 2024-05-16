import numpy as np
from matrix import getBaserunnerIndex

matrix = np.loadtxt('matrix.txt')
matrix = matrix.reshape(313, 313)

# 104*outs + 13*getBaserunnerIndex(baserunners) + 3 * currBalls + currStrikes + sameBatter if outs != 3 else 312
# outs = 0
# old_br = {'1': True, '2': True, '3': False}
# new_br = {'1': True, '2': False, '3': False}
# old_ct = {'balls': 0, 'strikes': 0}
# new_ct = {'balls': 2, 'strikes': 0}

def baserunners_to_string(br):
    if all(char == '0' for char in br):
        return 'no runners on, '
    else:
        retStr = 'runners on '
        if br[2] == '1':
            retStr += 'first '
        if br[1] == '1':
            retStr += 'second '
        if br[0] == '1':
            retStr += 'third, '
        return retStr

def reverseIndex(ind):
    outs = ind // 104
    ind = ind % 104
    baseInd = ind // 13
    ind = ind % 13
    
    balls = 0
    strikes = 0

    new_batter = False
    if ind == 0:
        new_batter = True
    else:
        balls = (ind-1) // 3
        strikes = (ind-1) % 3

    baseString = format(baseInd, '03b')
    # baserunners = baseString.count('1')

    out_string = ''
    if outs == 1:
        out_string = '1 out, '
    else:
        out_string = str(outs) + ' outs, '

    new_batter_string = ''
    if new_batter:
        new_batter_string = ', new batter'

    return out_string + baserunners_to_string(baseString) + str(balls) + '-' + str(strikes) + ' count' + new_batter_string
    # return outs, baserunners, new_batter, balls, strikes

# print('From ', outs, old_br, old_ct, '; To ', outs, new_br, new_ct, '; Prob=', matrix[104*outs + 13*getBaserunnerIndex(old_br) + 3*old_ct['balls'] + old_ct['strikes']][104*outs + 13*getBaserunnerIndex(new_br) + 3*new_ct['balls'] + new_ct['strikes'] + 1])
nonzero_indices = np.transpose(np.nonzero(matrix))
currRow = -1
sum = 0
with open('probs.txt', 'w') as file:
    for index in nonzero_indices:
        row = index[0]
        if currRow != row:
            if currRow != -1:
                file.write("\tTotal = " + str(sum) + "\n")
                sum = 0
            file.write("From " + reverseIndex(row) + " (index=" + str(row) + "):\n")
            currRow = row
        file.write("\tTo " + reverseIndex(index[1]) + " (index=" + str(index[1]) + "): " + str(matrix[index[0]][index[1]]) + "\n")
        sum += matrix[index[0]][index[1]]