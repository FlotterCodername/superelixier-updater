"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""


def definition_to_app(definition, **kwargs):
    from superelixier.definition import Definition

    if not isinstance(definition, Definition):
        raise TypeError
    match definition.repo_type:
        case "appveyor":
            from superelixier.appveyor.appveyor_app import AppveyorApp

            return AppveyorApp(definition=definition, **kwargs)
        case "github":
            from superelixier.github.github_app import GithubApp

            return GithubApp(definition=definition, **kwargs)
        case "html":
            from superelixier.html_page.html_app import HTMLApp

            return HTMLApp(definition=definition, **kwargs)
        case _:
            raise ValueError("Unknown repo type")
