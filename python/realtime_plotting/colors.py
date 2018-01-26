import os

if os.name == 'nt':
    BLACK = ''
    RED = ''
    GREEN = ''
    YELLOW = ''
    BLUE = ''
    MAGENTA = ''
    CYAN = ''
    WHITE = ''

    BRIGHT_BLACK = ''
    BRIGHT_RED = ''
    BRIGHT_GREEN = ''
    BRIGHT_YELLOW = ''
    BRIGHT_BLUE = ''
    BRIGHT_MAGENTA = ''
    BRIGHT_CYAN = ''
    BRIGHT_WHITE = ''

    RESET = ''
else:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    BRIGHT_BLACK = '\033[30;1m'
    BRIGHT_RED = '\033[31;1m'
    BRIGHT_GREEN = '\033[32;1m'
    BRIGHT_YELLOW = '\033[33;1m'
    BRIGHT_BLUE = '\033[34;1m'
    BRIGHT_MAGENTA = '\033[35;1m'
    BRIGHT_CYAN = '\033[36;1m'
    BRIGHT_WHITE = '\033[37;1m'

    RESET = '\033[0m'

if __name__ == "__main__":
    ALL_COLORS_dict = {'BLACK':BLACK, 'RED':RED, 'GREEN':GREEN, 'YELLOW':YELLOW, 'BLUE':BLUE, 'MAGENTA':MAGENTA, 
                  'CYAN':CYAN, 'WHITE':WHITE, 'BRIGHT_BLACK':BRIGHT_BLACK, 'BRIGHT_RED':BRIGHT_RED, 
                  'BRIGHT_GREEN':BRIGHT_GREEN, 'BRIGHT_YELLOW':BRIGHT_YELLOW, 'BRIGHT_BLUE':BRIGHT_BLUE, 
                  'BRIGHT_MAGENTA':BRIGHT_MAGENTA, 'BRIGHT_CYAN':BRIGHT_CYAN, 'BRIGHT_WHITE':BRIGHT_WHITE, 
                  'RESET':RESET}
                  
    for key in ALL_COLORS_dict.keys():
        print "%s%s%s" % (ALL_COLORS_dict[key], key, RESET)
