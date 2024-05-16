from ballstrikecount import getCountNums
from eventparser import getEventsByRow
import os
import csv
import numpy as np
import re

def getBaserunnerIndex(baserunners):
    if len(baserunners.keys()) != 3:
        pass
    reversedString = [str(int(baserunners[key])) for key in sorted(baserunners.keys(), reverse=True)]
    return int(''.join(reversedString), 2)

baserunners_indices = ['1', '2', '3']

# R00_dict = {(i, j): [] for i in range(13) for j in range(13)}

def getValues(data_dir, playoff, matrix, team_name = None):
    total = np.zeros(313)
    num_innings_total = 0
    specific_team = False if team_name is None else True
    for filename in os.listdir(data_dir):
        print(filename)
        filepath = os.path.join(data_dir, filename)
        if os.path.isfile(filepath) & (filepath.endswith(".EVA") | filepath.endswith(".EVN")):
            runs = 0
            error = False
            fielders = np.arange(1, 10)
            bases = np.array(['B', 1, 2, 3, 'H'])
            with open(filepath, newline='') as csvfile:
                reader = csv.reader(csvfile)
                currInning = ''
                batter = ''
                outs = 0
                homeTeamRuns = 0
                awayTeamRuns = 0
                baserunners = {'1': False, '2': False, '3': False}
                home_team = False
                vis_team = False
                for row in reader:
                    if error:
                        error = False
                        print("ERROR: ", row)
                    if specific_team:
                        if team_name in filepath:
                            home_team = True
                        elif len(row) == 3 and row[0] == 'info' and row[1] == 'visteam' and row[2] == team_name:
                            vis_team = True
                        elif len(row) > 2 and row[0] == 'info' and row[1] == 'visteam':
                            vis_team = False
                    if row[0] == 'play':
                        inning = row[1] + '-' + row[2]
                        if home_team and inning.endswith('0'):
                            continue
                        elif vis_team and inning.endswith('1'):
                            continue
                        elif home_team is False and vis_team is False and specific_team:
                            continue
                        currStrikes = 0
                        currBalls = 0
                        sameBatter = 0
                        repeat = False
                        if inning != currInning:
                            currInning = inning
                            num_innings_total += 1
                            outs = 0
                            baserunners = {'1': False, '2': False, '3': False}
                            if currInning[-1] == '0':
                                homeTeamRuns += runs
                            else:
                                awayTeamRuns += runs
                            runs = 0
                        elif batter == row[3]:
                            sameBatter = 1
                            repeat = True
                        batter = row[3]
                        pitchSeq = row[5]
                        if len(pitchSeq) > 1 and pitchSeq[-2] == '+':
                            pitchSeq = pitchSeq[0:-2]
                        addBalls = 0
                        addStrikes = 0
                        new_runs = 0
                        pitchCount = 0
                        for pitch in pitchSeq:
                            pitchCount += 1
                            if repeat and pitch == '.':
                                repeat = False
                            if pitch in ['+', '*', '.', '1', '2', '3', '>']:
                                continue
                            if pitch in ['A', 'C', 'K', 'L', 'M', 'O', 'Q', 'S', 'T']:
                                addStrikes = 1
                            elif pitch in ['B', 'I', 'P', 'V']:
                                addBalls = 1
                            elif pitch in ['F', 'R']:
                                if currStrikes < 2:
                                    addStrikes = 1
                            elif pitch in ['H', 'N', 'U', 'X', 'Y']:
                                pass
                            else:
                                print('ERROR: Unrecognized pitch type: ' + pitch)
                            if currStrikes == 2 and addStrikes == 1 and pitchCount != len(pitchSeq):
                                # print("ERROR: 3+ STRIKES: ", row)
                                error = True
                                addStrikes = 0
                            if currBalls == 3 and addBalls == 1 and pitchCount != len(pitchSeq):
                                # print("ERROR: 4+ BALLS: ", row)
                                error = True
                                addBalls = 0
                            if repeat and pitch != '.':
                                currBalls += addBalls
                                currStrikes += addStrikes
                                addBalls = 0
                                addStrikes = 0
                                continue
                            if (not pitchCount == len(pitchSeq)) and not repeat and not error:
                                prevMatrixIndex = 104*outs + 13*getBaserunnerIndex(baserunners) + 3 * currBalls + currStrikes + sameBatter
                                currBalls += addBalls
                                currStrikes += addStrikes
                                addBalls = 0
                                addStrikes = 0
                                sameBatter = 1
                                nextMatrixIndex = 104*outs + 13*getBaserunnerIndex(baserunners) + 3 * currBalls + currStrikes + sameBatter
                                # if 0 <= prevMatrixIndex <= 12 and 0<= nextMatrixIndex <= 12:
                                #     R00_dict[(prevMatrixIndex,nextMatrixIndex)].append(pitch)
                                matrix[prevMatrixIndex][nextMatrixIndex] += 1
                                total[prevMatrixIndex] += 1
                        eventSeq = row[6]
                        if eventSeq == 'S16/G6S.3-H;2-2':
                            pass
                        if int(inning.split('-')[0]) > 9 and not playoff: #since 2020, removed from playoffs in 2023
                            baserunners['2'] = True
                        basicDesc = eventSeq.split('/')[0]
                        addtlDesc = re.split(r'[./]', eventSeq)[1:] if '/' in eventSeq else ''
                        
                        advances = eventSeq.split('.')[-1] if '.' in eventSeq else ''
                        new_baserunners = baserunners.copy()
                        new_outs = outs
                        batter_out = False
                        batter_advanced = False
                        bases_reached = []
                        if len(advances) > 0:
                            for advance in advances.split(';'):
                                basicAdvance = advance.split('(')[0] if '(' in advance else advance
                                if 'X' in advance:
                                    if not 'E' in advance:
                                        new_outs += 1
                                        if not advance[0] == 'B':
                                            new_baserunners[advance[0]] = False
                                        else:
                                            batter_out = True
                                        continue
                                if basicAdvance[-1] == 'H':
                                    if advance[0] in baserunners_indices:
                                        new_baserunners[advance[0]] = False
                                    new_runs += 1
                                else:
                                    if advance[0] in baserunners_indices:
                                        new_baserunners[advance[0]] = False
                                    elif advance[0] == 'B':
                                        batter_advanced = True
                                    new_baserunners[basicAdvance[-1]] = True
                                    bases_reached.append(basicAdvance[-1])
                        reset_count = True
                        if(basicDesc.startswith('SB')):
                            reset_count = False
                            steals = basicDesc.split(';')
                            for steal in steals:
                                base = steal[2]
                                base_from = next((b for b in reversed(sorted(baserunners.keys())) if baserunners[b] is True and int(b) < (4 if base == 'H' else int(base))), '')
                                if new_outs >= 1 and base_from == '':
                                    # Runner stole a base then got out stealing a second one
                                    continue
                                elif any('E' in a and np.where(bases == a[0])[0] < np.where(bases == base)[0] and np.where(bases == a[2])[0] > np.where(bases == base)[0] for a in advances.split(';')):
                                    # Runner stole a base then advanced to another one on an error
                                    continue
                                if base == 'H':
                                    new_runs += 1
                                    new_baserunners[base_from] = False
                                else:
                                    new_baserunners[base] = True
                                    new_baserunners[base_from] = False
                        elif(basicDesc.startswith('POCS')):
                            reset_count = False
                            base = bases[np.where(bases == basicDesc[4])[0]-1][0]
                            if 'E' not in basicDesc:
                                new_baserunners[base] = False
                                new_outs += 1
                        elif(basicDesc.startswith('PO')):
                            reset_count = False
                            base = basicDesc[2]
                            if 'E' not in basicDesc:
                                new_outs += 1
                                new_baserunners[base] = False
                        elif(basicDesc.startswith('PB') or basicDesc.startswith('WP') or basicDesc.startswith('OA') or basicDesc.startswith('DI') or basicDesc.startswith('BK') or basicDesc.startswith('FLE')):
                            reset_count = False
                            pass
                        elif(basicDesc.startswith('NP')):
                            continue
                        elif(basicDesc.startswith('CS')):
                            reset_count = False
                            caughtSteals = basicDesc.split(';')
                            for caughtSteal in caughtSteals:
                                base = bases[np.where(bases == caughtSteal[2])[0]-1][0]
                                if 'E' not in caughtSteal:
                                    new_baserunners[base] = False
                                    new_outs += 1
                        elif not batter_out:
                            if(basicDesc.startswith('W') or basicDesc.startswith('IW')):
                                if not batter_advanced:
                                    new_baserunners['1'] = True
                            elif(basicDesc.startswith('K')):
                                if (len(basicDesc) == 1 or basicDesc.startswith('K23')) and not any(a.startswith('BX') for a in advances.split(';')):
                                    new_outs += 1
                                elif('+' in basicDesc):
                                    thirdStrikeDesc = basicDesc.split('+')[1]
                                    # if(a.startswith('B') for a in advances):
                                    #     pass
                                    if(thirdStrikeDesc.startswith('SB')):
                                        steals = thirdStrikeDesc.split(';')
                                        for steal in steals:
                                            base = steal[2]
                                            base_from = next((b for b in reversed(sorted(baserunners.keys())) if baserunners[b] is True), '')
                                            if new_outs >= 1 and base_from == '':
                                                # Runner stole a base then got out stealing a second one
                                                continue
                                            elif any('E' in a and np.where(bases == a[0])[0] < np.where(bases == base)[0] and np.where(bases == a[2])[0] > np.where(bases == base)[0] for a in advances.split(';')):
                                                # Runner stole a base then advanced to another one on an error
                                                continue
                                            if base == 'H':
                                                new_runs += 1
                                                new_baserunners[base_from] = False
                                            else:
                                                new_baserunners[base] = True
                                                new_baserunners[base_from] = False
                                    elif(thirdStrikeDesc.startswith('POCS')):
                                        base = bases[np.where(bases == thirdStrikeDesc[4])[0]-1][0]
                                        if 'E' not in thirdStrikeDesc:
                                            new_baserunners[base] = False
                                            new_outs += 1
                                    elif(thirdStrikeDesc.startswith('PO')):
                                        base = thirdStrikeDesc[2]
                                        if 'E' not in thirdStrikeDesc:
                                            new_outs += 1
                                            new_baserunners[base] = False
                                    elif(thirdStrikeDesc.startswith('CS')):
                                        new_outs += 1
                                        caughtSteals = thirdStrikeDesc.split(';')
                                        for caughtSteal in caughtSteals:
                                            base = bases[np.where(bases == caughtSteal[2])[0]-1][0]
                                            if 'E' not in caughtSteal and base not in bases_reached:
                                                new_baserunners[base] = False
                                                new_outs += 1
                            elif(basicDesc.startswith('HP')):
                                if not batter_advanced:
                                    new_baserunners['1'] = True
                            elif(basicDesc.startswith('H')):
                                for baserunner_index in baserunners_indices:
                                    new_baserunners[baserunner_index] = False
                                new_runs += 1
                            elif(basicDesc.startswith('FC')):
                                if not batter_advanced:
                                    new_baserunners['1'] = True
                            elif(re.compile(r'^\d*E').match(basicDesc)):
                                if(not any(a.startswith('B') for a in advances)):
                                    new_baserunners['1'] = True
                            elif(basicDesc.startswith('S')):
                                if not batter_advanced:
                                    new_baserunners['1'] = True
                            elif(basicDesc.startswith('D')):
                                if not batter_advanced:
                                    new_baserunners['2'] = True
                            elif(basicDesc.startswith('T')):
                                if not batter_advanced:
                                    new_baserunners['3'] = True
                            elif(basicDesc.startswith('C')):
                                if(not any(b.startswith('B') for b in advances)):
                                    new_baserunners['1'] = True
                            elif(int(basicDesc[0]) in fielders):
                                # num_baserunners = sum(value for value in baserunners.values() if value)
                                start_bases = [key for key, value in baserunners.items() if value]
                                start_bases.append('B')
                                untracked_runners = []
                                for i in range(len(start_bases)):
                                    if(not any(a.startswith(start_bases[i]) for a in advances.split(';'))):
                                        untracked_runners.append(start_bases[i])
                                new_outs += 1
                                if len(untracked_runners) > new_outs - outs:
                                    for i in range(len(basicDesc)):
                                        if i == len(basicDesc) - 1 and basicDesc[i] != ')':
                                            fielder = basicDesc[i]
                                            if fielder == '3' and '1' not in untracked_runners:
                                                new_baserunners['1'] = False
                                            elif fielder in ['4', '5'] and '2' not in untracked_runners:
                                                new_baserunners['2'] = False
                                            elif fielder == '5' and '3' not in untracked_runners:
                                                new_baserunners['3'] = False
                                            # else:
                                            #     new_baserunners['1'] = False
                                        elif basicDesc[i] == '(':
                                            runner = basicDesc[i+1]
                                            if runner.startswith('B') and '1' not in untracked_runners:
                                                untracked_runners.remove('B')
                                                new_baserunners['1'] = False
                                            elif runner.startswith('1') and '2' not in untracked_runners:
                                                untracked_runners.remove('1')
                                                new_baserunners['2'] = False
                                            elif runner.startswith('2') and '3' not in untracked_runners:
                                                untracked_runners.remove('2')
                                                new_baserunners['3'] = False
                                if(any('DP' in a for a in addtlDesc)):
                                    new_outs = outs + 2
                                if(any('TP' in a for a in addtlDesc)):
                                    new_outs = 3
                                # runnerSplit = basicDesc.split('(')
                                # for runner in runnerSplit:
                                #     if runner.startswith('B'):
                                #         new_baserunners['1'] = False
                                #     elif runner.startswith('1'):
                                #         new_baserunners['2'] = False
                                #     elif runner.startswith('2'):
                                #         new_baserunners['3'] = False
                                
                        prevMatrixIndex = 104*outs + 13*getBaserunnerIndex(baserunners) + 3 * currBalls + currStrikes + sameBatter if outs != 3 else 312
                        baserunners = new_baserunners
                        outs = new_outs
                        if reset_count:
                            currBalls = 0
                            currStrikes = 0
                            sameBatter = 0
                        else:
                            currBalls += addBalls
                            currStrikes += addStrikes
                            sameBatter = 1
                        nextMatrixIndex = 104*outs + 13*getBaserunnerIndex(baserunners) + 3 * currBalls + currStrikes + sameBatter if outs != 3 else 312
                        if prevMatrixIndex in range(13,26) and nextMatrixIndex in [221]:
                            pass
                        # if 0 <= prevMatrixIndex <= 12 and 0<= nextMatrixIndex <= 12:
                        #     R00_dict[(prevMatrixIndex,nextMatrixIndex)].append(eventSeq)
                        matrix[prevMatrixIndex][nextMatrixIndex] += 1
                        total[prevMatrixIndex] += 1
                        runs += new_runs
                        new_runs = 0
    print('total of ', num_innings_total, 'half innings')
    return total

