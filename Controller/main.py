import sys
import time
from time import sleep

import pandas as pd
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QDialog, QApplication
from PyQt6 import QtWidgets
import model
from modelBuilder import Student

QScreen = "../View/QuestionScreen.ui"
CScreen = "../View/CorrectScreen_2.ui"
IScreen = "../View/IncorrectScreen_2.ui"

# QuestionScreen Class
# Functions: gotoresult, showhint
def attempttime(initialtime, answer):
    # Sets qtime to amount of seconds between attempts
    qtime = '%.2f' % (time.time() - initialtime)
    qtimedouble = float(time.time() - initialtime)
    # Truncated to hundredths
    print("Seconds between attempts:")
    print(qtime)
    print("Answer:")
    print(answer)
    return qtimedouble


class QuestionScreen(QDialog):
    def __init__(self, start):
        self.start = start
        if self.start:
            self.data = {"duration": [], "hint": [], "incorrect": [], "correct": []}
            self.start = False
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
        # print(useranswer)

        # Detect keystroke and remove empty ans text

        if useranswer == "":
            sleep(.1)
            self.emptyans.setText("Please enter an answer")
        elif useranswer == questionanswer:
            sleep(.1)
            correct = CorrectScreen(self.initialtime)

            widget.addWidget(correct)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        else:
            sleep(.1)
            wrong = WrongScreen(self.initialtime, self.answer)
            widget.addWidget(wrong)
            widget.setCurrentIndex(widget.currentIndex() + 1)


    def showhint(self):
        sleep(.1)
        hinttext = "Here is the hint for this question!"
        data["duration"].append(attempttime(self))
        data["hint"].append(1)
        data["incorrect"].append(0)
        data["correct"].append(0)
        self.hintLabel.setText(hinttext)

    def showQuestion(self, question):
        sleep(.1)
        questiontext = question


class WrongScreen(QDialog):
    def __init__(self, initialtime, answer):
        self.initialtime = initialtime
        self.answer = answer
        super(WrongScreen, self).__init__()
        loadUi(IScreen, self)
        self.submit.clicked.connect(self.returntoquestion)


    def returntoquestion(self):
        sleep(.1)
        data["duration"].append(attempttime(self.initialtime, self.answer))
        data["hint"].append(0)
        data["incorrect"].append(1)
        data["correct"].append(0)
        question = QuestionScreen(False)
        widget.addWidget(question)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class CorrectScreen(QDialog):
    def __init__(self, initialtime):
        self.initialtime = initialtime
        super(CorrectScreen, self).__init__()
        loadUi(CScreen, self)
        self.submit.clicked.connect(self.returntoquestion)

    def returntoquestion(self):
        sleep(.1)
        data["duration"].append(attempttime(self.initialtime,"Nice Work"))
        data["hint"].append(0)
        data["incorrect"].append(0)
        data["correct"].append(1)
        df = pd.DataFrame(data)
        student.updateStudent(df)  # CURRENT ISSUE
        student.nextQ(OGdata, pairs, distributions)
        sleep(.1)
        question = QuestionScreen(True)
        widget.addWidget(question)
        widget.setCurrentIndex(widget.currentIndex() + 1)


# main
global student, OGdata, pairs, distributions, data
data = {"duration": [], "hint": [], "incorrect": [], "correct": []}
student, OGdata, pairs, distributions = model.initialize()
app = QApplication(sys.argv)
question = QuestionScreen(True)
widget = QtWidgets.QStackedWidget()
widget.addWidget(question)
widget.setFixedHeight(300)
widget.setFixedWidth(400)
widget.show()
try:
    sys.exit(app.exec())
except:
    print("Exiting")
