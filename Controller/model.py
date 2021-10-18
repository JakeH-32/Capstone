import modelBuilder as mb
import random


def initialize():
    data, pairs = mb.importData()
    distributions, groupDf = mb.distributionBuilder(data)
    stud = "Stu_fe96fe63d83aa63c4ec667167fc7f1ce"
    df = data[["step", "problem_id", "stud_id","duration", "hint", "incorrect", "correct"]]
    newdf = df[df["stud_id"] == stud]
    studentData = newdf.iloc[0:10,:]
    student = mb.Student(studentData)
    questionData = newdf.iloc[11:13, :]
    student.updateStudent(questionData)
    student.nextQ(data, pairs, distributions)

    return student