def buildMatrix(data_dir):
    matrix = np.zeros((313, 313), dtype=np.float64)
    total = getValues(data_dir, False, matrix)

    # R00_unique = {key: list(set(value)) for key, value in R00_dict.items()}
    # with open("zero_to_twelve_events.txt", "w") as file:
    #     for key, value in R00_unique.items():
    #         file.write(f"{key}:\n")
    #         file.write("\t, ".join(value) + "\n")

    total[-1] = 1
    matrix = matrix / total[:, np.newaxis]
    matrix[-1][-1] = 1
    np.savetxt('matrix.txt', matrix)
    print(np.sum(matrix, axis=1))
    # sumRows(matrix)
    return matrix

def sumRows(matrix):
    for col in range(matrix.shape[1]):
        sum = np.sum(matrix[:][col])
        print('col ', col, '. sum = ', sum)

def createTeamMatrices():
    teams = ['ANA', 'ARI', 'ATL', 'BAL', 'BOS', 'CHA', 'CHN', 'CIN', 'CLE', 'COL', 'DET', 'HOU', 'KCA', 'LAN', 'MIA', 'MIL', 'MIN', 'NYA', 'NYN', 'OAK', 'PHI', 'PIT', 'SDN', 'SEA', 'SFN', 'SLN', 'TBA', 'TEX', 'TOR', 'WAS']
    for team in teams:
        matrix = np.zeros((313, 313), dtype=np.float64)
        total = getValues('data', False, matrix, team)
        total[-1] = 1
        matrix = matrix / total[:, np.newaxis]
        matrix[-1][-1] = 1
        np.savetxt('team_matrices/' + team + '_matrix.txt', matrix)
        # print(np.sum(matrix, axis=1))