import numpy as np

def multMatrix(matrix):
    stateVec = np.zeros(25)
    stateVec[0] = 1
    numAtBats = 0
    while(stateVec[-1] < 1-1e-10):
        numAtBats += 1
        np.matmul(stateVec, matrix, out=stateVec)
        print('at bat #', numAtBats, '3-out prob=', stateVec[-1])
        np.savetxt('25finalStateVector.txt', stateVec)

def calcAvgRuns(matrix):
    stateVec = np.zeros(25, dtype=np.float64)
    stateVec[0] = 1
    run_mat = createRunMatrix() * matrix
    np.savetxt('25runProbMatrix.csv', run_mat, delimiter=',', fmt='%f')
    numAtBats = 0
    runsScored = 0
    while(stateVec[-1] < 1-1e-10):
        numAtBats += 1
        runsScored += np.sum(np.matmul(stateVec, run_mat))
        np.matmul(stateVec, matrix, out=stateVec)
        print('at bat #', numAtBats, 'runs = ', runsScored)
    print('Avg. of ', runsScored, ' in a half inning. Avg. of ', 18*runsScored, 'per game.')

def reverseIndex(ind):
    outs = ind // 8
    ind = ind % 8
    baseInd = ind

    baseString = bin(baseInd)[2:]
    baserunners = baseString.count('1')

    return outs, baserunners

def createRunMatrix():
    runMatrix = np.zeros((25, 25))
    for row in range(25):
        prev_outs, prev_baserunners = reverseIndex(row)
        for col in range(24):
            next_outs, next_baserunners = reverseIndex(col)
            runs = (prev_outs + prev_baserunners) - (next_outs + next_baserunners)
            runMatrix[row][col] = runs + 1 if runs > -1 else 0
    runMatrix[24][24] = 0
    np.savetxt('25runMatrix.csv', runMatrix, delimiter=',', fmt='%d')
    return runMatrix

def calcTeamAvgRuns():
    teams = ['ANA', 'ARI', 'ATL', 'BAL', 'BOS', 'CHA', 'CHN', 'CIN', 'CLE', 'COL', 'DET', 'HOU', 'KCA', 'LAN', 'MIA', 'MIL', 'MIN', 'NYA', 'NYN', 'OAK', 'PHI', 'PIT', 'SDN', 'SEA', 'SFN', 'SLN', 'TBA', 'TEX', 'TOR', 'WAS']
    team_runs = []
    for team in teams:
        team_matrix = np.loadtxt('team_matrices25/' + team + '_matrix25.txt')
        team_matrix = team_matrix.reshape((25, 25))
        stateVec = np.zeros(25, dtype=np.float64)
        stateVec[0] = 1
        run_mat = createRunMatrix() * team_matrix
        # np.savetxt('runProbMatrix.csv', run_mat, delimiter=',', fmt='%f')
        numAtBats = 0
        runsScored = 0
        while(stateVec[-1] < 1-1e-10):
            numAtBats += 1
            runsScored += np.sum(np.matmul(stateVec, run_mat))
            np.matmul(stateVec, team_matrix, out=stateVec)
            # print('at bat #', numAtBats, 'runs = ', runsScored)
        print(team + ': Avg. of ', runsScored, ' in a half inning. Avg. of ', 9*runsScored, 'per game.')
        team_runs.append((team, runsScored))
    team_runs = np.array(team_runs, dtype=[('team', 'U3'), ('runs', 'f8')])
    np.savetxt('teamruns25.csv', team_runs, delimiter=',', fmt='%s,%f')