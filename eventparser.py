import re
import csv
import numpy as np

fielders = np.arange(1, 10)
bases = np.array(['B', 1, 2, 3, 'H'])

def getEvents(filename, playoff):
    total = 0
    runs = 0
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        currInning = ''
        outs = 0
        homeTeamRuns = 0
        awayTeamRuns = 0
        baserunners = {'1': False, '2': False, '3': False}
        for row in reader:
            if row[0] == 'play':
                total += 1
                inning = row[1] + '-' + row[2]
                if inning != currInning:
                    currInning = inning
                    outs = 0
                    baserunners = {'1': False, '2': False, '3': False}
                    if currInning[-1] == '0':
                        homeTeamRuns += runs
                    else:
                        awayTeamRuns += runs
                    runs = 0
                eventSeq = row[6]
                if int(inning[0]) > 9 and not playoff:
                    baserunners['2'] = True
                basicDesc = eventSeq.split('/')[0]
                addtlDesc = re.split(r'[./]', eventSeq)[1:] if '/' in eventSeq else ''
                # find outs
                advances = eventSeq.split('.')[-1] if '.' in eventSeq else ''
                if len(advances) > 0:
                    new_baserunners = {'1': False, '2': False, '3': False}
                    for advance in advances.split(';'):
                        if 'X' in advance:
                            outs += 1
                        else:
                            if advance[-1] == 'H':
                                runs += 1
                            else:
                                new_baserunners[advance[-1]] = True
                    baserunners = new_baserunners
                if(basicDesc.startswith('SB')):
                    steals = basicDesc.split(';')
                    new_baserunners = {'1': False, '2': False, '3': False}
                    for steal in steals:
                        base = steal[2]
                        if base == 'H':
                            runs += 1
                        else:
                            new_baserunners[base] = True
                    baserunners = new_baserunners
                elif(basicDesc.startswith('POCS')):
                    caughtSteals = basicDesc.split(';')
                    for caughtSteal in caughtSteals:
                        base = bases[bases.index(caughtSteal[4])-1]
                        baserunners[base] = False
                        outs += 1
                elif(basicDesc.startswith('PO')):
                    pickoffs = basicDesc.split(';')
                    for pickoff in pickoffs:
                        base = pickoff[2]
                        if 'E' not in basicDesc:
                            outs += 1
                            baserunners[base] = False
                elif(basicDesc.startswith('PB') or basicDesc.startswith('WP') or basicDesc.startswith('OA') or basicDesc.startswith('DI') or basicDesc.startswith('BK') or basicDesc.startswith('NP') or basicDesc.startswith('FLE')):
                    pass
                elif(basicDesc.startswith('CS')):
                    caughtSteals = basicDesc.split(';')
                    for caughtSteal in caughtSteals:
                        base = bases[bases.index(caughtSteal[2])-1]
                        baserunners[base] = False
                        outs += 1
                elif(basicDesc.startswith('W') or basicDesc.startswith('IW')):
                    baserunners['1'] = True
                elif(basicDesc.startswith('K')):
                    outs += 1
                elif(basicDesc.startswith('HP')):
                    baserunners['1'] = True
                elif(basicDesc.startswith('H')):
                    runs += 1
                elif(basicDesc.startswith('FC')):
                    baserunners['1'] = True
                elif(basicDesc.startswith('E')):
                    baserunners['1'] = True
                elif(basicDesc.startswith('S')):
                    baserunners['1'] = True
                elif(basicDesc.startswith('D')):
                    baserunners['2'] = True
                elif(basicDesc.startswith('T')):
                    baserunners['3'] = True
                elif(basicDesc.startswith('C')):
                    if(not any(b.startswith('B') for b in advances)):
                        baserunners['1'] = True
                elif(int(basicDesc[0]) in fielders):
                    outs += 1
                    runnerSplit = basicDesc.split('(')
                    for runner in runnerSplit:
                        if runner.startswith('B'):
                            baserunners['1'] = False
                        elif runner.startswith('1'):
                            baserunners['2'] = False
                        elif runner.startswith('2'):
                            baserunners['3'] = False
                        first = runner[-1]
                        if first == '3':
                            baserunners['1'] = False
                    if(any('DP' in a for a in addtlDesc)):
                        outs += 1
                    if(any('TP' in a for a in addtlDesc)):
                        outs += 2
                    
