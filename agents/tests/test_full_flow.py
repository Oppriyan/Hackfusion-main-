from agents.core.agent_runner import run_agent

def test_input(user_input):
    print("\n" + "="*60)
    print("INPUT:", user_input)
    result = run_agent(user_input)
    print("OUTPUT:", result)
    print("="*60 + "\n")


if __name__ == "__main__":

    # 1. Happy path order
    test_input("order 1 paracetamol")

    # 2. Inventory check
    test_input("check inventory paracetamol")

    # 3. Search medicine
    test_input("search paracetamol")

    # 4. Invalid quantity
    test_input("order 0 paracetamol")

    # 5. Unknown medicine
    test_input("order 1 unknownmedicine")

    # 6. Order status (replace 1 with real ID if needed)
    test_input("order status 1")

    # 7. Cancel order (replace 1 with real ID if needed)
    test_input("cancel order 1")
    

    # 8. Smalltalk
    test_input("hello")