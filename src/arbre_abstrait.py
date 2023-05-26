import enum
import json
from typing import List, TypeAlias

JSON: TypeAlias = dict[str,
                       "JSON"] | list["JSON"] | str | int | float | bool | None


class Type(enum.Enum):
    INCONNU = enum.auto()
    ENTIER = enum.auto()
    BOOLEEN = enum.auto()
    FONCTION = enum.auto()
    AUTRE = enum.auto()


class AST:

    def to_json(self) -> JSON:
        print(self.__class__.__name__)
        raise NotImplementedError("to_json not implemented")

    def type(self) -> Type:
        return Type.INCONNU

    def __str__(self):
        return json.dumps(self.to_json(), indent=2)


class Programme(AST):

    def __init__(self, instructions: List[AST]):
        self.instructions = instructions

    def type(self) -> Type:
        return Type.AUTRE

    def to_json(self) -> JSON:
        return {"instructions": [i.to_json() for i in self.instructions]}

    def addInstruction(self, instruction: AST):
        self.instructions.append(instruction)


class Operation(AST):

    def __init__(self, op: str, exp1: AST, exp2: AST):
        self.lhs = exp1
        self.op = op
        self.rhs = exp2

    def type(self) -> Type:
        if self.lhs.type() == self.rhs.type():
            return self.lhs.type()
        return Type.INCONNU

    def to_json(self) -> JSON:
        return {
            "op": self.op,
            "lhs": self.lhs.to_json(),
            "rhs": self.rhs.to_json()
        }


class OperationUnaire(AST):

    def __init__(self, op: str, exp: AST):
        print("OperationUnaire", op, exp)
        self.op = op
        self.exp = exp

    def type(self) -> Type:
        return self.exp.type()

    def to_json(self) -> JSON:
        return {"op": self.op, "exp": self.exp.to_json()}


class Entier(AST):

    def __init__(self, valeur: int):
        self.valeur = valeur

    def type(self) -> Type:
        return Type.ENTIER

    def __eq__(self, rhs: object) -> bool:
        if isinstance(rhs, Entier):
            return self.valeur == rhs.valeur
        return self.valeur == rhs

    def to_json(self) -> JSON:
        return {"entier": self.valeur}


class Booleen(AST):

    def __init__(self, valeur):
        self.valeur = valeur

    def type(self) -> Type:
        return Type.BOOLEEN

    def __eq__(self, rhs: object) -> bool:
        if isinstance(rhs, Booleen):
            return self.valeur == rhs.valeur
        return self.valeur == rhs

    def to_json(self) -> JSON:
        return {"booleen": self.valeur}


class Identifiant(AST):

    def __init__(self, valeur: str):
        self.valeur = valeur

    def type(self) -> Type:
        return Type.AUTRE

    def __eq__(self, rhs: object) -> bool:
        if isinstance(rhs, Identifiant):
            return self.valeur == rhs.valeur
        return self.valeur == rhs

    def to_json(self) -> JSON:
        return {"identifiant": self.valeur}


class FunctionArgs(AST):

    def __init__(self, args: List[AST]):
        self.args = args

    def type(self) -> Type:
        return Type.AUTRE

    def to_json(self) -> JSON:
        return list(map(lambda x: x.to_json(), self.args))

    def __getitem__(self, i):
        return self.args[i]

    def append(self, arg: AST):
        self.args.append(arg)


class AppelFonction(AST):

    def __init__(self, name: Identifiant, args: FunctionArgs):
        self.name = name
        self.args = args

    def type(self) -> Type:
        return Type.INCONNU

    def to_json(self) -> JSON:
        return {"function_name": self.name.valeur, "args": self.args.to_json()}
