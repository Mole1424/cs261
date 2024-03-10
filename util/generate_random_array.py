from random import random
from sys import argv


def rand(a: float, b: float) -> float:
    return random() * (b - a) + a


if __name__ == "__main__":
    try:
        lower = float(argv[1])
        upper = float(argv[2])
        count = int(argv[3])
    except Exception as e:
        print("Arguments: min max count")
        print(e)
        exit(1)

    print([rand(lower, upper) for _ in range(count)])
