"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class VMWriter:
    """
    Writes VM commands into a file. Encapsulates the VM command syntax.
    """
    __current_function = ""
    __static_var_counter = 0
    __output_file = ""
    __map_of_segments = {"CONST": "constant", "ARG": "argument",
                         "LOCAL": "local", "STATIC": "static", "THIS": "this",
                         "THAT": "that", "POINTER": "pointer", "TEMP": "temp"}
    __map_of_arithmetic = {"ADD": "add", "SUB": "sub", "NEG": "neg",
                           "EQ": "eq", "GT": "gt", "LT": "lt", "AND": "and",
                           "OR": "or","NOT": "not", "SHIFTLEFT": "shiftleft",
                           "SHIFTRIGHT": "shiftright"}

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Creates a new file and prepares it for writing VM commands."""
        # Your code goes here!
        self.__output_file = output_stream

    def write_push(self, segment: str, index: int) -> None:
        """Writes a VM push command.

        Args:
            segment (str): the segment to push to, can be "CONST", "ARG", 
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP"
            index (int): the index to push to.
        """
        # Your code goes here!
        if segment == "VAR":
            self.__output_file.write(f"push local {index}\n")
        elif segment == "FIELD":
            self.__output_file.write(f"push this {index}\n")
        else:
            self.__output_file.write(f"push {self.__map_of_segments[segment]} "
                                     f"{index}\n")

    def write_pop(self, segment: str, index: int) -> None:
        """Writes a VM pop command.

        Args:
            segment (str): the segment to pop from, can be "CONST", "ARG", 
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP".
            index (int): the index to pop from.
        """
        # Your code goes here!
        self.__output_file.write(f"pop {self.__map_of_segments[segment]} "
                                 f"{index}\n")

    def write_arithmetic(self, command: str) -> None:
        """Writes a VM arithmetic command.

        Args:
            command (str): the command to write, can be "ADD", "SUB", "NEG", 
            "EQ", "GT", "LT", "AND", "OR", "NOT".
        """
        # Your code goes here!
        self.__output_file.write(f"{self.__map_of_arithmetic[command]}\n")

    def write_label(self, label: str) -> None:
        """Writes a VM label command.

        Args:
            label (str): the label to write.
        """
        # Your code goes here!
        self.__output_file.write(f"label {label}\n")

    def write_goto(self, label: str) -> None:
        """Writes a VM goto command.

        Args:
            label (str): the label to go to.
        """
        # Your code goes here!
        self.__output_file.write(f"goto {label}\n")

    def write_if(self, label: str) -> None:
        """Writes a VM if-goto command.

        Args:
            label (str): the label to go to.
        """
        # Your code goes here!
        self.__output_file.write(f"if-goto {label}\n")

    def write_call(self, name: str, n_args: int) -> None:
        """Writes a VM call command.

        Args:
            name (str): the name of the function to call.
            n_args (int): the number of arguments the function receives.
        """
        # Your code goes here!
        self.__output_file.write(f"call {name} {n_args}\n")

    def write_function(self, name: str, n_locals: int) -> None:
        """Writes a VM function command.

        Args:
            name (str): the name of the function.
            n_locals (int): the number of local variables the function uses.
        """
        # Your code goes here!
        self.__output_file.write(f"function {name} {n_locals}\n")

    def write_return(self) -> None:
        """Writes a VM return command."""
        # Your code goes here!
        self.__output_file.write("return\n")

    def close(self) -> None:
        """Closes the output file."""
        # Your code goes here!
        self.__output_file.close()
