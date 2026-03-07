from models.coefficient import FractionSurd

# Example: 4√5 / 3√7

num_mult = 4
num_rad = 5
den_mult = 3
den_rad = 7

fs = FractionSurd(num_mult, num_rad, den_mult, den_rad)

print("Expression:")
print(fs.display())

print("\nLaTeX:")
print(fs.to_latex())