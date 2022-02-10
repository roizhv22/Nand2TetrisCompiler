"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from Parser import Parser
from CodeWriter import CodeWriter


def translate_file(input_file: typing.TextIO, output_file: typing.TextIO) \
        -> None:
    """Translates a single file.

    Args:
        input_file (typing.TextIO): the file to translate.
        output_file (typing.TextIO): writes all output to this file.
    """
    # Your code goes here!
    # Note: you can get the input file's name using:
    # input_filename, input_extension =
    # os.path.splitext(os.path.basename(input_file.name))
    parser = Parser(input_file)
    writer = CodeWriter(output_file)
    writer.set_file_name(input_file.name)

    while parser.has_more_commands():
        cmd_type = parser.command_type()
        if cmd_type == "C_ARITHMETIC":
            writer.write_arithmetic(parser.arg1())
        elif cmd_type == "C_POP" or cmd_type == "C_PUSH":
            arg = parser.arg1().split()
            ind = parser.arg2()
            writer.write_push_pop(arg[0], arg[1], ind)
        elif cmd_type == "C_LABEL":
            writer.write_label(parser.arg1())
        elif cmd_type == "C_GOTO":
            writer.write_goto(parser.arg1())
        elif cmd_type == "C_IF":
            writer.write_if_goto(parser.arg1())
        elif cmd_type == "C_CALL":
            writer.write_call(parser.arg1(), parser.arg2())
        elif cmd_type == "C_FUNCTION":
            writer.write_function(parser.arg1(), parser.arg2())
        elif cmd_type == "C_RETURN":
            writer.write_return()
        parser.advance()


def write_bootstrap(op_file: typing.TextIO) -> None:
    """
    Writing the boostrap code into the asm file. calling the sys.init
    and initializing the needed memory segments.
    @param op_file:
    @return: None.
    """
    op_file.write("@256\nD=A\n@SP\nM=D\n") # set SP to 256
    temp_w = CodeWriter(op_file)
    temp_w.write_call("boot", 0) # unique flag that the write function gets inorder to invoke the private method that
    # writes the first call cmd for the sys.init.


if "__main__" == __name__:
    # Parses the input path and calls translate_file on each input file
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: VMtranslator <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_translate = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
        output_path = os.path.join(argument_path, os.path.basename(
            argument_path))
    else:
        files_to_translate = [argument_path]
        output_path, extension = os.path.splitext(argument_path)
    output_path += ".asm"
    with open(output_path, 'w') as output_file:
        write_bootstrap(output_file) # writing the bootstrap code before starting to translate.
        for input_path in files_to_translate:
            filename, extension = os.path.splitext(input_path)
            if extension.lower() != ".vm":
                continue
            with open(input_path, 'r') as input_file:
                translate_file(input_file, output_file)
