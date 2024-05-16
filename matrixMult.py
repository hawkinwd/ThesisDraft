import numpy as np

def multMatrix(matrix):
    stateVec = np.zeros(313)
    stateVec[0] = 1
    numPitches = 0
    while(stateVec[-1] < 1-1e-10 and numPitches < 150):
        numPitches += 1
        np.matmul(stateVec, matrix, out=stateVec)
        print('pitch #', numPitches, '3-out prob=', stateVec[-1])
        np.savetxt('finalStateVector.txt', stateVec)

def calcAvgRuns(matrix):
    stateVec = np.zeros(313, dtype=np.float64)
    stateVec[0] = 1
    run_mat = createRunMatrix() * matrix
    print("EX RUNS: ", matrix[87][13], "times", createRunMatrix()[87][13], run_mat[87][13])
    # np.savetxt('runProbMatrix.csv', run_mat, delimiter=',', fmt='%f')
    numPitches = 0
    runsScored = 0
    while(stateVec[-1] < 1-1e-10 and numPitches < 150):
        numPitches += 1
        runsScored += np.sum(np.matmul(stateVec, run_mat))
        np.matmul(stateVec, matrix, out=stateVec)
        print('pitch #', numPitches, 'runs = ', runsScored)
    print('Avg. of ', runsScored, ' in a half inning. Avg. of ', 18*runsScored, 'per game.')

def reverseIndex(ind):
    outs = ind // 104
    ind = ind % 104
    baseInd = ind // 13
    ind = ind % 13

    new_batter = False
    if ind == 0:
        new_batter = True

    baseString = bin(baseInd)[2:]
    baserunners = baseString.count('1')

    return outs, baserunners, new_batter

def createRunMatrix():
    runMatrix = np.zeros((313, 313))
    for row in range(313):
        prev_outs, prev_baserunners, dummy = reverseIndex(row)
        for col in range(312):
            next_outs, next_baserunners, new_batter = reverseIndex(col)
            runs = (prev_outs + prev_baserunners) - (next_outs + next_baserunners)
            if not new_batter:
                runMatrix[row][col] = runs if runs > 0 else 0
            else:
                runMatrix[row][col] = runs + 1 if runs > -1 else 0
    runMatrix[312][312] = 0
    # np.savetxt('runMatrix.csv', runMatrix, delimiter=',', fmt='%d')
    return runMatrix

def calcTeamAvgRuns():
    teams = ['ANA', 'ARI', 'ATL', 'BAL', 'BOS', 'CHA', 'CHN', 'CIN', 'CLE', 'COL', 'DET', 'HOU', 'KCA', 'LAN', 'MIA', 'MIL', 'MIN', 'NYA', 'NYN', 'OAK', 'PHI', 'PIT', 'SDN', 'SEA', 'SFN', 'SLN', 'TBA', 'TEX', 'TOR', 'WAS']
    avg_matrix = np.loadtxt('matrix.txt')
    avg_matrix = avg_matrix.reshape((313, 313))
    team_runs = []
    for team in teams:
        team_matrix = np.loadtxt('team_matrices/' + team + '_matrix.txt')
        team_matrix = team_matrix.reshape((313, 313))
        team_matrix[np.all(np.isnan(team_matrix), axis=1)] = avg_matrix[np.all(np.isnan(team_matrix), axis=1)]
        stateVec = np.zeros(313, dtype=np.float64)
        stateVec[0] = 1
        run_mat = createRunMatrix() 
        run_mat = run_mat * team_matrix
        # np.savetxt('runProbMatrix.csv', run_mat, delimiter=',', fmt='%f')
        numPitches = 0
        runsScored = 0
        while(stateVec[-1] < 1-1e-10 and numPitches < 150):
            numPitches += 1
            expRuns = np.matmul(stateVec, run_mat)
            runsScored += np.sum(expRuns)
            np.matmul(stateVec, team_matrix, out=stateVec)
            # print('pitch #', numPitches, 'runs = ', runsScored)
        print(team + ': Avg. of ', runsScored, ' in a half inning. Avg. of ', 9*runsScored, 'per game.')
        team_runs.append((team, runsScored))
    team_runs = np.array(team_runs, dtype=[('team', 'U3'), ('runs', 'f8')])
    np.savetxt('teamruns.csv', team_runs, delimiter=',', fmt='%s,%f')