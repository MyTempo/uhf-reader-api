import os
import datetime
from datetime import timezone
import random

class Helpers:
    def __init__(self) -> None:
        pass

    def is_num(n):
        if isinstance(n, (int, float)):
            return True
        elif isinstance(n, str) and n.isnumeric():
            return True
        else:
            return False

    @staticmethod
    def generateRandomNum(qtd):
        return ''.join(str(random.randint(1, 9)) for _ in range(qtd))
