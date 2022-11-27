"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import re

from cleo.commands.command import Command
from cleo.helpers import argument

from superelixier import configuration
from superelixier.definition import Definition

UPDATE_TRIGGER = {"update", "no_version_file", "not_installed"}


class Search(Command):
    # cleo
    name = "search"
    description = "Search the local definition cache for apps whose name or gist contains <query>"
    arguments = [argument(name="query", description="What to search for")]

    def handle(self) -> int:
        qry_re = re.compile(re.escape(self.argument("query")), re.IGNORECASE)
        hits = {}
        w_name = 0
        w_gist = 0
        for app in configuration.definitions.values():
            app: Definition
            match_name = qry_re.search(app.info.name)
            match_gist = qry_re.search(app.info.gist)
            if match_name or match_gist:
                name, gist = app.info.name, app.info.gist
                w_name, w_gist = max(l_name := len(name), w_name), max(l_gist := len(gist), w_gist)
                if match_name:
                    name = name.replace(match_name.group(), f"<fg=cyan>{match_name.group()}</>")
                if match_gist:
                    gist = gist.replace(match_gist.group(), f"<fg=cyan>{match_gist.group()}</>")
                hits[app.info.name] = (name, gist, l_name, l_gist)
        if hits:
            boundary = f"+-{'-'*w_name}---{'-'*w_gist}-+"
            self.line(boundary)
            for name, gist, l_name, l_gist in [hits[k] for k in sorted(hits, key=str.casefold)]:
                self.line(f"| {name}{' '*(w_name-l_name)} | {gist}{' '*(w_gist-l_gist)} |")
            self.line(boundary)
            return 0
        else:
            self.line_error("Sorry, nothing found!")
            return 1
