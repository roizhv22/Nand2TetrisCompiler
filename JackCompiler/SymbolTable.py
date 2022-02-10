"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """
    class_table = ""
    subroutine_table = ""
    __field_counter = -1
    __static_counter = -1
    __args_counter = -1
    __local_counter = -1
    __KIND_IND = 1
    __TYPE_IND = 0
    __COUNT = 2

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        # Your code goes here!
        self.__class_table = dict()
        self.__subroutine_table = dict()

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        # Your code goes here!
        self.__subroutine_table = dict()
        self.__local_counter = -1
        self.__args_counter = -1

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        # Your code goes here!
        if kind == "STATIC":
            self.__static_counter += 1
            self.__class_table[name] = (type, "STATIC", self.__static_counter)
        elif kind == "FIELD":
            self.__field_counter += 1
            self.__class_table[name] = (type, "FIELD", self.__field_counter)
        elif kind == "ARG":
            self.__args_counter += 1
            self.__subroutine_table[name] = (type, "ARG", self.__args_counter)
        elif kind == "VAR":
            self.__local_counter += 1
            self.__subroutine_table[name] = (type, "VAR",
                                             self.__local_counter)

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        # Your code goes here!
        if kind == "STATIC":
            return self.__static_counter + 1
        elif kind == "FIELD":
            return self.__field_counter + 1
        elif kind == "ARG":
            return self.__args_counter + 1
        elif kind == "VAR":
            return self.__local_counter + 1

    def __get_val_from_dict(self, name, field):
        """
        Gets the correct value from the dict - as we implemented as dict of
        str-tuple so we need to get the correct value from the tuple.
        """
        if name in self.__subroutine_table.keys():
            return self.__subroutine_table[name][field]
        if name in self.__class_table.keys():
            return self.__class_table[name][field]
        return None

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        # Your code goes here!
        return self.__get_val_from_dict(name, self.__KIND_IND)

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        # Your code goes here!
        return self.__get_val_from_dict(name, self.__TYPE_IND)

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        # Your code goes here!
        return self.__get_val_from_dict(name, self.__COUNT)
