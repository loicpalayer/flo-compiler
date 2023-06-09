from typing import Dict, List

from src.arbre_abstrait import Declaration, Identifiant, Programme, Type, Function


class Variable:

    def __init__(self, name: Identifiant, type: Type, address: int):
        self.name = name
        self.type = type
        self.offset = address


Symbol = Function | Variable


class SymbolTable:

    def __init__(self):
        self._symbols: Dict[str, Symbol] = {}

    @staticmethod
    def from_program(program: Programme):
        symbol_table = SymbolTable()
        for instruction in program.instructions:
            if isinstance(instruction, Function):
                symbol_table.add(instruction)
        return symbol_table

    def check_presence(self, sym: Identifiant):
        if not sym in self:
            raise Exception(f"Le symbole {sym} n'est pas défini")

    def add(self, sym: Symbol):
        if sym in self:
            raise Exception(f"Le symbole {sym.name} est déjà défini")
        self._symbols[sym.name.valeur] = sym

    def get(self, sym: Identifiant) -> Symbol:
        self.check_presence(sym)
        return self._symbols[sym.valeur]

    def remove(self, sym: Identifiant):
        if not sym in self:
            raise Exception(f"Le symbole {sym.name} n'est pas défini")
        del self._symbols[sym.valeur]

    def type(self, func: Identifiant) -> Type:
        self.check_presence(func)
        return self._symbols[func.valeur].return_type

    def args(self, func: Identifiant) -> List[Declaration]:
        self.check_presence(func)
        return self._symbols[func.valeur].args

    def memory_size(self, func: Identifiant) -> int:
        self.check_presence(func)
        return 4 * len(self.args(func))

    def __contains__(self, sym: Symbol | Identifiant):
        if isinstance(sym, Identifiant):
            return sym.valeur in self._symbols

        return sym.name.valeur in self._symbols

    def __str__(self):
        return '\n'.join([str(symbol) for symbol in self._symbols.values()])