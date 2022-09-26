import random
import string


def create_chore_name() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=20))
