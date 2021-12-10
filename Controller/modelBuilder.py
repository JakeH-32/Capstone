import pandas as pd
import numpy as np
import random

def getStudentData(data):
    stud = "Stu_fe96fe63d83aa63c4ec667167fc7f1ce"
    df = data[["step", "problem_id", "stud_id", "duration", "hint", "incorrect", "correct"]]
    newdf = df[df["stud_id"] == stud]
    studentData = newdf.iloc[0:10, :]
    return studentData


def importData():
    # Read in the CSVs, select variables, combine
    raw_data04 = pd.read_csv("2004-WPI-Assistments-Math.csv",low_memory=False)
    raw_data056 = pd.read_csv("2005-06-WPI-Assistments-Math.csv",low_memory=False)
    raw_data056["problem_id"] = raw_data056["problem_id"] + max(raw_data04.problem_id)
    raw_data = pd.concat([raw_data056,raw_data04])
    data = raw_data[["stud_id","duration","problem_id","step","attempt_num", "last_attempt","outcome","input"]]
    data.reset_index(drop=True, inplace=True)

    # Create binary variables for hint, correct, incorrect
    data.loc[:,"hint"] = np.where(data["outcome"] == "HINT",1,0)
    data.loc[:,"correct"] = np.where(data["outcome"] == "CORRECT",1,0)
    data.loc[:,"incorrect"] = np.where(data["outcome"] == "INCORRECT",1,0)

    # Filter + clean data
    data = data[data["duration"] != '.']
    data.loc[:,"duration"] = data["duration"].astype(np.float64)

    correct = data[data['outcome'] == "CORRECT"]
    uniqueCorrect = correct.drop_duplicates(subset=['problem_id'])
    pairs = uniqueCorrect[["problem_id", "input"]]
    data = data[data.problem_id.isin(pairs.problem_id)]

    import warnings
    warnings.filterwarnings('ignore')

    return data, pairs


def chi2lower(x):
    ''' Calculates the chi-squared distribution lower bound

    Parameters:
    x (float64): A # of incorrect, # of hints, or a duration

    Returns:
    float64: Returns the lower bound of the chi-squared distribution
    '''
    return np.mean(x) - np.std(x)/4


def chi2upper(x):
    ''' Calculates the chi-squared distribution upper bound

    Parameters:
    x (float64): A # of incorrect, # of hints, or a duration

    Returns:
    float64: Returns the upper bound of the chi-squared distribution
    '''
    return np.mean(x) + np.std(x)/2


def distributionBuilder(data):
    # group the problems and students together to get the sum of each variable for each question
    df = data[["problem_id", "duration", "hint", "stud_id","incorrect"]].groupby(["problem_id","stud_id"]).sum()
    problemDistsLower = df.groupby(["problem_id"]).agg(chi2lower)
    problemDistsUpper = df.groupby(["problem_id"]).agg(chi2upper)
    problemDistsLower.rename(columns={'duration': 'durationLower', 'hint': 'hintLower', 'incorrect': 'incorrectLower'}, inplace=True)
    problemDistsUpper.rename(columns={'duration': 'durationUpper', 'hint': 'hintUpper', 'incorrect': 'incorrectUpper'}, inplace=True)
    problemDists = pd.concat([problemDistsLower, problemDistsUpper], axis=1)

    return problemDists


def meanWithoutOutliers(x):
    cutoff = np.percentile(x, 90)
    outliersRemoved = x[x < cutoff]
    if len(outliersRemoved) != 0:
        mean = outliersRemoved.mean()
    else:
        mean = x.mean()
    return mean


def difficulty(data):
    df = data.groupby(["problem_id", "stud_id"], as_index=False).sum()
    question_means = df[["problem_id", "duration", "hint", "incorrect"]].groupby(["problem_id"]).agg(
        meanWithoutOutliers)
    normalized_duration = (question_means.duration - min(question_means.duration)) / (
                max(question_means.duration) - min(question_means.duration))
    normalized_incorrect = (question_means.incorrect - min(question_means.incorrect)) / (
                max(question_means.incorrect) - min(question_means.incorrect))
    normalized_hint = (question_means.hint - min(question_means.hint)) / (
                max(question_means.hint) - min(question_means.hint))
    question_means["duration"] = normalized_duration
    question_means["incorrect"] = normalized_incorrect
    question_means["hint"] = normalized_hint
    question_means["difficulty"] = (normalized_duration + normalized_hint + normalized_incorrect) / 3
    normalized_diff = (question_means.difficulty - min(question_means.difficulty)) / (
                max(question_means.difficulty) - min(question_means.difficulty))
    question_means["difficulty"] = normalized_diff
    difficulty_values = question_means[["difficulty"]].sort_values(["difficulty"]).reset_index()
    return difficulty_values


