"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import json
import os
import re
import sys

TERM_VER = 1
TERMS = [
    "Superelixier 3rd-Party Notice\r\n",
    "==================\r\n"
    "All apps installed using this program are subject to their respective licenses as determined by the proprietors "
    "of these apps ('proprietors' hereafter). ",
    "Inclusion in this list should not be seen as any indication of affiliation of proprietors with the creator(s) of "
    "Superelixier Updater ('we' hereafter). ",
    "We only provide automation routines for installing these apps on your local machine.\r\n",
    "It remains your responsibility as a user of our software to adhere to the terms and licenses proprietors have set "
    "for the software that you are asking our routines to access.\r\n",
    "As a practical example, you may be required to purchase a license from proprietors if using proprietors' software "
    "commercially. ",
    "As a further practical example, if you create a modified version of proprietors' software, you may be required to "
    "disclose source code of your modified version.",
]


class EulaChecker:
    @staticmethod
    def check_eula():
        term_file = os.path.join(os.path.dirname(sys.argv[0]), "config", "eula.json")
        if os.path.isfile(term_file):
            with open(term_file, "r") as file:
                my_dict = json.load(file)
            if "eula_version_accepted" in my_dict:
                if my_dict["eula_version_accepted"] == TERM_VER:
                    return
        EulaChecker.__show_eula()

    @staticmethod
    def __show_eula():
        print("".join(TERMS))
        challenge = input('To accept these terms, please type "Yes, I agree" and confirm with ENTER:\r\n')
        if re.match(r"^yes,? i agree$", challenge.casefold()):
            EulaChecker.__accept_eula(TERM_VER)
        else:
            print(
                "Cannot continue as terms were not accepted. "
                'If you meant to accept, make sure you only type "yes i agree" without quotes.'
            )
            input("Press ENTER to exit.")
            sys.exit()

    @staticmethod
    def __accept_eula(version: int):
        accepted = {
            "DO NOT MODIFY MODIFY THIS FILE": "PLEASE",
            "eula_version_accepted": version,
            "eula_for_reference": [*TERMS],
        }
        with open(os.path.join(os.path.dirname(sys.argv[0]), "config", "eula.json"), "w") as file:
            json.dump(accepted, file)
        os.system("cls" if os.name == "nt" else "clear")
