import pandas as pd
import numpy as np
import random


def importData():
    # Read in the CSVs, select variables, combine
    raw_data04 = pd.read_csv("2004-WPI-Assistments-Math.csv",low_memory=False)
    raw_data056 = pd.read_csv("2005-06-WPI-Assistments-Math.csv",low_memory=False)
    raw_data056["problem_id"] = raw_data056["problem_id"] + max(raw_data04.problem_id)
    raw_data = pd.concat([raw_data056,raw_data04])
    data = raw_data[["stud_id","duration","student_response_type","problem_id","step","attempt_num",
                 "last_attempt","outcome","input","feedback"]]
    data.reset_index(drop=True, inplace=True)

    # Create binary variables for hint, correct, incorrect
    data.loc[:,"hint"] = np.where(data["outcome"] == "HINT",1,0)
    data.loc[:,"correct"] = np.where(data["outcome"] == "CORRECT",1,0)
    data.loc[:,"incorrect"] = np.where(data["outcome"] == "INCORRECT",1,0)

    # Filter + clean data
    data = data[data["duration"] != '.']
    data["duration"] = data["duration"].astype(np.float64)

    correct = data[data['outcome'] == "CORRECT"]
    uniqueCorrect = correct.drop_duplicates(subset=['problem_id'])
    pairs = uniqueCorrect[["problem_id", "input"]]
    data = data[data.problem_id.isin(pairs.problem_id)]

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

    return problemDists, df


class Student:
    def __init__(self, data):
        self.data = data
        self.means = 0
        self.problem = ""
        self.answer = ""

    def updateStudent(self, lastQ):
        self.data = self.data.append(lastQ)
        self.means = self.data.mean()
        self.duration = self.means.duration
        self.incorrect = self.means.incorrect
        self.hint = self.means.hint

    def nextQ(self, data, pairs, problemDists):
        # Determines a viable next question
        EVdur = self.duration
        EVinc = self.incorrect
        EVhint = self.hint
        viableProbs = problemDists[(EVdur < problemDists["durationUpper"]) & (EVhint < problemDists["hintUpper"]) & \
                                   (problemDists["incorrectLower"] > EVinc)]
        problemNum = random.choice(viableProbs.index.values.tolist())
        self.problem = data[data["problem_id"]==problemNum].iloc[0]["step"].split(':')[-1].split("?")[0] + "?"
        answer = pairs[pairs["problem_id"]==problemNum].iloc[0][1]
        if answer[0] in ["A","B","C","D"]:
            answer = answer[3:]
        self.answer = answer