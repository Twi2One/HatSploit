#!/usr/bin/env python3

#
# MIT License
#
# Copyright (c) 2020-2022 EntySec
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from hatsploit.lib.show import Show

from hatsploit.core.db.importer import Importer
from hatsploit.core.cli.badges import Badges
from hatsploit.core.base.execute import Execute
from hatsploit.lib.storage import LocalStorage


class Commands:
    show = Show()

    importer = Importer()
    badges = Badges()
    execute = Execute()
    local_storage = LocalStorage()

    def load_commands(self, path):
        return self.importer.import_commands(path)

    def execute_command(self, commands):
        self.execute.execute_command(commands)

    def execute_system_command(self, commands):
        self.execute.execute_system(commands)

    def execute_custom_command(self, commands, handler, error=True):
        if commands:
            if not self.execute.execute_builtin_method(commands):
                if not self.execute.execute_custom_command(commands, handler):
                    if error:
                        self.badges.print_error(f"Unrecognized command: {commands[0]}!")
                    return False
        return True

    def show_commands(self, handler):
        self.show.show_custom_commands(handler)

    def commands_completer(self, text):
        return [command for command in self.get_all_commands() if command.startswith(text)]

    def get_all_commands(self):
        core_cmds = self.local_storage.get("commands")

        modules = self.local_storage.get("modules")
        modules_cmds = []

        if modules:
            for database in modules:
                for module in modules[database]:
                    if hasattr(modules[database][module], "commands"):
                        modules_cmds += modules[database][module].commands

        plugins = self.local_storage.get("loaded_plugins")
        plugins_cmds = []

        if plugins:
            for plugin in plugins:
                if hasattr(plugins[plugin], "commands"):
                    for label in plugins[plugin].commands:
                        plugins_cmds += plugins[plugin].commands[label]

        return core_cmds + modules_cmds + plugins_cmds
