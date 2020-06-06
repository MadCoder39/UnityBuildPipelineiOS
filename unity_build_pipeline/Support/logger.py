GREEN = '\x1b[32m'
YELLOW = '\033[93m'
RED = '\033[91m'
WHITE = '\x1b[32m'
RESET = '\x1b[0m'

def colority_string(string, color=RESET):
    return color + string + RESET


def color_print(string, color=RESET):
    print(colority_string(string, color))


def color_raw_input(prompt, color=RESET):
    return input(colority_string(prompt, color)).strip()
