import json
from typing import Any, Dict


class AST:

    def to_json(self) -> Dict[str, Any]:
        print(self.__class__.__name__)
        raise NotImplementedError("to_json not implemented")

    def __str__(self):
        return json.dumps(self.to_json(), indent=2)


class ListeInstructions(AST):

    def __init__(self):
        self.instructions = []

    def to_json(self) -> Dict[str, Any]:
        return {
            "instructions": list(map(lambda x: x.to_json(), self.instructions))
        }

    def addInstruction(self, instruction: AST):
        self.instructions.append(instruction)


class Programme(AST):

    def __init__(self, listeInstructions: ListeInstructions):
        self.listeInstructions = listeInstructions

    def to_json(self) -> Dict[str, Any]:
        return {"listeInstructions": self.listeInstructions.to_json()}


class Operation(AST):

    def __init__(self, op: str, exp1: AST, exp2: AST):
        self.lhs = exp1
        self.op = op
        self.rhs = exp2

    def to_json(self) -> Dict[str, Any]:
        return {
            "op": self.op,
            "lhs": self.lhs.to_json(),
            "rhs": self.rhs.to_json()
        }


class Entier(AST):

    def __init__(self, valeur: int):
        self.valeur = valeur

    def to_json(self) -> Dict[str, Any]:
        return {"entier": self.valeur}


class Booleen(AST):

    def __init__(self, valeur):
        self.valeur = valeur

    def to_json(self) -> Dict[str, Any]:
        return {"booleen": self.valeur}


class Identifiant(AST):

    def __init__(self, valeur: str):
        self.valeur = valeur

    def to_json(self) -> Dict[str, Any]:
        return {"identifiant": self.valeur}


class AppelFonction(AST):

    def __init__(self, name: Identifiant, args: AST):
        self.name = name
        self.args = args

    def to_json(self) -> Dict[str, Any]:
        return {"function_name": self.name.valeur, "args": self.args.to_json()}
