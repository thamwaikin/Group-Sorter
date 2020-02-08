import pandas as pd
import random
import operator
import math
from scipy import stats
import time
from decimal import Decimal
import statistics

###### Global Vars (Example) ######

importFile = 'group.xlsx'

indexCol = ['Student ID']
seedCol = ['Item A']

selectedCategoryCols = ['Gender', 'Ethnicity']
categoryWeights = [10, 5]

selectedQuartileCols = ['Item A', 'Item B', 'Item X', 'Item Y', 'Item Z', ]
quartileWeights = [1, 1, 1, 1, 1]

numOfTeams = 6
iterations = 100
selectTop = 1

df = pd.DataFrame()

quartileCols = []  # converted column names
categoryCols = []  # converted column names
normalizer = []  # num of unique var in each col
groups = []


###### Convert Continuous Variables to Quartiles ######
# for each selected quartile column, obtain the list of numbers
# for each number in the list, obtain the percentile of the number
# assign the quartile based on the percentile
# create a new column with the corresponding quartile number


def getQuartiles():
    for selectedCol in selectedQuartileCols:
        col = list(df[selectedCol])
        temp = []
        for x in col:
            percentile = stats.percentileofscore(col, x)
            if percentile <= 25:
                quartile = 1
            elif percentile <= 50:
                quartile = 2
            elif percentile <= 75:
                quartile = 3
            else:
                quartile = 4
            temp.append(quartile)
        df.insert(len(df.columns), selectedCol + ' Quartile', temp)
        quartileCols.append(selectedCol + ' Quartile')


###### Convert Categorical Variables to Numbers ######
# create the normalizer list (var represent the # of unique elements in the column)
# i.e. gender may have 2 (male and female), each converted quartile column has 4
# for each selected categorical column, assign a number for each unique category
# i.e. male > 1, female > 2 OR chinese > 1, indian > 2, malay < 3, others > 4
# create a new column with the corresponding categorical number


def getCategories():
    global normalizer
    normalizer = [4] * len(selectedQuartileCols)

    for selectedCol in selectedCategoryCols:
        temp = []
        col = list(df[selectedCol])
        colLower = [x.lower() for x in col]
        colSet = set(colLower)
        for x in col:
            temp.append(list(colSet).index(x.lower())+1)
        df.insert(len(df.columns), selectedCol + ' Category', temp)
        categoryCols.append(selectedCol + ' Category')
        normalizer.append(len(colSet))


###### Funciton for Diversity Score ######
# takes in a group of people as an input
# look through a column and calculate how diverse the results are
# i.e. for gender: 1x male & 1x female will have a higher score than 2x male
# adds the score of the column to the overall diversity score of the group
# return the result


def method(group):
    cols = quartileCols + categoryCols
    weights = quartileWeights + categoryWeights
    diversityScore = 0
    for col, index, weight in zip(cols, normalizer, weights):
        var = [p.get(col) for p in group]  # function for a variable of a col
        rawScore = [var.count(i+1) for i in range(index)]
        normalizedScore = [i/sum(rawScore) for i in rawScore]
        finalScore = [abs(i - (1/index)) for i in normalizedScore]
        diversityScore += (weight * sum(finalScore))
    return diversityScore


###### Sorting into groups ######
# main method to sort people into the groups, takes in a column as an input for seeding
# converts the dataframe to dictionary and set various parameters
# outer loop, while not all people are assigned to groups or if 1 group has less than min # of people, re-sort everyone
# inner loop, assign the first row of people then randomly choose from the pool 
# assign the randomly chosen person to every group and determine the group with the largest improvement in diversity score
# assign the person to the group and remove the person from the pool, repeat


def getGroupings(col):
    records = df.to_dict(orient='records')
    if col:
        # if chosen to seed, sort people by the selected col
        records.sort(key=lambda x: x[col], reverse=True)

    numOfPeople = len(records) 
    maxNumPerTeam = math.ceil(numOfPeople / numOfTeams)
    minNumPerTeam = math.floor(numOfPeople / numOfTeams)
    maxTeamWithMaxNum = numOfPeople % numOfTeams
    done = False

    # outer loop
    while not done:
        people = records.copy()
        groups.clear()

        # inner loop
        for _ in range(numOfTeams):
            if col:
                person = people[0] # seed by the selected col
            else:
                person = random.choice(people) # randomly assign
            group = [person]
            groups.append(group)
            people.remove(person)

        maxed = [False] * numOfTeams # track the teams that has reached maximum

        while len(people) != 0:
            person = random.choice(people)
            tempVar = [0] * numOfTeams

            for counter in range(numOfTeams):
                if len(groups[counter]) <= maxNumPerTeam:
                    oldGroup = groups[counter].copy() # without the new person
                    newGroup = groups[counter].copy() # with the new person
                    newGroup.append(person)
                    tempVar[counter] = float(
                        round(Decimal(method(oldGroup) - method(newGroup)), 2))  # find the group with the largest improvement in diversity

            tempVar = [-math.inf if max else i for i,
                       max in zip(tempVar, maxed)]  # assign -inf for groups that have reached the limit
            # print('TempVar : ' + str(tempVar))

            for index, value in enumerate(tempVar):
                if value == max(tempVar) and not maxed[index]:
                    groups[index].append(person)
                    people.remove(person)
                    # print('Group ' + str(index + 1) + ': ' + str([p.get('Student ID') for p in groups[index]]))
                    if maxTeamWithMaxNum == 0:
                        if len(groups[index]) == maxNumPerTeam:
                            maxed[index] = True
                    elif len(groups[index]) == (maxNumPerTeam - 1 if maxed.count(True) >= maxTeamWithMaxNum else maxNumPerTeam):
                        maxed[index] = True
                    break

        # for index, group in enumerate(groups):
        #     print('Group ' + str(index + 1) + ': ' + str([p.get('Student ID') for p in groups[index]]))
        # print(str([p.get('Student ID') for p in people]))
        # print('***************************************************')

        if len(people) == 0:
            numPerTeam = [len(i) for i in groups]
            if all(check >= minNumPerTeam for check in numPerTeam):
                done = True


