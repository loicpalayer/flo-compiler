import sys
from typing import List, Optional
from src.analyse_syntaxique import analyse_syntaxique
import src.arbre_abstrait as arbre_abstrait
from src.symbol_table import SymbolTable

num_etiquette_courante = -1  #Permet de donner des noms différents à toutes les étiquettes (en les appelant e0, e1,e2,...)

afficher_table = False
afficher_nasm = True

current_function: Optional[arbre_abstrait.Function] = None


def check_type(expr: arbre_abstrait.AST, expected: arbre_abstrait.Type):
    """
    Fonction locale, permet de vérifier que le type d'une expression est bien celui attendu.
    """
    if expr.type() != expected:
        raise Exception(
            f"Erreur de type: {expr} est de type {expr.type()} au lieu de {expected}"
        )


def printifm(*args, **kwargs):
    """
    Un print qui ne fonctionne que si la variable afficher_table vaut Vrai.
    (permet de choisir si on affiche le code assembleur ou la table des symboles)
    """
    if afficher_nasm:
        print(*args, **kwargs)


def printift(*args, **kwargs):
    """
    Un print qui ne fonctionne que si la variable afficher_table vaut Vrai.
    (permet de choisir si on affiche le code assembleur ou la table des symboles)
    """
    if afficher_table:
        print(*args, **kwargs)


def nasm_comment(comment):
    """
    Fonction locale, permet d'afficher un commentaire dans le code nasm.
    """
    if comment != "":
        printifm(
            "\t\t ; " + comment
        )  #le point virgule indique le début d'un commentaire en nasm. Les tabulations sont là pour faire jolie.
    else:
        printifm("")


def nasm_instruction(opcode, op1="", op2="", op3="", comment=""):
    """
    Affiche une instruction nasm sur une ligne
    Par convention, les derniers opérandes sont nuls si l'opération a moins de 3 arguments.
    """
    if op2 == "":
        printifm("\t" + opcode + "\t" + op1 + "\t\t", end="")
    elif op3 == "":
        printifm("\t" + opcode + "\t" + op1 + ",\t" + op2 + "\t", end="")
    else:
        printifm("\t" + opcode + "\t" + op1 + ",\t" + op2 + ",\t" + op3,
                 end="")
    nasm_comment(comment)


def nasm_nouvelle_etiquette():
    """
    Retourne le nom d'une nouvelle étiquette
    """
    global num_etiquette_courante
    num_etiquette_courante += 1
    return "e" + str(num_etiquette_courante)


def gen_entrypoint(programme: arbre_abstrait.Programme):
    """
    Affiche le code nasm correspondant à tout un programme
    """
    printifm('%include\t"io.asm"')
    printifm('section\t.bss')
    printifm(
        'sinput:	resb	255	;reserve a 255 byte space in memory for the users input string'
    )
    printifm('v$a:	resd	1')
    printifm('section\t.text')
    printifm('global _start')

    symbol_table = SymbolTable.from_program(programme)
    printift(symbol_table)

    gen_programme(programme, symbol_table, is_main=True)

    nasm_instruction("mov", "eax", "1", "", "1 est le code de SYS_EXIT")
    nasm_instruction("int", "0x80", "", "", "exit")


def gen_programme(programme: arbre_abstrait.Programme,
                  symbol_table: SymbolTable,
                  is_main=False):

    funcs = [
        instruction for instruction in programme.instructions
        if isinstance(instruction, arbre_abstrait.Function)
    ]
    for func in funcs:
        gen_function(func, symbol_table)

    if is_main:
        printifm('_start:')

    instrs = [
        instruction for instruction in programme.instructions
        if not isinstance(instruction, arbre_abstrait.Function)
    ]
    gen_listeInstructions(instrs, symbol_table)


def gen_listeInstructions(instructions: List[arbre_abstrait.AST],
                          symbol_table: SymbolTable):
    """
    Affiche le code nasm correspondant à une suite d'instructions
    """
    for instruction in instructions:
        gen_instruction(instruction, symbol_table)


def gen_return(return_: arbre_abstrait.Return, symbol_table: SymbolTable):
    """
    Affiche le code nasm correspondant à un return. Met sa valeur dans eax avant de revenir
à l’appel de la fonction grâce à l’instruction nasm ret
    """

    if current_function is None:
        raise Exception("return en dehors d'une fonction")

    if current_function.return_type != return_.value.type():
        raise Exception("return de type différent de la fonction")

    gen_expression(return_.value, symbol_table)
    nasm_instruction("pop", "eax", "", "", "")
    nasm_instruction("ret", "", "", "", "retourne à l'appel de la fonction")


