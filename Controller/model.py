import modelBuilder as mb
from student import Student
import random


def initialize():
    '''

    '''
    data, pairs = mb.importData()
    distributions = mb.distributionBuilder(data)

    studentData = mb.getStudentData(data)
    student = Student(studentData)
    student.nextQ(data, pairs, distributions)

    return student, data, pairs, distributions
