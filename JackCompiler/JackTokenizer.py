"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    """

    __keywords = {'class': 'CLASS', 'constructor': 'CONSTRUCTOR',
                  'function': 'FUNCTION', 'method': 'METHOD', 'field': 'FIELD',
                  'static': 'STATIC', 'var': 'VAR', 'int': 'INT',
                  'char': 'CHAR', 'boolean': 'BOOLEAN', 'void': 'VOID',
                  'true': 'TRUE', 'false': 'FALSE', 'null': 'NULL',
                  'this': 'THIS', 'let': 'LET', 'do': 'DO', 'if': 'IF',
                  'else': 'ELSE', 'while': 'WHILE', 'return': 'RETURN'}

    __symbols = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*',
                 '/', '&', '|', '<', '>', '=', '~', '^', '#'}

    __input_lines = []
    input_no_comments = []
    cur_token = ""
    __counter = 0
    __cur_line = []
    __cur_line_counter = 0

    def __remove_comments(self):
        """
        An helper function that integrating over a given list of lines and
        removes the comments.
        Returns: None, changing the list self.input_no_comments

        """
        counter = 0
        while counter < len(self.__input_lines):
            self.__input_lines[counter] = self.__input_lines[counter].strip()
            if self.__input_lines[counter][0:2] == "//" or \
                    len(self.__input_lines[counter]) == 0 or \
                    self.__input_lines[counter] == "\n":
                counter += 1
                continue
            if self.__input_lines[counter][0:2] == "/*" or \
                    self.__input_lines[counter][0:3] == "/**":
                while not ("*/" in self.__input_lines[counter]):
                    counter += 1
                ind = self.__input_lines[counter].find("*/")
                if ind != (len(self.__input_lines[counter]) - 1):
                    if "//" in self.__input_lines[counter][ind + 2:]:
                        ind_2 = self.__input_lines[counter][ind + 2:].find(
                            "//")
                        self.input_no_comments.append(
                            self.__input_lines[counter]
                            [ind + 2:ind_2].strip())
                    else:
                        self.input_no_comments.append(
                            self.__input_lines[counter]
                            [ind + 2:].strip())
                counter += 1
                continue
            if "//" in self.__input_lines[counter]:
                ind = self.__input_lines[counter].find("//")
                self.input_no_comments.append(
                    self.__input_lines[counter][:ind])
            else:
                self.input_no_comments.append(self.__input_lines[counter])
            counter += 1
        res = list()
        for i in range(len(self.input_no_comments)):
            if len(self.input_no_comments[i]) == 0:
                continue
            res.append(self.input_no_comments[i].strip())
        self.input_no_comments = res

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is:
        self.__input_lines = input_stream.read().splitlines()
        self.input_no_comments = []
        self.__counter = 0
        self.__remove_comments()
        self.__cur_line = self.input_no_comments[self.__counter]
        self.advance()

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        # Your code goes here!
        if self.__counter < len(self.input_no_comments):
            return True
        return False

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        # Your code goes here!
        if not self.has_more_tokens():
            return

        while self.__cur_line_counter < len(self.__cur_line):
            while self.__cur_line[self.__cur_line_counter] == " ":
                self.__cur_line_counter += 1
            cur_ind = self.__cur_line_counter
            if self.__cur_line[self.__cur_line_counter] == "\"":
                cur_ind += 1
                while self.__cur_line[cur_ind] != "\"":
                    cur_ind += 1
                self.cur_token = self.__cur_line[self.__cur_line_counter:
                                                 cur_ind + 1]
                self.__cur_line_counter = cur_ind + 1
                return
            if cur_ind == len(self.__cur_line) - 1:
                self.cur_token = self.__cur_line[cur_ind]
                self.__cur_line_counter = cur_ind + 1
                return

            while cur_ind < len(self.__cur_line) and self.__cur_line[cur_ind] \
                    != " ":
                if self.__cur_line[cur_ind] in self.__symbols:
                    if self.__cur_line_counter != cur_ind:
                        self.cur_token = self.__cur_line[
                                         self.__cur_line_counter:
                                         cur_ind]
                        self.__cur_line_counter = cur_ind
                        return
                    self.cur_token = self.__cur_line[cur_ind]
                    self.__cur_line_counter = cur_ind + 1
                    return
                cur_ind += 1

            self.cur_token = self.__cur_line[self.__cur_line_counter:cur_ind]
            self.__cur_line_counter = cur_ind
            return
        self.__counter += 1
        if not self.has_more_tokens():
            return
        self.__cur_line = self.input_no_comments[self.__counter]
        self.__cur_line_counter = 0
        self.advance()

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        # Your code goes here!
        if self.cur_token in self.__keywords.keys():
            return "KEYWORD"
        elif self.cur_token in self.__symbols:
            return "SYMBOL"
        elif self.cur_token.isdigit():
            return "INT_CONST"
        elif self.cur_token[0] == "\"":
            return 'STRING_CONST'
        else:
            return "IDENTIFIER"

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        # Your code goes here!
        return self.__keywords[self.cur_token]

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
        """
        # Your code goes here!
        return self.cur_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
        """
        # Your code goes here!
        return self.cur_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
        """
        # Your code goes here!
        return int(self.cur_token)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
        """
        # Your code goes here!
        return self.cur_token[1:-1]