def gen_instruction(instruction: arbre_abstrait.AST,
                    symbol_table: SymbolTable):
    """
    Affiche le code nasm correspondant à une instruction
    """
    if isinstance(instruction, arbre_abstrait.Function):
        gen_function(instruction, symbol_table)
    elif isinstance(instruction, arbre_abstrait.Return):
        gen_return(instruction, symbol_table)
    else:
        gen_expression(instruction, symbol_table)


class Builtins:

    @staticmethod
    def ecrire(arg: arbre_abstrait.AST, symbol_table: SymbolTable):
        """
        Affiche le code nasm correspondant au fait d'envoyer la valeur entière d'une expression sur la sortie standard
        """
        # on calcule et empile la valeur d'expression
        gen_expression(arg, symbol_table)
        # on dépile la valeur d'expression sur eax
        nasm_instruction("pop", "eax", "", "", "")
        # on envoie la valeur d'eax sur la sortie standard
        nasm_instruction("call", "iprintLF", "", "", "")

    @staticmethod
    def lire(symbol_table: SymbolTable):
        """
        Affiche le code nasm correspondant au fait de lire un entier sur l'entrée standard et de le mettre dans une variable
        """
        nasm_instruction("mov", "eax", "sinput", "", "")
        nasm_instruction("call", "readline", "", "", "")
        nasm_instruction("call", "atoi", "", "", "")
        nasm_instruction("push", "eax", "", "", "")


def gen_appel_fonction(fonction: arbre_abstrait.AppelFonction,
                       symbol_table: SymbolTable):
    """
    Affiche le code nasm correspondant à l'appel d'une fonction
    """
    if fct := getattr(Builtins, fonction.name.valeur, None):
        fct(*fonction.args, symbol_table=symbol_table)
    elif fonction.name in symbol_table:
        gen_appel_fonction_user(fonction, symbol_table)
    else:
        print("fonction inconnue", fonction.name)
        exit(0)


def gen_appel_fonction_user(fonction: arbre_abstrait.AppelFonction,
                            symbol_table: SymbolTable):
    """
    Affiche le code nasm correspondant à l'appel d'une fonction utilisateur
    """
    # on empile les arguments de la fonction
    for arg in fonction.args:
        gen_expression(arg, symbol_table)

    # on appelle la fonction
    nasm_instruction("call", f"_{fonction.name.valeur}", "", "", "")

    # on empile la valeur de retour de la fonction
    nasm_instruction("push", "eax", "", "", "")


def gen_function(fonction: arbre_abstrait.Function, symbol_table: SymbolTable):
    """
    Affiche le code nasm correspondant à la définition d'une fonction
    """
    printift(fonction)

    global current_function
    current_function = fonction

    printifm(f"_{fonction.name.valeur}:")
    gen_listeInstructions(fonction.body.instructions, symbol_table)

    current_function = None


def gen_expression(expression: arbre_abstrait.AST, symbol_table: SymbolTable):
    """
    Affiche le code nasm pour calculer et empiler la valeur d'une expression
    """
    if type(expression) == arbre_abstrait.Operation:
        # on calcule et empile la valeur de l'opération
        gen_operation(expression, symbol_table)
    elif type(expression) == arbre_abstrait.OperationUnaire:
        gen_operation_unaire(expression, symbol_table)
    elif type(expression) == arbre_abstrait.Entier or type(
            expression) == arbre_abstrait.Booleen:
        # on met sur la pile la valeur entière
        nasm_instruction("push", str(int(expression.valeur)), "", "", "")
    elif type(expression) == arbre_abstrait.AppelFonction:
        gen_appel_fonction(expression, symbol_table)
    else:
        print("type d'expression inconnu", type(expression))
        exit(0)


