"""
Copyright 2021 Fabian H. Schneider
"""
import colorama

github_token = ""


class Main:
    def __init__(self):
        pass

    def execute(self):
        colorama.init(autoreset=True)

    @staticmethod
    def print_header(string, color=''):
        bar = (len(string) + 4) * "#"
        print(color + bar + "\n# " + string + " #\n" + bar)


if __name__ == '__main__':
    superelixier_updater = Main()
    superelixier_updater.execute()
