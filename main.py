"""
Copyright 2021 Fabian H. Schneider
"""
import colorama


class Main:
    def __init__(self):
        pass

    def execute(self):
        colorama.init(autoreset=True)


if __name__ == '__main__':
    superelixier_updater = Main()
    superelixier_updater.execute()
