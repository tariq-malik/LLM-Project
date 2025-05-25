# NODE: add
def add(x, y):
    return x + y

# NODE: subtract
def subtract(x, y):
    return x - y

# NODE: multiply
def multiply(x, y):
    return x * y

# NODE: divide
def divide(x, y):
    if y == 0:
        return "Error! Division by zero."
    return x / y

# NODE: calculator
# EDGES: calculator -> add, calculator -> subtract, calculator -> multiply, calculator -> divide
def calculator():
    print("Simple Calculator")
    print("Select operation:")
    print("1. Add")
    print("2. Subtract")
    print("3. Multiply")
    print("4. Divide")

    choice = input("Enter choice (1/2/3/4): ")

    if choice not in ['1', '2', '3', '4']:
        print("Invalid input")
        return

    num1_input = input("Enter first number: ")
    num2_input = input("Enter second number: ")

    # Basic validation without try-except
    if not num1_input.replace('.', '', 1).isdigit() or not num2_input.replace('.', '', 1).isdigit():
        print("Invalid number input")
        return

    num1 = float(num1_input)
    num2 = float(num2_input)

    if choice == '1':
        print(f"Result: {add(num1, num2)}")
    elif choice == '2':
        print(f"Result: {subtract(num1, num2)}")
    elif choice == '3':
        print(f"Result: {multiply(num1, num2)}")
    elif choice == '4':
        print(f"Result: {divide(num1, num2)}")

calculator()
