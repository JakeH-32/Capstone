import modelBuilder as mb
from student import Student
import random


def initialize():
    data, pairs = mb.importData()
    distributions = mb.distributionBuilder(data)
    questionDifficulty = mb.difficulty(data)
    problemNum, problem, answer = mb.startingQ(data, pairs)
    student = Student(problemNum, problem, answer)
    return student, data, pairs, questionDifficulty, distributions
