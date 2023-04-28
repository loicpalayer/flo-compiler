import json
from typing import List, TypeAlias

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None

class AST:

    def to_json(self) -> JSON:
        print(self.__class__.__name__)
        raise NotImplementedError("to_json not implemented")

    def __str__(self):
        return json.dumps(self.to_json(), indent=2)


class ListeInstructions(AST):

    def __init__(self):
        self.instructions = []

    def to_json(self) -> JSON:
        return {
            "instructions": list(map(lambda x: x.to_json(), self.instructions))
        }

    def addInstruction(self, instruction: AST):
        self.instructions.append(instruction)


class Programme(AST):

    def __init__(self, listeInstructions: ListeInstructions):
        self.listeInstructions = listeInstructions

    def to_json(self) -> JSON:
        return {"listeInstructions": self.listeInstructions.to_json()}


class Operation(AST):

    def __init__(self, op: str, exp1: AST, exp2: AST):
        self.lhs = exp1
        self.op = op
        self.rhs = exp2

    def to_json(self) -> JSON:
        return {
            "op": self.op,
            "lhs": self.lhs.to_json(),
            "rhs": self.rhs.to_json()
        }


class Entier(AST):

    def __init__(self, valeur: int):
        self.valeur = valeur

    def to_json(self) -> JSON:
        return {"entier": self.valeur}


class Booleen(AST):

    def __init__(self, valeur):
        self.valeur = valeur

    def to_json(self) -> JSON:
        return {"booleen": self.valeur}


class Identifiant(AST):

    def __init__(self, valeur: str):
        self.valeur = valeur

    def to_json(self) -> JSON:
        return {"identifiant": self.valeur}


class FunctionArgs(AST):

    def __init__(self, args: List[AST]):
        self.args = args

    def to_json(self) -> JSON:
        return list(map(lambda x: x.to_json(), self.args))

    def append(self, arg: AST):
        self.args.append(arg)

class AppelFonction(AST):

    def __init__(self, name: Identifiant, args: FunctionArgs):
        self.name = name
        self.args = args

    def to_json(self) -> JSON:
        return {"function_name": self.name.valeur, "args": self.args.to_json()}
