import pandas as pd
import numpy as np
import random
import math
'''
Unused function ----------------

def getStudentData(data):
    stud = "Stu_fe96fe63d83aa63c4ec667167fc7f1ce"
    df = data[["step", "problem_id", "stud_id", "duration", "hint", "incorrect", "correct"]]
    newdf = df[df["stud_id"] == stud]
    studentData = newdf.iloc[0:10, :]
    return studentData
'''

def timefunction(series):
    ''' Calculates the total time a student spent on a problem

        Parameters:
        series (pandas series): Series of datetime objects

        Returns:
        dur (float): The amount of time a student took ok a particular problem
    '''
    series = series.sort_values()
    length = len(series)
    if length == 1:
        dur = 0
    else:
        duration = series.iloc[length - 1] - series.iloc[0]
        dur = duration.total_seconds() / 60
        if dur > 60:
            dur = 60
    return dur


def importData():
    '''Returns the dataset and question answer pairs

       Returns:
       data (DataFrame): Contains rows of student responses with all the variables of interest
       pairs (DataFrame): Contain each problem id and its answer
    '''
    df = pd.read_csv('data.csv')
    cleanData = convertSQLtoClean(df, True)
    return cleanData


def convertSQLtoClean(df, original=False):
    df.Time = pd.to_datetime(df.Time)  # change time to datetime object
    data = df.drop(['Sourcehash'], axis=1)  # drop unneeded hash
    # Change incorrect, hint, and correct to binary features
    data.loc[:, "incorrect"] = np.where(data['Score'] == 0, 1, 0)
    data.loc[:, "hint"] = np.where((data['Score'] > 0) & (data['Score'] < 100), 1, 0)
    data.loc[:, "correct"] = np.where((data['Score'] == 100), 1, 0)
    cleanData = data
    if original:
        # Find indices where score is less than 100
        index = data.index
        condition = data['Score'] < 100  # Boolean for when students score less than a 100
        not100Indices = index[condition]  # Index of all submissions where students score less than a 100
        # Find indices where score is 100, but drop the duplicates
        data100s = data.loc[data['Score'] == 100]
        sortedData = data100s.sort_values('Time', axis=0, ascending=True)
        dataNoDups = pd.DataFrame(data100s, columns=['Stud_ID', 'Topic', 'Score']).drop_duplicates()
        indices = dataNoDups.index
        i = indices.append(not100Indices)
        cleanData = data.iloc[i]
    correctnessData = cleanData[["Stud_ID", "Topic", "incorrect", "hint"]].groupby(
        ["Stud_ID", "Topic"]).sum().reset_index()
    # Use the time function to find the time per problem for each student
    subsetData = cleanData[['Stud_ID', 'Topic', 'Time']]
    timeData = subsetData.groupby(['Stud_ID', 'Topic']).agg(func=timefunction).reset_index()
    # Merge the correctness data with the time data to get the finished dataset
    final_df = pd.merge(correctnessData, timeData, how='left', left_on=['Stud_ID', 'Topic'],
                        right_on=['Stud_ID', 'Topic'])
    final = final_df.rename(columns={'Stud_ID': "stud_id", "Topic": 'problem_id', "Time": "duration"})

    return final


def chi2lower(x):
    ''' Calculates the chi-squared distribution lower bound

    Parameters:
    x (float64): A # of incorrect, # of hints, or a duration

    Returns:
    float64: Returns the lower bound of the chi-squared distribution
    '''
    cutoff = np.percentile(x, 90)
    return max(np.mean(cutoff) - np.std(cutoff)/4, 0)


def chi2upper(x):
    ''' Calculates the chi-squared distribution upper bound

        Parameters:
        x (float64): A # of incorrect, # of hints, or a duration

        Returns:
        float64: Returns the upper bound of the chi-squared distribution
    '''
    cutoff = np.percentile(x, 90)
    return np.mean(cutoff) + np.std(cutoff)/2


