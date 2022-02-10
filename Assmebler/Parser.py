"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """Encapsulates access to the input code. Reads and assembly language 
    command, parses it, and provides convenient access to the commands 
    components (fields and symbols). In addition, removes all white space and 
    comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is:
        self.__input_lines = input_file.read().splitlines()
        self.__counter = -1
        self.__cur_line = ""
        self.advance()

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        # Your code goes here!
        if self.__counter == len(self.__input_lines):
            return False
        return True

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        # Your code goes here!
        self.__counter += 1
        if self.__counter == len(self.__input_lines):
            return
        self.__cur_line = ''.join(self.__input_lines[self.__counter].split())
        back_pos = self.__cur_line.find("/")
        while (len(self.__cur_line) == 0 or back_pos == 0):  # protection from overflow.
            self.__counter += 1
            if self.__counter == len(self.__input_lines):
                break
            self.__cur_line = ''.join(
                self.__input_lines[self.__counter].split())
            back_pos = self.__cur_line.find("/")
        if back_pos != -1:
            self.__cur_line = self.__cur_line[:back_pos]


    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        # Your code goes here!
        if self.__cur_line[0] == "@":
            return "A_COMMAND"
        elif self.__cur_line[0] == "(":
            return "L_COMMAND"
        else:
            return "C_COMMAND"

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        # Your code goes here!
        if self.command_type() == "L_COMMAND":
            return self.__cur_line[1:-1]
        return self.__cur_line[1:]

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        # Your code goes here!
        chr_ind = self.__cur_line.find("=")
        if chr_ind == -1:
            return "null"
        return self.__cur_line[:chr_ind]

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        # Your code goes here!
        eq_ind = self.__cur_line.find("=")
        dot_ind = self.__cur_line.find(";")
        if eq_ind == -1:
            return self.__cur_line[:dot_ind]
        elif dot_ind == -1:
            return self.__cur_line[eq_ind+1:]
        elif eq_ind != -1 and dot_ind != -1:
            return self.__cur_line[eq_ind+1:dot_ind]
        else:
            return self.__cur_line

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        # Your code goes here!
        chr_ind = self.__cur_line.find(";")
        if chr_ind == -1:
            return "null"
        return self.__cur_line[chr_ind+1:]
