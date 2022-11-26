"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
from cleo.application import Application

from superelixier.commands.search import Search
from superelixier.commands.upgrade import Upgrade

DefaultCommand = Upgrade
cli = Application(name="superelixier-updater", version="preview")
cli.add(Upgrade())
cli.add(Search())
