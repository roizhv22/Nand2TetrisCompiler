"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient
    access to their components.
    In addition, it removes all white space and comments.
    """
    MAX_ARG_LEN = 3

    input = []
    cur_cmd = []
    counter = -1

    art_cmds = {'add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not',
                'shiftleft', 'shiftright'}
    mem_cmds = {'pop', 'push'}

    dict_of_cmd = {"pop": "C_POP", "push": "C_PUSH", "label": "C_LABEL",
                   "goto": "C_GOTO", "if-goto": "C_IF",
                   "function": "C_FUNCTION", "return": "C_RETURN",
                   "call": "C_CALL"}

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is:
        self.input = input_file.read().splitlines()
        self.advance()



    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        if self.counter >= len(self.input):
            return False
        return True

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        self.counter += 1
        if self.has_more_commands(): # checks overflow
            self.cur_cmd = self.input[self.counter].split()
            while self.cur_cmd == [] or self.cur_cmd[0][0] == "/":
                self.counter += 1
                if not self.has_more_commands(): # checks overflow
                    return
                self.cur_cmd = self.input[self.counter].split()


    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        cmd = self.cur_cmd[0]
        if cmd in self.art_cmds:
            return "C_ARITHMETIC"
        return self.dict_of_cmd[cmd]

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned.
            Should not be called if the current command is "C_RETURN".
        """
        if self.command_type() == "C_ARITHMETIC":
            return self.cur_cmd[0]
        elif self.command_type() == "C_POP" or self.command_type() == "C_PUSH":
            return self.cur_cmd[0] + " " + self.cur_cmd[1]
        elif self.command_type() == "C_LABEL" \
                or self.command_type() == "C_GOTO" or \
                self.command_type() == "C_IF":
            return self.cur_cmd[1] # returns just the label name.

        elif self.command_type() == "C_CALL" or "C_FUNCTION":
            return self.cur_cmd[1] # returns function name

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP",
            "C_FUNCTION" or "C_CALL".
        """
        if self.command_type() == "C_PUSH" or self.command_type() == "C_POP":
            return int(self.cur_cmd[2])
        elif self.command_type() == "C_CALL" or "C_FUNCTION":
            return int(self.cur_cmd[2])




