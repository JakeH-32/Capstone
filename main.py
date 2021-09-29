import sys
from time import sleep

from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QDialog, QApplication
from PyQt6 import QtWidgets


class QuestionScreen(QDialog):
    def __init__(self):
        super(QuestionScreen, self).__init__()
        loadUi("QuestionScreen.ui", self)
        self.submit.clicked.connect(self.gotoresult)
        self.hintButton.clicked.connect(self.showhint)

    def gotoresult(self):
        questionanswer = "1"
        useranswer = self.answerBox.text()
        # print(useranswer)

        # Detect keystroke and remove empty ans text

        if useranswer == "":
            sleep(.1)
            self.emptyans.setText("Please enter an answer")
        elif useranswer == questionanswer:
            sleep(.1)
            correct = CorrectScreen()
            widget.addWidget(correct)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        else:
            sleep(.1)
            wrong = WrongScreen()
            widget.addWidget(wrong)
            widget.setCurrentIndex(widget.currentIndex() + 1)

    def showhint(self):
        sleep(.1)
        hinttext = "Here is the hint for this question!"
        self.hintLabel.setText(hinttext)


class WrongScreen(QDialog):
    def __init__(self):
        super(WrongScreen, self).__init__()
        loadUi("IncorrectScreen_2.ui", self)
        self.submit.clicked.connect(self.returntoquestion)

    def returntoquestion(self):
        sleep(.1)
        question = QuestionScreen()
        widget.addWidget(question)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class CorrectScreen(QDialog):
    def __init__(self):
        super(CorrectScreen, self).__init__()
        loadUi("CorrectScreen_2.ui", self)
        self.submit.clicked.connect(self.returntoquestion)

    def returntoquestion(self):
        sleep(.1)
        question = QuestionScreen()
        widget.addWidget(question)
        widget.setCurrentIndex(widget.currentIndex() + 1)



# main
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