def distributionBuilder(df):
    ''' Calculates the chi-squared distribution bounds for each problem id

        Parameters:
        data (DataFrame): Contains rows of student responses with all the variables of interest

        Returns:
        problemDists (DataFrame): Contains the bounds for hint, incorrect, and duration for each problem
    '''
    # group the problems and students together to get the sum of each variable for each question
    problemDistsLower = df.groupby(["problem_id"]).agg(chi2lower)  # creates the lower bound dists
    problemDistsUpper = df.groupby(["problem_id"]).agg(chi2upper)  # creates the upper bound dists

    # rename columns so we can combine the upper and lower distributions
    problemDistsLower.rename(columns={'duration': 'durationLower', 'hint': 'hintLower', 'incorrect': 'incorrectLower'}, inplace=True)
    problemDistsUpper.rename(columns={'duration': 'durationUpper', 'hint': 'hintUpper', 'incorrect': 'incorrectUpper'}, inplace=True)
    problemDists = pd.concat([problemDistsLower, problemDistsUpper], axis=1)  # make into one df

    return problemDists


def meanWithoutOutliers(x):
    ''' Calculates the mean of the given data after taking out the highest 10% of the the data

        Parameters:
        x (numpy series): Series of duration, # hints, and # incorrects

        Returns:
        mean (float): Represents the mean of the question's duration, # hints, and # incorrects per person
    '''
    # cut off the most extreme 10% of the data
    cutoff = np.percentile(x, 90)
    outliersRemoved = x[x < cutoff]
    if len(outliersRemoved) != 0:  # as long as there is data
        mean = outliersRemoved.mean()  # take the mean
    else:  # if removing the outliers removes all the data ...
        mean = x.mean()  # take the mean of the original data
    return mean


def difficulty(data):
    ''' Calculates the student perceived difficulty for each question

        Parameters:
        data (DataFrame): Contains rows of student responses with all the variables of interest

        Returns:
        difficulty_values (DataFrame): Represents the mean of the question's duration, # hints, and # incorrects per person
    '''
    # each index (problem and student) contains info on an individual student and an individual problem
    df = data.groupby(["problem_id", "stud_id"], as_index=False).sum()
    question_means = df[["problem_id", "duration", "hint", "incorrect"]].groupby(["problem_id"]).agg(
        meanWithoutOutliers)  # take the mean (without outliers) of the duration, hint, and incorrect for each prob

    # normalize the duration, incorrect, and hint between 0 and 1
    normalized_duration = (question_means.duration - min(question_means.duration)) / (
                max(question_means.duration) - min(question_means.duration))
    normalized_incorrect = (question_means.incorrect - min(question_means.incorrect)) / (
                max(question_means.incorrect) - min(question_means.incorrect))
    normalized_hint = (question_means.hint - min(question_means.hint)) / (
                max(question_means.hint) - min(question_means.hint))

    # throw means into a dataframe
    question_means["duration"] = normalized_duration
    question_means["incorrect"] = normalized_incorrect
    question_means["hint"] = normalized_hint

    # take the mean of all three metrics to get the overall "difficulty", then normalize between 0 and 1
    question_means["difficulty"] = (normalized_duration + normalized_hint + normalized_incorrect) / 3
    normalized_diff = (question_means.difficulty - min(question_means.difficulty)) / (
                max(question_means.difficulty) - min(question_means.difficulty))
    question_means["difficulty"] = normalized_diff

    # sort difficulties in ascending order
    difficulty_values = question_means[["difficulty"]].sort_values(["difficulty"]).reset_index()
    return difficulty_values