homeTeamRuns = 0
awayTeamRuns = 0
currInning = '0-0'
def getEventsByRow(playoff, row):
    inning = row[1] + '-' + row[2]
    if inning != currInning:
        currInning = inning
        outs = 0
        baserunners = {'1': False, '2': False, '3': False}
        if currInning[-1] == '0':
            homeTeamRuns += runs
        else:
            awayTeamRuns += runs
        runs = 0
    eventSeq = row[6]
    if int(inning[0]) > 9 and not playoff:
        baserunners['2'] = True
    basicDesc = eventSeq.split('/')[0]
    addtlDesc = re.split(r'[./]', eventSeq)[1:] if '/' in eventSeq else ''
    # find outs
    advances = eventSeq.split('.')[-1] if '.' in eventSeq else ''
    if len(advances) > 0:
        new_baserunners = {'1': False, '2': False, '3': False}
        for advance in advances.split(';'):
            if 'X' in advance:
                outs += 1
            else:
                if advance[-1] == 'H':
                    runs += 1
                else:
                    new_baserunners[advance[-1]] = True
        baserunners = new_baserunners
    if(basicDesc.startswith('SB')):
        steals = basicDesc.split(';')
        new_baserunners = {'1': False, '2': False, '3': False}
        for steal in steals:
            base = steal[2]
            if base == 'H':
                runs += 1
            else:
                new_baserunners[base] = True
        baserunners = new_baserunners
    elif(basicDesc.startswith('POCS')):
        caughtSteals = basicDesc.split(';')
        for caughtSteal in caughtSteals:
            base = bases[bases.index(caughtSteal[4])-1]
            baserunners[base] = False
            outs += 1
    elif(basicDesc.startswith('PO')):
        pickoffs = basicDesc.split(';')
        for pickoff in pickoffs:
            base = pickoff[2]
            if 'E' not in basicDesc:
                outs += 1
                baserunners[base] = False
    elif(basicDesc.startswith('PB') or basicDesc.startswith('WP') or basicDesc.startswith('OA') or basicDesc.startswith('DI') or basicDesc.startswith('BK') or basicDesc.startswith('NP') or basicDesc.startswith('FLE')):
        pass
    elif(basicDesc.startswith('CS')):
        caughtSteals = basicDesc.split(';')
        for caughtSteal in caughtSteals:
            base = bases[bases.index(caughtSteal[2])-1]
            baserunners[base] = False
            outs += 1
    elif(basicDesc.startswith('W') or basicDesc.startswith('IW')):
        baserunners['1'] = True
    elif(basicDesc.startswith('K')):
        outs += 1
    elif(basicDesc.startswith('HP')):
        baserunners['1'] = True
    elif(basicDesc.startswith('H')):
        runs += 1
    elif(basicDesc.startswith('FC')):
        baserunners['1'] = True
    elif(basicDesc.startswith('E')):
        baserunners['1'] = True
    elif(basicDesc.startswith('S')):
        baserunners['1'] = True
    elif(basicDesc.startswith('D')):
        baserunners['2'] = True
    elif(basicDesc.startswith('T')):
        baserunners['3'] = True
    elif(basicDesc.startswith('C')):
        if(not any(b.startswith('B') for b in advances)):
            baserunners['1'] = True
    elif(int(basicDesc[0]) in fielders):
        outs += 1
        runnerSplit = basicDesc.split('(')
        for runner in runnerSplit:
            if runner.startswith('B'):
                baserunners['1'] = False
            elif runner.startswith('1'):
                baserunners['2'] = False
            elif runner.startswith('2'):
                baserunners['3'] = False
            first = runner[-1]
            if first == '3':
                baserunners['1'] = False
        if(any('DP' in a for a in addtlDesc)):
            outs += 1
        if(any('TP' in a for a in addtlDesc)):
            outs += 2

