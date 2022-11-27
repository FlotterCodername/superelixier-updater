"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
from cleo.commands.command import Command

from superelixier.appveyor.appveyor_app import AppveyorApp
from superelixier.generic.generic_app import GenericApp
from superelixier.github.github_app import GithubApp
from superelixier.helper.terminal import Ansi
from superelixier.html_page.html_app import HTMLApp


def definition_to_app_job(definition, **kwargs) -> GenericApp:
    from superelixier.definition import Definition

    if not isinstance(definition, Definition):
        raise TypeError
    match definition.repo_type:
        case "appveyor":

            return AppveyorApp(definition=definition, **kwargs)
        case "github":

            return GithubApp(definition=definition, **kwargs)
        case "html":

            return HTMLApp(definition=definition, **kwargs)
        case _:
            raise ValueError("Unknown repo type")


def create_app_jobs(apps: list[str], target: str, command: Command = None) -> list[GenericApp]:
    from superelixier import configuration

    app_list: list[GenericApp] = []
    for list_item in apps:
        norm_name = list_item.casefold()
        if norm_name in configuration.definitions:
            appconf = configuration.definitions[norm_name]
            app_list.append(definition_to_app_job(appconf, target=target))
        else:
            if isinstance(command, Command):
                command.line(f"{Ansi.WARNING}Ignoring undefined app \"{norm_name}\"{Ansi.RESET}")
    return app_list
