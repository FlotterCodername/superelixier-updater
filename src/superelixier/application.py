"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
from cleo.application import Application

from superelixier import __version__
from superelixier.commands.check_configuration import CheckConfiguration
from superelixier.commands.check_definitions import CheckDefinitions
from superelixier.commands.install import Install
from superelixier.commands.search import Search
from superelixier.commands.self_upgrade import SelfUpgrade
from superelixier.commands.upgrade import Upgrade

DefaultCommand = Upgrade
cli = Application(name="superelixier", version=__version__)
cli.auto_exits(False)
cli.add(CheckConfiguration())
cli.add(CheckDefinitions())
cli.add(Install())
cli.add(Search())
cli.add(SelfUpgrade())
cli.add(Upgrade())
