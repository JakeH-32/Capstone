import sys
import time
from time import sleep

import pandas as pd
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QDialog, QApplication
from PyQt6 import QtWidgets
import model
import modelBuilder as mb

from student import Student
import fuzzywuzzy
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from modelBuilder import importData
dataframe, pairs = importData()

from modelBuilder import distributionBuilder
distributions = distributionBuilder(dataframe)

from modelBuilder import difficulty
questionDifficulty = difficulty(dataframe)

from modelBuilder import startingQ
problemNum, problem, answer = startingQ(dataframe, pairs)

from student import Student
student = Student(problemNum, problem, answer)


QScreen = "../View/QuestionScreen.ui"
CScreen = "../View/CorrectScreen_2.ui"
IScreen = "../View/IncorrectScreen_2.ui"

# QuestionScreen Class
# Functions: gotoresult, showhint
def attempttime(initialtime, endtime, answer):
    # Sets qtime to amount of seconds between attempts
    qtime = '%.2f' % (endtime - initialtime)
    qtimedouble = float(endtime - initialtime)

    # Truncated to hundredths
    print("Seconds between attempts:")
    print(qtime)
    print("Answer:")
    print(answer)
    return qtimedouble


class QuestionScreen(QDialog):
    def __init__(self, start):
        print("QuestionScreen Start: " + str(start))
        self.start = start
        if self.start:
            self.data = {"duration": [], "hint": [], "incorrect": [], "correct": []}
            self.start = False
        # initialize time
        self.initialtime = time.time()
        self.problem = student.problem
        self.answer = student.answer
        super(QuestionScreen, self).__init__()
        loadUi(QScreen, self)
        self.QuestionLabel.setText(self.problem)
        self.submit.clicked.connect(self.gotoresult)
        self.hintButton.clicked.connect(self.showhint)


    def gotoresult(self):
        questionanswer = self.answer
        useranswer = self.answerBox.text()

        # Detect keystroke and remove empty ans text

        if useranswer == "":
            sleep(.1)
            self.emptyans.setText("Please enter an answer")
        correctness = False
        try:
            useranswernum = float(useranswer)
            error = abs(float(self.answer) - useranswernum) / abs(float(self.answer))
            if error < 0.005:
                correctness = True
        except:
            ratio = fuzz.token_sort_ratio(self.answer.lower().strip(), useranswer.lower().strip())
            if ratio > 75:
                correctness = True
        if correctness:
            sleep(.1)
            correct = CorrectScreen(self.initialtime, self.data)

            widget.addWidget(correct)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        else:
            sleep(.1)
            wrong = WrongScreen(self.initialtime, self.answer, self.data)
            widget.addWidget(wrong)
            widget.setCurrentIndex(widget.currentIndex() + 1)


    def showhint(self):
        sleep(.1)
        hinttext = "Here is the hint for this question!"

        self.endtime = time.time()
        self.data["duration"].append(attempttime(self.initialtime, self.endtime, self.answer))
        self.data["hint"].append(1)
        self.data["incorrect"].append(0)
        self.data["correct"].append(0)
        self.initialtime = time.time()
        self.hintLabel.setText(hinttext)

    def showQuestion(self, question):
        sleep(.1)
        questiontext = question


class WrongScreen(QDialog):
    def __init__(self, initialtime, answer, data):
        self.initialtime = initialtime
        self.answer = answer
        self.endtime = time.time()
        self.data = data
        super(WrongScreen, self).__init__()
        loadUi(IScreen, self)
        self.submit.clicked.connect(self.returntoquestion)


    def returntoquestion(self):
        sleep(.1)
        self.data["duration"].append(attempttime(self.initialtime, self.endtime, self.answer))
        self.data["hint"].append(0)
        self.data["incorrect"].append(1)
        self.data["correct"].append(0)
        question = QuestionScreen(False)
        widget.addWidget(question)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class CorrectScreen(QDialog):
    def __init__(self, initialtime, data):
        self.data = data
        self.initialtime = initialtime
        self.endtime = time.time()
        super(CorrectScreen, self).__init__()
        loadUi(CScreen, self)
        self.submit.clicked.connect(self.returntoquestion)

    def returntoquestion(self):
        sleep(.1)
        self.data["duration"].append(attempttime(self.initialtime,self.endtime, "Nice Work"))
        self.data["hint"].append(0)
        self.data["incorrect"].append(0)
        self.data["correct"].append(1)
        self.data = pd.DataFrame(self.data)
        self.data = self.data.sum()
        print(student.problem_id)
        print(self.data)
        question_id, question, answer = mb.nextQuestion(student.problem_id, self.data, pairs, distributions, questionDifficulty, dataframe)  # Current problem
        student.problem_id = question_id
        student.problem = question
        student.answer = answer
        sleep(.1)
        question = QuestionScreen(True)
        widget.addWidget(question)
        widget.setCurrentIndex(widget.currentIndex() + 1)


# main
def main():
    app = QApplication(sys.argv)
    question = QuestionScreen(start=True)
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(question)
    widget.show()
    try:
        sys.exit(app.exec())
    except:
        print("Exiting")

if __name__ == "__main__":
    main()