def increaseDifficulty(lastQ_id, difficulty_values):
    ''' Chooses a question of greater difficulty than the one the student just completed

        Args:
            lastQ_id (int): The question ID of the last question that the student completed
            difficulty_values (DataFrame): Represents the mean of the question's duration, # hints, and # incorrects per person

        Returns:
            nextQ (int): The question ID of the next question that the tutor will ask the student
    '''

    # get the difficulty value of the last question completed
    diff = float(difficulty_values.loc[difficulty_values.problem_id == lastQ_id].difficulty)
    index = difficulty_values.loc[difficulty_values.problem_id == lastQ_id].index[0]  # find Q index
    questionsFromCurrent = 3  # Initializing the range of questions from the current
    if index >= len(difficulty_values) - questionsFromCurrent:
        nextQ = maintainDifficulty(lastQ_id, difficulty_values)  # if none easier, maintain difficulty
    else:
        # look at all questions with lesser difficulty than the last completed Q
        greaterDiff = difficulty_values.loc[difficulty_values['difficulty'] > diff].reset_index().drop(["index"], axis=1)
        # choose a question that is a third of the way from the last Q difficulty to the easiest question difficulty
        nextQ = greaterDiff.iloc[int(np.ceil(len(greaterDiff) * .33)) - 1].problem_id

    return nextQ


def reduceDifficulty(lastQ_id, difficulty_values):
    '''Chooses a question of lesser difficulty than the one the student just completed

    Args:
        lastQ_id (int): The question ID of the last question that the student completed
        difficulty_values (DataFrame): Represents the mean of the question's duration, # hints, and # incorrects per person

    Returns:
        nextQ (int): The question ID of the next question that the tutor will ask the student

    '''
    # get the difficulty value of the last question completed
    diff = float(difficulty_values.loc[difficulty_values.problem_id == lastQ_id].difficulty)
    index = difficulty_values.loc[difficulty_values.problem_id == lastQ_id].index[0]  # find Q index
    questionsFromCurrent = 3  # Initializing the range of questions from the current
    if index < questionsFromCurrent:
        nextQ = maintainDifficulty(lastQ_id, difficulty_values)  # if none easier, maintain difficulty
    else:
        # look at all questions with lesser difficulty than the last completed Q
        lesserDiff = difficulty_values.loc[difficulty_values['difficulty'] < diff].reset_index().drop(["index"], axis=1)
        # choose a question that is a third of the way from the last Q difficulty to the easiest question difficulty
        nextQ = lesserDiff.iloc[int(np.ceil(len(lesserDiff) * .66))].problem_id

    return nextQ


def maintainDifficulty(lastQ_id, difficulty_values):
    '''Chooses a question of a relatively similar difficulty than the one the student just completed

    Args:
        lastQ_id (int): The question ID of the last question that the student completed
        difficulty_values (DataFrame): Represents the mean of the question's duration, # hints, and # incorrects per person

    Returns:
        nextQ (int): The question ID of the next question that the tutor will ask the student
    '''
    import random
    # get the difficulty value of the last question completed
    diff = float(difficulty_values.loc[difficulty_values.problem_id == lastQ_id].difficulty)
    index = difficulty_values.loc[difficulty_values.problem_id == lastQ_id].index[0]  # find Q index
    questionsFromCurrent = len(diff)*.05  # Initializing the range of questions from the current
    if index < questionsFromCurrent:  # if the index has VERY few questions easier
        nextQIndex = index + 1  # give the next hardest question since you're already at the easiest
        nextQ = difficulty_values.iloc[nextQIndex].problem_id  # get the problem ID of the next question
    elif index >= len(difficulty_values) - questionsFromCurrent:  # if you're already at the hardest questions
        nextQIndex = index - 1 # choose the question that is the next easiest Q
        nextQ = difficulty_values.iloc[nextQIndex].problem_id # get the problem ID of the next question
    else:  # if the question is not that close to the easiest or hardest question
        viableQuestions = difficulty_values[index - questionsFromCurrent: index + questionsFromCurrent]
        viableQuestions.drop(index=index)
        nextQ = random.choice(viableQuestions.problem_id.values)
    return nextQ


