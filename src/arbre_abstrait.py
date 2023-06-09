import enum
import json
from typing import List, Optional, TypeAlias

JSON: TypeAlias = dict[str,
                       "JSON"] | list["JSON"] | str | int | float | bool | None


class Type(enum.Enum):
    INCONNU = enum.auto()
    ENTIER = enum.auto()
    BOOLEEN = enum.auto()
    FONCTION = enum.auto()
    VIDE = enum.auto()

    @staticmethod
    def from_str(s: str) -> "Type":
        if s == "entier":
            return Type.ENTIER
        if s == "booleen":
            return Type.BOOLEEN
        return Type.INCONNU


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
        raise NotImplementedError("Programme has no type")
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
            if self.op in ["<", "<=", ">", ">=", "==", "!="]:
                return Type.BOOLEEN
            return self.lhs.type()
        print("op:", self.lhs.to_json(), self.rhs.to_json())
        return Type.INCONNU

    def to_json(self) -> JSON:
        return {
            "op": self.op,
            "lhs": self.lhs.to_json(),
            "rhs": self.rhs.to_json()
        }


class OperationUnaire(AST):

    def __init__(self, op: str, exp: AST):
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

    def __init__(self, valeur: bool):
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


class If(AST):

    def __init__(self, condition: AST, body: Programme,
                 orelse: Optional[Programme]):
        self.condition = condition
        self.body = body
        self.orelse = orelse or Programme([])

    def type(self) -> Type:
        return Type.AUTRE

    def add_elif(self, condition: AST, body: Programme):
        if self.orelse.instructions and isinstance(
                self.orelse.instructions[-1], If):
            self.orelse.instructions[-1].add_elif(condition, body)
        else:
            self.orelse.addInstruction(If(condition, body, None))

    def add_else(self, body: Programme):
        for i in body.instructions:
            self.orelse.addInstruction(i)

    def to_json(self) -> JSON:
        return {
            "condition": self.condition.to_json(),
            "body": self.body.to_json(),
            "orelse": self.orelse.to_json()
        }


class While(AST):

    def __init__(self, condition: AST, body: Programme):
        self.condition = condition
        self.body = body

    def type(self) -> Type:
        return Type.AUTRE

    def to_json(self) -> JSON:
        return {
            "condition": self.condition.to_json(),
            "body": self.body.to_json()
        }


class Declaration(AST):

    def __init__(self, name: Identifiant, _type: Type, value: Optional[AST]):
        self.name = name
        self._type = _type
        self.value = value

    def type(self) -> Type:
        return self._type

    def to_json(self) -> JSON:
        return {
            "name": self.name.to_json(),
            "type": self.type().name,
            "value": self.value.to_json() if self.value else None
        }


class Assignment(AST):

    def __init__(self, name: Identifiant, value: AST):
        self.name = name
        self.value = value

    def type(self) -> Type:
        return Type.AUTRE

    def to_json(self) -> JSON:
        return {"name": self.name.to_json(), "value": self.value.to_json()}


class Return(AST):

    def __init__(self, value: AST):
        self.value = value

    def type(self) -> Type:
        return Type.AUTRE

    def to_json(self) -> JSON:
        return {"return_value": self.value.to_json()}


class Function(AST):

    def __init__(self, name: Identifiant, args: List[Declaration],
                 body: Programme, return_type: Type):
        self.name = name
        self.args = args
        self.body = body
        self.return_type = return_type
        self.stack_size = 0

    def type(self) -> Type:
        return Type.FONCTION

    def to_json(self) -> JSON:
        return {
            "name": self.name.to_json(),
            "args": [a.to_json() for a in self.args],
            "body": self.body.to_json(),
            "return_type": self.return_type.name,
            "stack_size": self.stack_size
        }


class FunctionArgs(AST):

    def __init__(self, args: List[AST]):
        self.args = args

    def type(self) -> Type:
        return Type.AUTRE

    def to_json(self) -> JSON:
        return list(map(lambda x: x.to_json(), self.args))

    def __getitem__(self, i: int):
        return self.args[i]

    def __iter__(self):
        return iter(self.args)

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
