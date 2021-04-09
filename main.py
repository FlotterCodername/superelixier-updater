"""
Copyright 2021 Fabian H. Schneider
"""
import colorama

from config_loader.config_loader import ConfigLoader

colorama.init(autoreset=True)


class Main:
    def __init__(self):
        configuration = ConfigLoader().configuration
        self.cfg_auth = configuration["auth"]
        self.cfg_available = configuration["available"]
        self.cfg_local = configuration["local"]
        self.github_token = self.cfg_auth["github_token"]

    def execute(self):
        pass

    @staticmethod
    def print_header(string, color=''):
        bar = (len(string) + 4) * "#"
        print(color + bar + "\n# " + string + " #\n" + bar)


if __name__ == '__main__':
    superelixier_updater = Main()
    superelixier_updater.execute()
