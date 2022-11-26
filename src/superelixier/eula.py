"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import os
import re
import textwrap

from superelixier.helper import toml
from superelixier.helper.environment import DIR_APP
from superelixier.helper.shell import clear
from superelixier.helper.terminal import exit_app

TERM_VER: int = 2
TERMS: str = """\
Superelixier 3rd-Party Notice
=============================
All apps installed using this program are subject to their respective licenses as determined by the proprietors of these
apps ('proprietors' hereafter). Inclusion of installation definitions in this software should not be seen as any
indication of affiliation of proprietors with the creator(s) of this software. This software only provide automations
for installing these apps on your local machine.

It remains your responsibility as a user of our software to adhere to the terms and licenses proprietors have set for
the software that you are asking our routines to access.

As a practical example, you may be required to purchase a license from proprietors if using proprietors' software
commercially.

As a further practical example, if you create a modified version of proprietors' software, you may be required
to disclose source code of your modified version."""


def check_terms() -> None:
    term_file = os.path.join(DIR_APP, "config", "eula.toml")
    if os.path.isfile(term_file):
        with open(term_file, "rb") as file:
            my_dict = toml.load(file)
        if "eula_version_accepted" in my_dict:
            if my_dict["eula_version_accepted"] == TERM_VER:
                return
    __show_eula()


def __show_eula() -> None:
    print(TERMS)
    challenge = input('To accept these terms, please type "agree" and confirm with ENTER:\r\n')
    if re.match(r"^agree$", challenge.casefold()):
        __accept_eula()
    else:
        print(
            textwrap.dedent(
                """\
                Cannot continue as terms were not accepted.
                If you meant to accept, make sure you only type "agree" without quotes."""
            )
        )
        exit_app(-1)


def __accept_eula() -> None:
    accepted = {"eula_version_accepted": TERM_VER, "eula_for_reference": TERMS}
    with open(os.path.join(DIR_APP, "config", "eula.toml"), "wb") as file:
        toml.dump(accepted, file)
    os.system(clear)
