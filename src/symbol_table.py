from typing import Dict

from src.arbre_abstrait import Identifiant, Programme, Type, Function


class SymbolTable:

    def __init__(self):
        self._symbols: Dict[str, Type] = {}

    @staticmethod
    def from_program(program: Programme):
        symbol_table = SymbolTable()
        for instruction in program.instructions:
            if isinstance(instruction, Function):
                symbol_table.add(instruction)
        return symbol_table

    def add(self, func: Function):
        if func in self:
            raise Exception(f"La fonction {func.name} est déjà définie")
        self._symbols[func.name.valeur] = func.return_type

    def get(self, name: Identifiant) -> Type:
        if not name in self:
            raise Exception(f"La fonction {name} n'est pas définie")
        return self._symbols[name.valeur]

    def __contains__(self, func: Function | Identifiant):
        if isinstance(func, Identifiant):
            return func.valeur in self._symbols

        return func.name.valeur in self._symbols

    def __str__(self):
        return '\n'.join([str(symbol) for symbol in self._symbols.values()])