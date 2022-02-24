import modelBuilder as mb


def initialize():
    data = mb.importData()
    distributions = mb.distributionBuilder(data)  # build the chi-squared upper and lower bound dist for each Q
    questionDifficulty = mb.difficulty(data)  # build student perceived difficulty model
    problem = mb.startingQ(data, questionDifficulty)
    return problem, questionDifficulty, distributions  # return all that we found