import sys
import keyboard
from time import sleep
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QDialog, QApplication
from PyQt6 import QtWidgets

QScreen = "View/QuestionScreen.ui"
CScreen = "View/CorrectScreen_2.ui"
IScreen = "View/IncorrectScreen_2.ui"
questiontext = "This is the question"


# QuestionScreen Class
# Functions: gotoresult, showhint
class QuestionScreen(QDialog):
    def __init__(self):
        super(QuestionScreen, self).__init__()
        loadUi(QScreen, self)
        self.QuestionLabel.setText(questiontext)
        self.submit.clicked.connect(self.gotoresult)
        self.hintButton.clicked.connect(self.showhint)

        if keyboard.is_pressed("enter"):
            self.gotoresult()

    # Name: gotoresult
    # Params: self, question
    # Compares text user inputs to the question answer.
    # Shows corresponding screen for correct or incorrect.
    def gotoresult(self):
        # Temporary answer
        questionanswer = "1"
        # Get user answer from answerBox
        useranswer = self.answerBox.text()

        # If empty
        if useranswer == "":
            sleep(.1)
            # Tell student to enter an answer
            self.emptyans.setText("Please enter an answer")
        # Else if correct answer, show correct screen
        elif useranswer == questionanswer:
            sleep(.1)
            correct = CorrectScreen()
            widget.addWidget(correct)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        # Else must be incorrect, show incorrect screen
        else:
            sleep(.1)
            wrong = IncorrectScreen()
            widget.addWidget(wrong)
            widget.setCurrentIndex(widget.currentIndex() + 1)

    # Name: showhint
    # Params: self, question
    def showhint(self):
        sleep(.1)
        # Temporary hint (will be dynamic from question object later)
        hinttext = "Here is the hint for this question!"
        # Set hintLabel text to hintText
        self.hintLabel.setText(hinttext)


# Name: IncorrectScreen
# Functions: __init__, return to question
class IncorrectScreen(QDialog):
    # Initialize incorrect screen
    def __init__(self):
        super(IncorrectScreen, self).__init__()
        loadUi(IScreen, self)
        self.submit.clicked.connect(self.returntoquestion)

    # Name: returntoquestion
    # Params: self
    # Returns to question screen from incorrect screen
    def returntoquestion(self):
        sleep(.1)
        question = QuestionScreen()
        widget.addWidget(question)
        widget.setCurrentIndex(widget.currentIndex() + 1)

# Name: CorrectScreen
# Functions: __init__, return to question
class CorrectScreen(QDialog):
    # Initialize correct screen
    def __init__(self):
        super(CorrectScreen, self).__init__()
        loadUi(CScreen, self)
        self.submit.clicked.connect(self.returntoquestion)

    # Name: returntoquestion
    # Params: self
    # Returns to question screen from incorrect screen
    def returntoquestion(self):
        sleep(.1)
        question = QuestionScreen()
        widget.addWidget(question)
        widget.setCurrentIndex(widget.currentIndex() + 1)


# Main
app = QApplication(sys.argv)
question = QuestionScreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(question)
widget.setFixedHeight(300)
widget.setFixedWidth(400)
widget.show()
try:
    sys.exit(app.exec())
except:
    print("Exiting")