###### Get Mean Score of Groups ######


def getMean():
    score = []
    for group in groups:
        score.append(method(group))
    return statistics.mean(score)


###### Get Variance Score of Groups ######


def getVariance():
    score = []
    for group in groups:
        score.append(method(group))
    return statistics.variance(score)


###### Evaluate All Iterations ######
# obtain the mean and variance of all iterations
# sort the mean and variance separate and assign a rank number to each
# iteration with the lowest sum of mean rank and variance rank will be selected and returned


def evaluate(means, variances):
    m = {k: v for k, v in enumerate(means)}
    v = {k: v for k, v in enumerate(variances)}

    mSorted = sorted(m.items(), key=lambda kv: (kv[1], kv[0]))
    vSorted = sorted(v.items(), key=lambda kv: (kv[1], kv[0]))

    scoreList = [0] * len(means)

    for idx, val in enumerate(mSorted):
        scoreList[val[0]] += idx

    for idx, val in enumerate(vSorted):
        scoreList[val[0]] += idx

    return scoreList.index(min(scoreList))


###### Exports the File ######
# exports to the specified directory with specified filename
# default exports to the .exe directory as export.xlsx


def export(filename, i, dataFrame):
    export = pd.DataFrame()

    for index, group in enumerate(dataFrame):
        tempDf = pd.DataFrame.from_dict(group)
        tempDf['Group'] = index + 1
        export = pd.concat([export, tempDf], ignore_index=True)

    export = export.drop(columns=categoryCols +
                         selectedQuartileCols)  # drop unwanted cols
    export = export.set_index(indexCol)
    if not filename:
        print('./export' + str(i) + '.xlsx')
        export.to_excel('./export' + str(i) + '.xlsx')
    else:
        print(filename + str(i) + '.xlsx')
        export.to_excel(filename + str(i) + '.xlsx')


###### Clear All Variables ######
# clear the script variables for re-generating the groups


def clear():
    global df
    global quartileCols
    global categoryCols
    global normalizer
    global groups

    df = df.drop(columns=quartileCols+categoryCols)
    quartileCols.clear()
    categoryCols.clear()
    normalizer.clear()
    groups.clear()


###### Main Function ######
# called by the interface.py file and receives the inputs
# assign the inputs to the variables in the script and run the above functions


def main(a, b, c, d, e, f, g, h, i, j, k):
    global df
    global indexCol
    global seedCol
    global selectedCategoryCols
    global categoryWeights
    global selectedQuartileCols
    global quartileWeights
    global numOfTeams
    global iterations
    global selectTop

    start_time = time.time()

    importFile = a
    indexCol = b
    seedCol = c
    selectedCategoryCols = d
    categoryWeights = e
    selectedQuartileCols = f
    quartileWeights = g
    numOfTeams = h
    iterations = i
    selectTop = j

    if importFile.endswith('.csv'):
        df = pd.read_csv(importFile)  # import csv file
    elif importFile.endswith('.xls') or importFile.endswith('.xlsx'):
        df = pd.read_excel(importFile)  # import excel file

    getQuartiles()  # convert quartile cols
    getCategories()  # convert category cols

    means = []
    variances = []
    dataFrames = []

    for i in range(iterations):
        if i % 10 == 9:
            print('Iteration: ' + str(i+1))
        if not seedCol:
            getGroupings(None)
        else:
            getGroupings(seedCol[0])
        means.append(float(round(Decimal(getMean()), 2)))
        variances.append(float(round(Decimal(getVariance()), 2)))
        dataFrames.append(groups.copy())

    for i in range(selectTop):
        idx = evaluate(means, variances)
        tempGroup = dataFrames[idx]
        try:
            export(k, i + 1, tempGroup)
        except Exception as e:
            print(str(e))
            clear()
            return False
        for index, group in enumerate(tempGroup):
            print('Group ' + str(index + 1) + ': ' +
                  str([p.get('Student ID') for p in tempGroup[index]]))
        print('Mean Diversity Score: ' + str(means[idx]))
        print('Variance Diversity Score: ' + str(variances[idx]))
        print('***************************************************')
        del means[idx]
        del variances[idx]
        del dataFrames[idx]

    clear()

    print("--- %s seconds ---" % (time.time() - start_time))
    return True
