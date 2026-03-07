from latex.vertical_operation_formatter import VerticalFormatter

formatter = VerticalFormatter()

# equation1: 14x + 7y = 49
# equation2: 4x - 7y = 41

eq1 = (14,7,49)
eq2 = (4,-7,41)

result = formatter.add_equations(eq1,eq2)

print(result)