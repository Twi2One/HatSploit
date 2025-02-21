"""
MIT License

Copyright (c) 2020-2024 EntySec

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import json

from badges.cmd import Cmd

from hatsploit.core.utils.ui.banner import Banner
from hatsploit.core.utils.ui.tip import Tip

from hatsploit.core.db.db import DB

from hatsploit.lib.ui.modules import Modules

from hatsploit.lib.config import Config
from hatsploit.lib.runtime import Runtime

from hatsploit.lib.storage import STORAGE


class Console(Cmd):
    """ Subclass of hatsploit.core.base module.

    This subclass of hatsploit.lib.base module represents console
    handler for HatSploit.
    """

    def __init__(self) -> None:
        """ Initialize console.

        :return None: None
        """

        self.config = Config()
        self.scheme = self.config.core_config['details']['prompt']

        self.history = None
        self.log = STORAGE.get("log")

        if STORAGE.get("history"):
            self.history = self.config.path_config['history_path']

        super().__init__(
            prompt=f"[{self.scheme}]> ",
            history=self.history,
            path=[self.config.path_config['commands_path']],
            console=self,
            log=self.log,
            shorts=json.load(
                open(self.config.path_config['shorts_path']))
        )

        self.runtime = Runtime()
        self.modules = Modules()

    def postcmd(self, _) -> None:
        """ Update prompt.

        :return None: None
        """

        self.runtime.refresh()
        module = self.modules.get_current_module()

        if not module:
            self.set_prompt(f'[{self.scheme}]> ')
            return

        self.set_prompt(f'[{self.scheme}: %red{module.info["Name"]}%end]> ')

    def precmd(self, line: str) -> str:
        """ Refresh console before executing command.

        :param str line: command line
        :return str: command line
        """

        self.runtime.refresh()
        return line

    def shell(self, header: bool = True) -> None:
        """ Configure HatSploit shell interpreter and start it.

        :param bool header: print header
        :return None: None
        """

        if header:
            self.show_header()

        self.loop()

    def show_header(self) -> None:
        """ Print HatSploit shell interpreter header.

        :return None: None
        """

        version = self.config.core_config['details']['version']
        codename = self.config.core_config['details']['codename']

        if self.config.core_config['console']['clear']:
            self.print_empty("%clear", end='', log=False)

        if self.config.core_config['console']['banner']:
            Banner().print_random_banner()

        if self.config.core_config['console']['header']:
            header = ""
            header += "%end"
            if codename:
                header += f"    --=[ %yellowHatSploit Framework {version} {codename} (https://hatsploit.com)%end\n"
            else:
                header += f"    --=[ %yellowHatSploit Framework {version}%end\n"
            header += (
                "--==--=[ Developed by EntySec (%linehttps://entysec.com%end)\n"
            )
            header += f"    --=[ %red{DB(table='modules').count()}%end modules | %blue{DB(table='payloads').count()}%end payloads "
            header += f"| %green{DB(table='encoders').count()}%end encoders | %yellow{DB(table='plugins').count()}%end plugins"
            header += "%end"

            self.print_empty(header, log=False, less=False)

        if self.config.core_config['console']['tip']:
            Tip().print_random_tip()

    def script(self, input_files: list, shell: bool = True) -> None:
        """ Execute HatSploit script(s).

        :param list input_files: list of filenames of files
        containing HatSploit scripts
        :param bool shell: True to launch shell interpreter
        after all scripts executed else False
        :return None: None
        """

        self.show_header()

        for input_file in input_files:
            if not os.path.exists(input_file):
                return

            with open(input_file, 'r') as f:
                for line in f.read().split('\n'):
                    self.runtime.refresh()
                    self.onecmd(line)
                    self.runtime.refresh()

        if shell:
            self.shell(header=False)
