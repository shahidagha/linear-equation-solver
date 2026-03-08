class EquationNumbering:

    def __init__(self):

        self.counter = 0
        self.equations = {}

    def add(self, equation):

        self.counter += 1

        number = self.counter

        self.equations[number] = equation

        return number

    def get(self, number):

        return self.equations.get(number)