import random

class oldStudent:
    def __init__(self, data):
        self.data = data
        self.means = self.data.mean()
        self.duration = self.means.duration
        self.incorrect = self.means.incorrect
        self.hint = self.means.hint
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
        import random
        EVdur = self.duration
        EVinc = self.incorrect
        EVhint = self.hint
        viableProbs = problemDists[(EVdur < problemDists["durationUpper"]) & (EVhint < problemDists["hintUpper"]) & \
                                   (problemDists["incorrectLower"] > EVinc)]
        problemNum = random.choice(viableProbs.index.values.tolist())
        self.problem = data[data["problem_id"]==problemNum].iloc[0]["step"].split(':')[-1].split("?")[0] + "?"
        answer = pairs[pairs["problem_id"]==problemNum].iloc[0][1]
        self.answer = answer


class Student:
    def __init__(self, problem_id, question, answer):
        self.problem = question
        self.answer = answer
        self.problem_id = problem_id
