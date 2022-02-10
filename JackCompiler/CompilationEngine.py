"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
from JackTokenizer import *
import typing

from SymbolTable import SymbolTable
from VMWriter import VMWriter


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """
    __keywords_dict = __keywords = {'CLASS': 'class',
                                    'CONSTRUCTOR': 'constructor',
                                    'FUNCTION': 'function', 'METHOD': 'method',
                                    'FIELD': 'field',
                                    'STATIC': 'static', 'VAR': 'var',
                                    'INT': 'int',
                                    'CHAR': 'char', 'BOOLEAN': 'boolean',
                                    'VOID': 'void',
                                    'TRUE': 'true', 'FALSE': 'false',
                                    'NULL': 'null',
                                    'THIS': 'this', 'LET': 'let', 'DO': 'do',
                                    'IF': 'if',
                                    'ELSE': 'else', 'WHILE': 'while',
                                    'RETURN': 'return'}
    input_tokenizer = ""
    vm_writer = ""
    symbol_table = ""
    subroutine_type = ""
    class_name = ""
    cur_sub_name = ""
    bin_op = {'+': "ADD", '-': "SUB", '*': "MULTI", '/': "DIV",
              '&': "AND", '|': "OR", '<': "LT", '>': "GT", '=': "EQ"}
    un_op = {'-': "NEG", '~': "NOT", '^': "SHIFTLEFT", '#': "SHIFTRIGHT"}

    __amount_of_expressions = 0
    __if_counter = 0
    __while_counter = 0
    __return_was_called = False

    def __init__(self, input_stream: typing.TextIO,
                 output_stream: typing.TextIO) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        self.input_tokenizer = JackTokenizer(input_stream)
        self.vm_writer = VMWriter(output_stream)
        self.symbol_table = SymbolTable()

    def compile_class(self) -> None:
        """Compiles a complete class."""
        # Your code goes here!

        self.input_tokenizer.advance()  # pass class keyword
        self.class_name = self.input_tokenizer.identifier()  # gets class for
        # this type.
        self.input_tokenizer.advance()  # pass class_name
        self.input_tokenizer.advance()  # pass {
        self.compile_class_var_dec()

        while self.input_tokenizer.token_type() != "SYMBOL" and \
                self.input_tokenizer.symbol() != "}":
            self.compile_subroutine()
        self.vm_writer.close()
        # left }

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # Your code goes here!
        cur_kind = ""
        cur_type = ""
        cur_name = ""
        if self.input_tokenizer.token_type() == "KEYWORD":
            while self.input_tokenizer.keyword() == "FIELD" or \
                    self.input_tokenizer.keyword() == "STATIC":
                cur_kind = self.input_tokenizer.keyword()  # var kind
                self.input_tokenizer.advance()
                cur_type = self.__get_type()  # var type
                self.input_tokenizer.advance()
                cur_name = self.input_tokenizer.identifier()
                # var_name
                self.input_tokenizer.advance()
                self.symbol_table.define(cur_name, cur_type, cur_kind)  # adds
                # to table

                while self.input_tokenizer.symbol() != ";":
                    self.input_tokenizer.advance()  # pass on comma
                    self.symbol_table.define(self.input_tokenizer.identifier(),
                                             cur_type, cur_kind)
                    # adds same kind and type vars (field var x,y;)
                    self.input_tokenizer.advance()
                # ;
                self.input_tokenizer.advance()  # finish one line and advance
                # on ;

                if self.input_tokenizer.token_type() != "KEYWORD":
                    # if we done to declare break.
                    break

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""
        # Your code goes here!
        self.symbol_table.start_subroutine()
        self.__if_counter = 0
        self.__while_counter = 0
        self.__return_was_called = False
        num_of_local_vars = 0
        self.subroutine_type = self.input_tokenizer.keyword()  # method type

        self.input_tokenizer.advance()  # pass method/function/constructor
        subroutine_return_type = self.__get_type()
        self.input_tokenizer.advance()  # pass type
        self.cur_sub_name = self.input_tokenizer.identifier()
        # method/func name
        self.input_tokenizer.advance()  # pass name

        self.input_tokenizer.advance()  # pass on (
        if self.subroutine_type == "METHOD":
            self.symbol_table.define("this", self.class_name, "ARG")
        self.compile_parameter_list()
        self.input_tokenizer.advance()  # pass on )

        # sub body.
        self.input_tokenizer.advance()  # pass on {
        self.compile_var_dec()
        num_of_local_vars += self.symbol_table.var_count("VAR")
        # writes the function to the vm
        self.vm_writer.write_function(f"{self.class_name}.{self.cur_sub_name}",
                                      num_of_local_vars)
        if self.subroutine_type == "METHOD":
            self.vm_writer.write_push("ARG", 0)
            self.vm_writer.write_pop("POINTER", 0)
            # adds this in case of method.
        elif self.subroutine_type == "CONSTRUCTOR":
            self.__compile_constructor()
            # mem alloc and then continue as usual.

        self.compile_statements()
        # make sure the to return.
        if subroutine_return_type == "VOID" and (not self.__return_was_called):
            self.vm_writer.write_push("CONST", 0)
            self.vm_writer.write_return()

        self.input_tokenizer.advance()  # pass on }

    def __get_type(self):
        """Get the method / var type - we use in case of class_name
        and not primitive"""
        if self.input_tokenizer.token_type() == "IDENTIFIER":
            subroutine_return_type = self.input_tokenizer.identifier()
            # case of class_name type
        else:
            subroutine_return_type = self.input_tokenizer.keyword()
            # return type/type for primitive
        return subroutine_return_type

    def __compile_constructor(self) -> None:
        """
        Perform the memory allocation and anchor the address to pointer 0.
        """
        # perform memory alloc
        num_of_objects = self.symbol_table.var_count("FIELD")
        self.vm_writer.write_push("CONST", num_of_objects)
        self.vm_writer.write_call("Memory.alloc", 1)
        self.vm_writer.write_pop("POINTER", 0)  # set base to this


    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """

        while self.input_tokenizer.token_type() != "SYMBOL" or \
                (self.input_tokenizer.token_type() == "SYMBOL" and
                 self.input_tokenizer.symbol() != ")"):
            if self.input_tokenizer.token_type() == "SYMBOL":
                if self.input_tokenizer.symbol() == ",":
                    self.input_tokenizer.advance()  # pass comma
            cur_type = self.__get_type()  # get type
            self.input_tokenizer.advance()
            cur_ident = self.input_tokenizer.identifier()  # get ident
            self.input_tokenizer.advance()
            self.symbol_table.define(cur_ident, cur_type, "ARG")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        while self.input_tokenizer.token_type() == "KEYWORD" and \
                self.input_tokenizer.keyword() == "VAR":
            self.input_tokenizer.advance()  # pass on var
            if self.input_tokenizer.token_type() == "IDENTIFIER":
                cur_type = self.input_tokenizer.identifier()
                # case of class name
            else:
                cur_type = self.input_tokenizer.keyword()  # type
            self.input_tokenizer.advance()
            cur_name = self.input_tokenizer.identifier()  # var_name
            self.input_tokenizer.advance()
            self.symbol_table.define(cur_name, cur_type, "VAR")
            while self.input_tokenizer.symbol() != ";":
                self.input_tokenizer.advance()  # pass comma
                cur_name = self.input_tokenizer.identifier()  # var_name
                self.input_tokenizer.advance()
                self.symbol_table.define(cur_name, cur_type, "VAR")
            self.input_tokenizer.advance()  # pass ;

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        # choose which.
        while self.input_tokenizer.token_type() == "KEYWORD":
            key_word = self.input_tokenizer.keyword()
            if key_word == "IF":
                self.compile_if()
            elif key_word == "LET":
                self.compile_let()
            elif key_word == "WHILE":
                self.compile_while()
            elif key_word == "DO":
                self.compile_do()
            elif key_word == "RETURN":
                self.compile_return()

    def compile_do(self) -> None:
        """Compiles a do statement."""

        self.input_tokenizer.advance()  # pass on do
        sub_name = self.input_tokenizer.identifier()
        self.input_tokenizer.advance()  # pass on sub name
        if self.input_tokenizer.symbol() == ".":
            self.__compile_subroutine_call(sub_name)  # func/method from
            # other class.
        else:
            self.__compile_method_call(sub_name)  # method call
        self.vm_writer.write_pop("TEMP", 0)

        self.input_tokenizer.advance()  # pass on ;

    def compile_let(self) -> None:
        """Compiles a let statement."""

        self.input_tokenizer.advance()  # pass let

        var_name = self.input_tokenizer.identifier()  # varName
        self.input_tokenizer.advance()  # pass var name
        if self.input_tokenizer.symbol() == "[":
            self.__let_array_handle(var_name)
            return

        self.input_tokenizer.advance()  # pass =

        self.compile_expression()
        if self.symbol_table.kind_of(var_name) == "VAR":
            self.vm_writer.write_pop("LOCAL",
                                     self.symbol_table.index_of(var_name))
        elif self.symbol_table.kind_of(var_name) == "FIELD":
            self.vm_writer.write_pop("THIS",
                                     self.symbol_table.index_of(var_name))
        else:
            self.vm_writer.write_pop(self.symbol_table.kind_of(var_name),
                                     self.symbol_table.index_of(var_name))
        self.input_tokenizer.advance()  # pass ;

    def __let_array_handle(self, var_name) -> None:
        """
        Handles array assignments from let statements.
        """
        self.input_tokenizer.advance()  # pass [
        self.vm_writer.write_push(self.symbol_table.kind_of(var_name),
                                  self.symbol_table.index_of(var_name))
        # push base address of the array.
        self.compile_expression()  # push exp value
        self.vm_writer.write_arithmetic("ADD")
        self.input_tokenizer.advance()  # pass ]
        self.input_tokenizer.advance()  # pass =
        self.compile_expression()
        self.vm_writer.write_pop("TEMP", 0)
        self.vm_writer.write_pop("POINTER", 1)
        self.vm_writer.write_push("TEMP", 0)
        self.vm_writer.write_pop("THAT", 0)
        self.input_tokenizer.advance()  # pass ;

    def compile_while(self) -> None:
        """Compiles a while statement."""
        L1 = f"{self.class_name}.{self.cur_sub_name}.while.L1." \
             f"{self.__while_counter}"
        L2 = f"{self.class_name}.{self.cur_sub_name}.while.L2." \
             f"{self.__while_counter}"
        self.__while_counter += 1
        # increment labels counter from unique labels
        self.vm_writer.write_label(L1)
        self.input_tokenizer.advance()  # pass while
        self.input_tokenizer.advance()  # pass (

        self.compile_expression()
        self.vm_writer.write_arithmetic("NOT")  # negate from the structure was
        # presented.

        self.input_tokenizer.advance()  # pass )
        self.input_tokenizer.advance()  # pass {

        self.vm_writer.write_if(L2)
        self.compile_statements()
        self.vm_writer.write_goto(L1)

        self.input_tokenizer.advance()  # pass }
        self.vm_writer.write_label(L2)


    def compile_return(self) -> None:
        """Compiles a return statement."""
        # Your code goes here!
        self.__return_was_called = True
        self.input_tokenizer.advance()  # pass return

        if self.input_tokenizer.token_type() != "SYMBOL" or \
                (self.input_tokenizer.token_type() == "SYMBOL" and
                 self.input_tokenizer.symbol() != ";"):
            self.compile_expression()  # in case there is an expression.
        else:
            self.vm_writer.write_push("CONST", 0)  # case of void return.
        self.vm_writer.write_return()
        self.input_tokenizer.advance()  # pass write ;

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # Your code goes here!

        self.input_tokenizer.advance()  # pass if
        self.input_tokenizer.advance()  # write (
        L1 = f"{self.class_name}.{self.cur_sub_name}.if.L1.{self.__if_counter}"
        L2 = f"{self.class_name}.{self.cur_sub_name}.if.L2.{self.__if_counter}"
        self.__if_counter += 1  # increment labels counter from unique labels
        self.compile_expression()
        self.vm_writer.write_arithmetic("NOT")  # negate the results.
        self.input_tokenizer.advance()  # pass )
        self.input_tokenizer.advance()  # pass {
        self.vm_writer.write_if(L1)  # if goto L1
        self.compile_statements()  # compile if statements.
        self.vm_writer.write_goto(L2)  # goto L2

        self.input_tokenizer.advance()  # pass }
        self.vm_writer.write_label(L1)  # write L1

        if self.input_tokenizer.token_type() == "KEYWORD" and \
                self.input_tokenizer.keyword() == "ELSE":
            self.input_tokenizer.advance()  # pass else
            self.input_tokenizer.advance()  # pass {
            self.compile_statements()  # compile else statements.
            self.input_tokenizer.advance()  # pass }

        self.vm_writer.write_label(L2)  # write L2 - end of if,else section.

    def compile_expression(self) -> None:
        """Compiles an expression."""
        # Your code goes here!

        # just an expression or bin expression case
        self.compile_term()
        while self.input_tokenizer.token_type() == "SYMBOL" and \
                self.input_tokenizer.symbol() in self.bin_op.keys():
            cur_bin_op = self.input_tokenizer.symbol()
            self.input_tokenizer.advance()
            self.compile_term()
            if cur_bin_op == "*" or cur_bin_op == "/":
                if cur_bin_op == "*":
                    self.vm_writer.write_call("Math.multiply", 2)
                else:
                    self.vm_writer.write_call("Math.divide", 2)
            else:
                self.vm_writer.write_arithmetic(self.bin_op[cur_bin_op])

    def compile_term(self) -> None:
        """Compiles a term. This routine is faced with a slight difficulty
        when trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing
        must distinguish between a variable, an array entry,
        and a subroutine call. A single look-ahead token, which may be one
        of "[", "(", or "." suffices to distinguish between the three
        possibilities. Any other token is not part of this term and should
        not be advanced over.
        """
        # Your code goes here!

        if self.input_tokenizer.token_type() == "INT_CONST":
            # integerConstant
            self.vm_writer.write_push("CONST", self.input_tokenizer.int_val())
            self.input_tokenizer.advance()

        elif self.input_tokenizer.token_type() == "STRING_CONST":
            str_val = self.input_tokenizer.string_val()
            self.vm_writer.write_push('CONST', len(str_val))
            self.vm_writer.write_call("String.new", 1)
            for i in range(len(str_val)):
                self.vm_writer.write_push("CONST", ord(str_val[i]))
                self.vm_writer.write_call("String.appendChar", 2)
            self.input_tokenizer.advance()

        elif self.input_tokenizer.token_type() == "SYMBOL":
            if self.input_tokenizer.symbol() in self.un_op.keys():
                # unary op case
                cur_un_op = self.input_tokenizer.symbol()
                self.input_tokenizer.advance()
                self.compile_term()  # compile term and push it
                self.vm_writer.write_arithmetic(
                    self.un_op[cur_un_op])  # write
                # correct un op

            elif self.input_tokenizer.symbol() == "(":
                self.input_tokenizer.advance()  # pass (
                self.compile_expression()
                self.input_tokenizer.advance()  # pass )

        elif self.input_tokenizer.token_type() == "KEYWORD":
            key_word = self.input_tokenizer.keyword()
            if key_word == "NULL" or key_word == "FALSE" or key_word == "TRUE":
                self.vm_writer.write_push("CONST", 0)
                if key_word == "TRUE":
                    self.vm_writer.write_arithmetic("NOT")
            else:
                # push the this - arg 0 by convention.
                if self.symbol_table.index_of("this") is not None:
                    self.vm_writer.write_push("ARG", 0)
                else:
                    self.vm_writer.write_push("POINTER", 0)
                    # this is not defined in function and because we get a
                    # valid code this will be called only in the constructor
                    # to return this, thus we push pointer 0 and returns it.

            self.input_tokenizer.advance()

        else:
            # case of identifier.
            ident = self.input_tokenizer.identifier()
            self.input_tokenizer.advance()
            if self.input_tokenizer.symbol() == "[":
                self.vm_writer.write_push(self.symbol_table.kind_of(ident),
                                          self.symbol_table.index_of(ident))
                self.input_tokenizer.advance()  # pass [
                self.compile_expression()
                self.vm_writer.write_arithmetic("ADD")
                self.input_tokenizer.advance()  # pass ]
                self.vm_writer.write_pop("POINTER", 1)
                self.vm_writer.write_push("THAT", 0)

            elif self.input_tokenizer.symbol() == ".":
                self.__compile_subroutine_call(ident)

            elif self.input_tokenizer.symbol() == "(":
                self.__compile_method_call(ident)
            else:
                # classic var situation we just push it
                if self.symbol_table.kind_of(ident) == "FIELD":
                    self.vm_writer.write_push("THIS",
                                              self.symbol_table.index_of(
                                                  ident))
                elif self.symbol_table.kind_of(ident) == "VAR":
                    self.vm_writer.write_push("LOCAL",
                                              self.symbol_table.index_of(
                                                  ident))
                else:
                    self.vm_writer.write_push(self.symbol_table.kind_of(ident),
                                              self.symbol_table.index_of(
                                                  ident))

    def __compile_method_call(self, ident) -> None:
        """
        Compile method call, this is a specific call from a object,
        For example, In point we have Print -> Do print() will invoke this
        method. Also we note when the method is called from Constructor and
        push the correct address.
        """
        # self method call.
        self.__amount_of_expressions = 1
        if self.subroutine_type == "METHOD":
            self.vm_writer.write_push("ARG", 0)  # push this
        elif self.subroutine_type == "CONSTRUCTOR":
            self.vm_writer.write_push("POINTER", 0)
        self.input_tokenizer.advance()  # pass (
        self.compile_expression_list()
        self.input_tokenizer.advance()  # pass )
        self.vm_writer.write_call(f"{self.class_name}.{ident}",
                                  self.__amount_of_expressions)

    def __compile_subroutine_call(self, ident) -> None:
        """
        Compile subroutine call method or Function, this code know to differ
        between the cases and will hadnle cases of XXX.Method/func(...)
        """
        # subroutineCall case
        self.input_tokenizer.advance()  # pass .
        sub_name = self.input_tokenizer.identifier()
        # get sub identifier
        self.__amount_of_expressions = 0
        class_name = ident
        if self.symbol_table.type_of(ident) is not None:
            # case of method
            self.vm_writer.write_push(self.symbol_table.kind_of(ident)
                                      , self.symbol_table.index_of(ident))
            # push it as it will be used as this in the next call.
            self.__amount_of_expressions += 1
            class_name = self.symbol_table.type_of(ident)
            # change class name to the type of the instance.
        self.input_tokenizer.advance()  # pass name
        self.input_tokenizer.advance()  # pass (
        self.compile_expression_list()
        self.input_tokenizer.advance()  # pass  )
        self.vm_writer.write_call(f"{class_name}.{sub_name}",
                                  self.__amount_of_expressions)

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!
        if self.input_tokenizer.token_type() == "SYMBOL" \
                and self.input_tokenizer.symbol() == ")":
            return
        self.compile_expression()
        # returns the next token.
        self.__amount_of_expressions += 1
        while self.input_tokenizer.token_type() == "SYMBOL" \
                and self.input_tokenizer.symbol() == ",":
            self.input_tokenizer.advance()  # pass comma
            self.compile_expression()
            self.__amount_of_expressions += 1