def increaseDifficulty(lastQ_id, difficulty_values):
    diff = float(difficulty_values.loc[difficulty_values.problem_id == lastQ_id].difficulty)
    try:
        greaterDiff = difficulty_values.loc[difficulty_values['difficulty'] > diff].reset_index().drop(["index"], axis=1)
        nextQ = int(greaterDiff.iloc[int(np.ceil(len(greaterDiff) * .33))].problem_id)
    except:
        nextQ = maintainDifficulty(lastQ_id, difficulty_values)
    return nextQ


def reduceDifficulty(lastQ_id, difficulty_values):
    diff = float(difficulty_values.loc[difficulty_values.problem_id == lastQ_id].difficulty)
    try:
        lesserDiff = difficulty_values.loc[difficulty_values['difficulty'] < diff].reset_index().drop(["index"], axis=1)
        nextQ = int(lesserDiff.iloc[int(np.ceil(len(lesserDiff) * .66))].problem_id)
    except:
        nextQ = maintainDifficulty(lastQ_id, difficulty_values)
    return nextQ


def maintainDifficulty(lastQ_id, difficulty_values):
    import random
    diff = float(difficulty_values.loc[difficulty_values.problem_id == lastQ_id].difficulty)
    index = difficulty_values.loc[difficulty_values.problem_id == lastQ_id].index[0]
    percent = int(np.ceil(len(difficulty_values) * .025))
    if index < percent:
        nextQIndex = random.randint(0, index - 1)
        nextQ = int(difficulty_values.iloc[nextQIndex].problem_id)
    elif index > len(difficulty_values) - percent:
        nextQIndex = random.randint(index + 1, len(difficulty_values))
        nextQ = int(difficulty_values.iloc[nextQIndex].problem_id)
    else:
        viableQuestions = difficulty_values[index - percent: index + percent]
        nextQ = int(random.choice(viableQuestions.problem_id.values))
    return nextQ


def nextQuestion(lastQ_id, questionData, pairs, problemDists, difficulty_values, data):
    bounds = problemDists.loc[problemDists.index == lastQ_id]

    if questionData.incorrect < bounds.incorrectLower.values[0] and questionData.hint < bounds.hintLower.values[
        0] and questionData.duration < bounds.durationLower.values[0]:
        nextQ = increaseDifficulty(lastQ_id, difficulty_values)
    elif questionData.incorrect < bounds.incorrectLower.values[0] and questionData.hint < bounds.hintLower.values[
        0] and questionData.duration > bounds.durationUpper.values[0]:
        nextQ = maintainDifficulty(lastQ_id, difficulty_values)
    elif questionData.incorrect < bounds.incorrectLower.values[0] and questionData.hint > bounds.hintUpper.values[
        0] and questionData.duration < bounds.durationLower.values[0]:
        nextQ = reduceDifficulty(lastQ_id, difficulty_values)
    elif questionData.incorrect < bounds.incorrectLower.values[0] and questionData.hint > bounds.hintUpper.values[
        0] and questionData.duration > bounds.durationUpper.values[0]:
        nextQ = maintainDifficulty(lastQ_id, difficulty_values)
    elif questionData.incorrect > bounds.incorrectUpper.values[0] and questionData.hint < bounds.hintLower.values[
        0] and questionData.duration < bounds.durationLower.values[0]:
        nextQ = reduceDifficulty(lastQ_id, difficulty_values)
    elif questionData.incorrect > bounds.incorrectUpper.values[0] and questionData.hint < bounds.hintLower.values[
        0] and questionData.duration > bounds.durationUpper.values[0]:
        nextQ = reduceDifficulty(lastQ_id, difficulty_values)
    elif questionData.incorrect > bounds.incorrectUpper.values[0] and questionData.hint > bounds.hintUpper.values[
        0] and questionData.duration < bounds.durationLower.values[0]:
        nextQ = reduceDifficulty(lastQ_id, difficulty_values)
    elif questionData.incorrect > bounds.incorrectUpper.values[0] and questionData.hint > bounds.hintUpper.values[
        0] and questionData.duration > bounds.durationUpper.values[0]:
        nextQ = reduceDifficulty(lastQ_id, difficulty_values)
    else:
        nextQ = maintainDifficulty(lastQ_id, difficulty_values)
    problem = data[data["problem_id"] == nextQ].iloc[0]["step"].split(':')[-1].split("?")[0] + "?"
    answer = pairs[pairs["problem_id"] == nextQ].iloc[0][1]
    return nextQ, problem, answer


def startingQ(data, pairs):
    problemNum = random.choice(pairs.problem_id.values.tolist())
    problem = data[data["problem_id"] == problemNum].iloc[0]["step"].split(':')[-1].split("?")[0] + "?"
    answer = pairs[pairs["problem_id"] == problemNum].iloc[0][1]
    return problemNum, problem, answer