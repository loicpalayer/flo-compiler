from typing import Dict, List

from src.arbre_abstrait import Declaration, Identifiant, Programme, Type, Function


class SymbolTable:

    def __init__(self):
        self._symbols: Dict[str, Function] = {}

    @staticmethod
    def from_program(program: Programme):
        symbol_table = SymbolTable()
        for instruction in program.instructions:
            if isinstance(instruction, Function):
                symbol_table.add(instruction)
        return symbol_table

    def check_presence(self, func: Identifiant):
        if not func in self:
            raise Exception(f"La fonction {func} n'est pas définie")

    def add(self, func: Function):
        if func in self:
            raise Exception(f"La fonction {func.name} est déjà définie")
        self._symbols[func.name.valeur] = func

    def type(self, name: Identifiant) -> Type:
        self.check_presence(name)
        return self._symbols[name.valeur].return_type

    def args(self, func: Identifiant) -> List[Declaration]:
        self.check_presence(func)
        return self._symbols[func.valeur].args

    def memory_size(self, func: Identifiant) -> int:
        self.check_presence(func)
        return 4 * len(self.args(func))

    def __contains__(self, func: Function | Identifiant):
        if isinstance(func, Identifiant):
            return func.valeur in self._symbols

        return func.name.valeur in self._symbols

    def __str__(self):
        return '\n'.join([str(symbol) for symbol in self._symbols.values()])