def nextQuestion(lastQ_id, difficulty_values, problemDists, questionData):
        '''Chooses the next question ID based on how they answered

        Args:
            lastQ_id (int): the ID of the question the student just answered
            questionData (DF): rows of the student response data for each attempt
            pairs (DF): question answer pairs
            problemDists (DF): the distributions of overall question duration, number of incorrects, and hints
            difficulty_values (DF): problem IDs and their difficulties in ascending order
            data (DF): the entire original data set

        Returns:
            nextQ: the ID of the question the student will attempt next
            problem: the text of the problem the student will attempt next
            answer: the answer to the problem the student will attempt next
        '''
        # find the question distribution for the question the student just answered
        bounds = problemDists.loc[problemDists.index == lastQ_id]
        nextQ = increaseDifficulty(lastQ_id, difficulty_values)

        # Iterates through an if-else tree derived from our seminal paper "Effort Based Tutoring"
        # The tree compares the last question's data with the question's distributions and decides to maintain, increase,
        # or decrease problem difficulty for the next question asked by the tutor
        # if questionData.incorrect[0] < bounds.incorrectLower.values[0] and questionData.hint[0] < bounds.hintLower.values[
        #     0] and questionData.duration[0] < bounds.durationLower.values[0]:
        #     nextQ = increaseDifficulty(lastQ_id, difficulty_values)
        # elif questionData.incorrect[0] < bounds.incorrectLower.values[0] and questionData.hint[0] < bounds.hintLower.values[
        #     0] and questionData.duration[0] > bounds.durationUpper.values[0]:
        #     nextQ = maintainDifficulty(lastQ_id, difficulty_values)
        # elif questionData.incorrect[0] < bounds.incorrectLower.values[0] and questionData.hint[0] > bounds.hintUpper.values[
        #     0] and questionData.duration[0] < bounds.durationLower.values[0]:
        #     nextQ = reduceDifficulty(lastQ_id, difficulty_values)
        # elif questionData.incorrect[0] < bounds.incorrectLower.values[0] and questionData.hint[0] > bounds.hintUpper.values[
        #     0] and questionData.duration[0] > bounds.durationUpper.values[0]:
        #     nextQ = maintainDifficulty(lastQ_id, difficulty_values)
        # elif questionData.incorrect[0] > bounds.incorrectUpper.values[0] and questionData.hint[0] < bounds.hintLower.values[
        #     0] and questionData.duration[0] < bounds.durationLower.values[0]:
        #     nextQ = reduceDifficulty(lastQ_id, difficulty_values)
        # elif questionData.incorrect[0] > bounds.incorrectUpper.values[0] and questionData.hint[0] < bounds.hintLower.values[
        #     0] and questionData.duration[0] > bounds.durationUpper.values[0]:
        #     nextQ = reduceDifficulty(lastQ_id, difficulty_values)
        # elif questionData.incorrect[0] > bounds.incorrectUpper.values[0] and questionData.hint[0] > bounds.hintUpper.values[
        #     0] and questionData.duration[0] < bounds.durationLower.values[0]:
        #     nextQ = reduceDifficulty(lastQ_id, difficulty_values)
        # elif questionData.incorrect[0] > bounds.incorrectUpper.values[0] and questionData.hint[0] > bounds.hintUpper.values[
        #     0] and questionData.duration[0] > bounds.durationUpper.values[0]:
        #     nextQ = reduceDifficulty(lastQ_id, difficulty_values)
        # else:
        #     nextQ = maintainDifficulty(lastQ_id, difficulty_values)

        return nextQ


def formatQandA(data, pairs, nextQ):
    ''' Formats the question based on the format of the data

    Args:
        data (DF): the entire original data set
        pairs (DF): question answer pairs
        nextQ: the ID of the question the student will attempt next

    Returns:
        problem: the text of the problem the student will attempt next
        answer: the answer to the problem the student will attempt next

    '''
    # Format the problem
    problem = data[data["problem_id"] == nextQ].iloc[0]["step"].split(':')[-1].split("?")[0] + "?"
    # Format the answer
    answer = pairs[pairs["problem_id"] == nextQ].iloc[0][1]

    return problem, answer


def startingQ(data, questionDifficulty):
    ''' Gets starting question

    Args:
        data (DF): the entire original data set
        questionDifficulty (DF): a dataframe of each question with its correspond 0-1 difficulty

    Returns:
        problem: the problem title of the next assigned problem

    '''
    problems = len(questionDifficulty)
    problemNum = int(math.floor(problems/2))
    startingProblem = questionDifficulty.iloc[problemNum].problem_id

    return startingProblem