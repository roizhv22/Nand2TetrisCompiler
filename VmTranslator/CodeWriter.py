"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import os


class CodeWriter:
    """Translates VM commands into Hack assembly code."""
    TEMP_LOCATION = 5
    asm_file = ""
    file_name = ""
    seg_standrad_dict = {"local": "LCL", "argument": "ARG", "this": "THIS",
                         "that": "THAT"}
    func_ret_counters = {}
    cur_func = ""
    op_counter = 0

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        # Your code goes here!
        self.asm_file = output_stream

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        self.file_name, not_used = os.path.splitext(
            os.path.basename(filename))

    def write_arithmetic(self, command: str) -> None:
        """Writes the assembly code that is the translation of the given 
        arithmetic command.

        Args:
            command (str): an arithmetic command.
        """
        # Your code goes here!
        if command == "add" or command == "sub":
            self.__add_sub(command)
        elif command == "neg":
            self.__neg()
        elif command == "eq":
            self.__eq()
        elif command == "gt" or command == "lt":
            self.__gt_lt(command)
        elif command == "and" or command == "or":
            self.__and_or(command)
        elif command == "not" or command == "shiftleft" or \
                command == "shiftright":
            self.__not_shift(command)

    def __add_sub(self, command: str) -> None:
        """
        @param command: the type of the given cmd, add or sub.
        """
        if command == "add":
            self.asm_file.write("// add\n")
            cmd = "@SP\nAM=M-1\nD=M\nA=A-1\nD=M+D\nM=D\n"
        else:
            self.asm_file.write("// sub\n")
            cmd = "@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\nM=D\n"
        self.asm_file.write(cmd)

    def __neg(self) -> None:
        """
        negate the top element of the stack.
        """
        self.asm_file.write("// neg\n")
        cmd = "@SP\nA=M-1\nM=-M\n"
        self.asm_file.write(cmd)

    def __eq(self) -> None:
        """
        perform eq operation on the stack.
        """
        self.asm_file.write("// eq\n")
        ind = str(self.op_counter)
        cmd = "@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n@iseq." + ind \
              + "\nD;JEQ\n@neq." + ind + "\nD;JMP\n(iseq." + ind + ")\n@SP\n" \
              + "A=M-1\nM=1\nM=-M\n@endeq." + ind + "\nD;JMP\n(neq." + ind + \
              ")\n@SP\nA=M-1\nM=0\n(endeq." + ind + ")\n"
        self.asm_file.write(cmd)
        self.op_counter += 1

    def __gt_lt(self, command: str) -> None:
        """
        performing gt/lt operation on the stack.
        @param command: given cmd gt or lt.
        @return: no return value.
        """
        ind = str(self.op_counter)
        if command == "gt":
            self.asm_file.write("// gt\n")
            # Hack assembly code that perform the given operation.
            # as we know overflow can occur if in the given equation a+b=c
            # if b and c have the same sign. therefore we must check if this attribute is occurring.
            # if so, it simple to know which one is larger, otherwise we can use the naive implementation and perform
            # the given task. the following code checks every edge case (++,+-,-+,--)
            cmd = "@SP\nAM=M-1\nD=M\n@gt.yp" + ind + "\nD;JGE\n@gt.y-" + \
                ind + "\nD;JMP\n(gt.yp" + ind + ")\n@SP\nA=M-1\nD=M\n@gt.yxp"\
                  + ind \
                + "\nD;JGE\n@gt.false" + ind + "\nD;JMP\n(gt.y-" + ind + \
                  ")\n@SP\n" \
                "A=M-1\nD=M\n@gt.true" + ind + "\nD;JGE\n@gt.y-x-" + ind + \
                "\nD;JMP\n(gt.yxp" + ind + ")\n@SP\nA=M\nD=M\nA=A-1\nD=M-D\n" \
                "@gt.true" + ind + "\nD;JGT\n@gt.false" + ind + "\nD;JMP\n" \
                "(gt.y-x-" + ind + ")\n@SP\nA=M\nD=M\nA=A-1\nD=M-D\n@gt.true" \
                  + ind \
                  + "\nD;JGT\n@gt.false" + ind + "\nD;JMP\n" \
                "(gt.true" + ind + ")\n@SP\nA=M-1\nM=1\nM=-M\n@gt.end" + ind +\
                  "\nD;JMP\n(gt.false" + ind + ")\n@SP\nA=M-1\nM=0\n" \
                                               "(gt.end" + ind + ")\n"

        else:
            self.asm_file.write("// lt\n")
            cmd = "@SP\nAM=M-1\nD=M\n@lt.yp" + ind + "\nD;JGE\n@lt.y-" + \
                ind + "\nD;JMP\n(lt.yp" + ind + ")\n@SP\nA=M-1\nD=M\n@lt.yxp" \
                  + ind \
                + "\nD;JGE\n@lt.true" + ind + "\nD;JMP\n(lt.y-" + ind \
                  + ")\n@SP\n" \
                "A=M-1\nD=M\n@lt.false" + ind + "\nD;JGE\n@lt.y-x-" + ind + \
                "\nD;JMP\n(lt.yxp" + ind + ")\n@SP\nA=M\nD=M\nA=A-1\nD=D-M\n" \
                "@lt.true" + ind + "\nD;JGT\n@lt.false" + ind + "\nD;JMP\n" \
                "(lt.y-x-" + ind + ")\n@SP\nA=M\nD=M\nA=A-1\nD=D-M\n@lt.true" \
                  + ind \
                + "\nD;JGT\n@lt.false" + ind + "\nD;JMP\n" \
                "(lt.true" + ind + ")\n@SP\nA=M-1\nM=1\nM=-M\n@lt.end" + ind \
                  + "\n" "D;JMP\n(lt.false" + ind + ")\n@SP\nA=M-1\nM=0\n" \
                                                    "(lt.end" + ind + ")\n"
        self.asm_file.write(cmd)
        self.op_counter += 1

    def __and_or(self, command: str) -> None:
        """
        perform and/or operation.
        @param command: "or / and"
        @return: None.
        """
        if command == "and":
            self.asm_file.write("// and\n")
            cmd = "@SP\nAM=M-1\nD=M\nA=A-1\nD=D&M\nM=D\n"
        else:
            self.asm_file.write("// or\n")
            cmd = "@SP\nAM=M-1\nD=M\nA=A-1\nD=D|M\nM=D\n"
        self.asm_file.write(cmd)

    def __not_shift(self, command: str) -> None:
        """
        perform not/shift operation
        @param command: "not" / "shift"
        @return: None.
        """
        if command == "not":
            self.asm_file.write("// not\n")
            cmd = "@SP\nA=M-1\nM=!M\n"
        elif command == "shiftleft":
            self.asm_file.write("// shiftleft\n")
            cmd = "@SP\nA=M-1\nM=M<<\n"
        else:
            self.asm_file.write("// shiftright\n")
            cmd = "@SP\nA=M-1\nM=M>>\n"
        self.asm_file.write(cmd)

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes the assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Your code goes here!
        if segment in self.seg_standrad_dict.keys():
            self.__write_push_pop_base(command, segment, index)
        elif segment == "constant":
            self.__write_push_const(index)
        elif segment == "static":
            self.__write_push_pop_static(command, index)
        elif segment == "temp":
            self.__write_push_pop_temp(command, index)
        elif segment == "pointer":
            self.__write_push_pop_pointer(command, index)

    def close(self) -> None:
        """Closes the output file."""
        # Your code goes here!
        self.asm_file.close()

    def __write_push_pop_base(self, command: str, segment: str, index: int) ->\
            None:
        """
        perform push/pop for the basic memory segment.
        @param command: push/pop
        @param segment: the given memory segment.
        @param index: the index needed
        @return: None
        """

        hack_seg = self.seg_standrad_dict[segment]
        if command == "push":
            self.asm_file.write(
                "// push " + hack_seg + " " + str(index) + "\n")
            cmd = "@" + str(
                index) + "\nD=A\n@" + hack_seg + "\nA=M+D\nD=M\n@" + \
                  "SP\nAM=M+1\nA=A-1\nM=D\n"

        else:
            self.asm_file.write("// pop " + hack_seg
                                + " " + str(index) + "\n")
            cmd = "@" + str(index) + "\nD=A\n@" + hack_seg + \
                  "\nD=M+D\n@R13\n" + \
                  "M=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n"

        self.asm_file.write(cmd)

    def __write_push_pop_temp(self, command: str, index: int) -> None:
        """
        perform push/pop for the temp segment.
        @param command: push/pop
        @param index: index for the given cell
        @return: None
        """
        new_ind = str(self.TEMP_LOCATION + index)
        if command == "push":
            self.asm_file.write("// push temp " + str(index) + "\n")
            cmd = "@" + new_ind + "\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n"
        else:
            self.asm_file.write("// pop temp " + str(index) + "\n")
            cmd = "@SP\nAM=M-1\nD=M\n@" + new_ind + "\nM=D\n"
        self.asm_file.write(cmd)

    def __write_push_const(self, const: int) -> None:
        """
        perform push for const segment.
        @param const: the given const value.
        @return: None
        """
        self.asm_file.write("// push constant " + str(const) + "\n")
        cmd = "@" + str(const) + "\nD=A\n@SP\nAM=M+1\nA=A-1\nM=D\n"
        self.asm_file.write(cmd)

    def __write_push_pop_static(self, command: str, index: int) -> None:
        """
        perform push/pop operation on the static segment.
        @param command: push/pop
        @param index: index
        @return:
        """
        var_name = self.file_name + "." + str(index)
        if command == "push":
            self.asm_file.write("// push static " + str(index) + "\n")
            cmd = "@" + var_name + "\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n"
        else:
            self.asm_file.write("// pop static " + str(index) + "\n")
            cmd = "@SP\nAM=M-1\nD=M\n@" + var_name + "\nM=D\n"
        self.asm_file.write(cmd)

    def __write_push_pop_pointer(self, command: str, index: int) -> None:
        """
        perform push/pop operation for the pointer segment.
        @param command: push/pop
        @param index: given index.
        @return: None
        """
        ind = str(index)
        if command == "push":
            self.asm_file.write("// push pointer " + str(index) + "\n")
            cmd = "@" + ind + "\nD=A\n@THIS\nA=A+D\nD=M\n@SP\nAM=M+1\nA=A-1\n"\
                              "M=D\n"
        else:
            self.asm_file.write("// pop pointer " + str(index) + "\n")
            cmd = "@" + ind + "\nD=A\n@THIS\nA=A+D\nD=A\n@R13\nM=D\n@SP\nAM" \
                              "=M-1\nD=M\n@R13\nA=M\nM=D\n"
        self.asm_file.write(cmd)

    def write_label(self, label: str) -> None:
        """
        writing a given label in the format File_name.cur_func$label_name
        @param label: a label name to be inserted. (only name without func/file)
        @return: None
        """
        self.asm_file.write("//creating label\n")
        label_str = self.file_name + "." + self.cur_func + "$" + label
        self.asm_file.write(f"({label_str})\n")

    def write_goto(self, label: str) -> None:
        """
        writing the goto command.
        as in the writing label function, only the label name is needed.
        @param label: label as a string
        @return: None
        """
        self.asm_file.write("//writing goto\n")
        label_str = self.file_name + "."+self.cur_func + "$"+label
        self.asm_file.write(f"@{label_str}\n0;JMP\n")

    def write_if_goto(self, label: str) -> None:
        """
        writing if-goto, similar to the goto function, only checks if the last element in the stack !0. 
        if so it will JMP
        @param label: a label to jump to.
        @return: None
        """""
        self.asm_file.write("//writing if-goto\n")
        label_str = self.file_name + "." + self.cur_func + "$"+label
        self.asm_file.write(f"@SP\nAM=M-1\nD=M\n@{label_str}\nD;JNE\n")
        # performs pop of expression and evaluate (checking if < 0, as
        # True value agreed to be !0 in binary.

    def __write_push_for_call(self, segment: str) -> None:
        """
        Simple helper function that performs the pushed the we require for the Call cmd.
        @param segment: The segment that needed to be pushed.
        @return: None.
        """
        self.asm_file.write(f"@{segment}\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n")

    def __write_boot_sys_init_call(self) -> None:
        """
        private method that perform the first call for the sys.init function.
        following the protocol creating labels that won't be recovered.
        @return: None
        """
        self.asm_file.write(f"@BOOT_RET\nD=A\n@SP\nAM=M+1\nA=A-1\nM=D\n")
        self.__write_push_for_call("LCL")
        self.__write_push_for_call("ARG")
        self.__write_push_for_call("THIS")
        self.__write_push_for_call("THAT")
        self.asm_file.write(f"@SP\nD=M\n@5\nD=D-A\n@ARG\n"
                            f"M=D\n")
        self.asm_file.write("@SP\nD=M\n@LCL\nM=D\n")
        self.asm_file.write(f"@Sys.init\n0;JMP\n")
        self.asm_file.write("(BOOT_RET)\n")

    def write_call(self, func_name: str, num_args: int) -> None:
        """
        Writing the call cmd.
        @param func_name: The callee
        @param num_args: num of arguments that were pushed
        @return: None
        """
        self.asm_file.write(f"//Call {func_name} {num_args}\n")
        if func_name == "boot":
            self.__write_boot_sys_init_call()
            return
        return_add = self.file_name + "." + self.cur_func + "$ret." + \
                     str(self.func_ret_counters[self.cur_func])
        self.asm_file.write(f"@{return_add}\nD=A\n@SP\nAM=M+1\nA=A-1\nM=D\n")
        self.__write_push_for_call("LCL")
        self.__write_push_for_call("ARG")
        self.__write_push_for_call("THIS")
        self.__write_push_for_call("THAT")
        back_steps_for_arg = 5 + num_args
        self.asm_file.write(f"@SP\nD=M\n@{back_steps_for_arg}\nD=D-A\n@ARG\n"
                            f"M=D\n")
        self.asm_file.write("@SP\nD=M\n@LCL\nM=D\n")
        self.asm_file.write(f"@{func_name}\n0;JMP\n")
        self.write_label("ret." + str(self.func_ret_counters[self.cur_func]))
        self.func_ret_counters[self.cur_func] += 1

    def write_function(self, func_name: str, nargs: int) -> None:
        """
        Writing the function in Hack. perform push 0 for as many local variables needed.
        @param func_name: function name
        @param nargs: number local variables needed
        @return: None.
        """
        self.asm_file.write(f"//function {func_name} {nargs}\n")
        func_par = func_name.split(".")
        self.asm_file.write("("+self.file_name+"."+func_par[1]+")\n")
        self.cur_func = func_par[1]
        if self.cur_func not in self.func_ret_counters.keys():
            self.func_ret_counters[self.cur_func] = 1
        for _ in range(nargs):
            self.__write_push_const(0)

    def write_return(self) -> None:
        """
        writing the return cmd. perform the given protocol to recycle the needed values and assign them to the
        variables.
        @return: None.
        """
        self.asm_file.write("//return\n")
        self.asm_file.write("@LCL\nD=M\n@R13\nM=D\n@5\nD=D-A\nA=D\nD=M\n@R14\n"
                            "M=D\n")  # R13 = endFrame, R14 = redAddr
        self.asm_file.write(
            "@SP\nAM=M-1\nD=M\n@ARG\nA=M\nM=D\n")  # pop to ARG 0
        self.asm_file.write(
            "@ARG\nD=M\nD=D+1\n@SP\nM=D\n")  # SP address assign
        # to ARG+1
        # recycling the address.
        self.asm_file.write("@R13\nD=M\nD=D-1\nA=D\nD=M\n@THAT\nM=D\n")
        self.asm_file.write("@R13\nD=M\n@2\nD=D-A\nA=D\nD=M\n@THIS\nM=D\n")
        self.asm_file.write("@R13\nD=M\n@3\nD=D-A\nA=D\nD=M\n@ARG\nM=D\n")
        self.asm_file.write("@R13\nD=M\n@4\nD=D-A\nA=D\nD=M\n@LCL\nM=D\n")
        self.asm_file.write("@R14\nA=M\n0;JMP\n")
        # jump to returns address.