def gen_operation(operation: arbre_abstrait.Operation,
                  symbol_table: SymbolTable):
    """
    Affiche le code nasm pour calculer l'opération et la mettre en haut de la pile
    """

    op = operation.op

    gen_expression(operation.lhs,
                   symbol_table)  # on calcule et empile la valeur de exp1
    gen_expression(operation.rhs,
                   symbol_table)  # on calcule et empile la valeur de exp2

    nasm_instruction("pop", "ebx", "", "",
                     "dépile la seconde operande dans ebx")
    nasm_instruction("pop", "eax", "", "",
                     "dépile la permière operande dans eax")

    code = {
        "+": "add",
        "*": "imul",
        "-": "sub",
        "/": "div",
        "%": "mod",
        "et": "and",
        "ou": "or",
    }
    # Un dictionnaire qui associe à chaque opérateur sa fonction nasm
    # Voir: https://www.bencode.net/blob/nasmcheatsheet.pdf
    if op in ['+', '-']:
        check_type(operation, arbre_abstrait.Type.ENTIER)

        nasm_instruction(
            code[op], "eax", "ebx", "", "effectue l'opération eax" + op +
            "ebx et met le résultat dans eax")
    elif op == '*':
        check_type(operation, arbre_abstrait.Type.ENTIER)

        nasm_instruction(
            code[op], "ebx", "", "", "effectue l'opération eax" + op +
            "ebx et met le résultat dans eax")
    elif op == '/':
        check_type(operation, arbre_abstrait.Type.ENTIER)

        nasm_instruction("mov", "edx", "0", "", "met edx à 0")

        nasm_instruction(
            code[op], "ebx", "", "", "effectue l'opération edx:eax" + op +
            "ebx et met le résultat dans eax")
    elif op == '%':
        check_type(operation, arbre_abstrait.Type.ENTIER)

        nasm_instruction("mov", "edx", "0", "", "met edx à 0")
        nasm_instruction(
            "idiv", "ebx", "", "", "effectue l'opération eax" + op +
            "ebx et met le résultat dans edx")
    elif op in ["ou", "et"]:
        check_type(operation, arbre_abstrait.Type.BOOLEEN)

        nasm_instruction(
            code[op], "eax", "ebx", "", "effectue l'opération eax" + op +
            "ebx et met le résultat dans eax")

    elif op in ["<", "<=", ">", ">=", "==", "!="]:
        gen_comparison(operation)

    else:
        print("type d'opération inconnu", op)
        exit(0)

    target = "edx" if op == "%" else "eax"

    nasm_instruction("push", target, "", "", "empile le résultat")


def gen_operation_unaire(operation: arbre_abstrait.OperationUnaire,
                         symbol_table: SymbolTable):
    op = operation.op

    gen_expression(operation.exp,
                   symbol_table)  # on calcule et empile la valeur de exp
    nasm_instruction("pop", "eax", "", "",
                     "dépile la première operande dans eax")

    if op == '-':
        check_type(operation, arbre_abstrait.Type.ENTIER)
        nasm_instruction("neg", "eax", "", "", "effectue l'opération -eax")
    elif op == "non":
        check_type(operation, arbre_abstrait.Type.BOOLEEN)
        nasm_instruction("xor", "eax", "1", "", "effectue l'opération not eax")
    else:
        print("type d'opération unaire inconnu")
        exit(0)

    nasm_instruction("push", "eax", "", "", "empile le résultat")


def gen_comparison(expr: arbre_abstrait.Operation):
    """
    Génère le code pour une comparaison
    """

    check_type(expr, arbre_abstrait.Type.ENTIER)

    # On effectue la comparaison
    nasm_instruction("cmp", "eax", "ebx", "", "compare eax et ebx")
    if expr.op == '<':
        nasm_instruction("setl", "al", "", "", "met al à 1 si eax < ebx")
    elif expr.op == '<=':
        nasm_instruction("setle", "al", "", "", "met al à 1 si eax <= ebx")
    elif expr.op == '>':
        nasm_instruction("setg", "al", "", "", "met al à 1 si eax > ebx")
    elif expr.op == '>=':
        nasm_instruction("setge", "al", "", "", "met al à 1 si eax >= ebx")
    elif expr.op == '==':
        nasm_instruction("sete", "al", "", "", "met al à 1 si eax == ebx")
    elif expr.op == '!=':
        nasm_instruction("setne", "al", "", "", "met al à 1 si eax != ebx")
    else:
        print("type de comparaison inconnu")
        exit(0)


def main():
    global afficher_nasm
    global afficher_tableSymboles

    afficher_nasm = True
    if len(sys.argv) < 3 or sys.argv[1] not in ["-nasm", "-table"]:
        print(
            "usage: python3 generation_code.py -nasm|-table NOM_FICHIER_SOURCE.flo"
        )
        exit(0)
    if sys.argv[1] == "-nasm":
        afficher_nasm = True
    if sys.argv[1] == "-table":
        afficher_tableSymboles = True

    with open(sys.argv[2], "r") as f:
        data = f.read()
        try:
            arbre = analyse_syntaxique(data)
            gen_entrypoint(arbre)
        except EOFError:
            exit()


if __name__ == "__main__":
    main()
