from typing import List, Optional
import src.arbre_abstrait as arbre_abstrait
from src.arbre_abstrait import Entier, Type
from src.symbol_table import SymbolTable, Variable

num_etiquette_courante = -1  #Permet de donner des noms différents à toutes les étiquettes (en les appelant e0, e1,e2,...)

afficher_table = False
afficher_nasm = True

current_function: Optional[arbre_abstrait.Function] = None
current_depth: int = 0
pre_pass = False


def check_type(expected: Type, *args: Type):
    """
    Fonction locale, permet de vérifier que le type d'une expression est bien celui attendu.
    """
    for arg in args:
        if arg != expected:
            raise Exception(
                f"Le type de l'expression est {arg} alors que le type attendu est {expected.name}"
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
    nasm_instruction("mov", "ebx", "0", "", "0 est le code de retour")
    nasm_instruction("int", "0x80", "", "", "exit")


def gen_programme(programme: arbre_abstrait.Programme,
                  symbol_table: SymbolTable,
                  is_main: bool = False):

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
    main_func = arbre_abstrait.Function(arbre_abstrait.Identifiant("_main"),
                                        [], arbre_abstrait.Programme(instrs),
                                        Type.VIDE)
    gen_function(main_func, symbol_table)
    #gen_listeInstructions(instrs, symbol_table)


def gen_listeInstructions(instructions: List[arbre_abstrait.AST],
                          symbol_table: SymbolTable):
    """
    Affiche le code nasm correspondant à une suite d'instructions
    """
    global current_depth
    current_depth += 1
    for instruction in instructions:
        gen_instruction(instruction, symbol_table)
    vars = symbol_table.end_block(current_depth)
    if not afficher_nasm:
        current_function.stack_size += 4 * len(vars)
    current_depth -= 1


def gen_return(return_: arbre_abstrait.Return, symbol_table: SymbolTable):
    """
    Affiche le code nasm correspondant à un return. Met sa valeur dans eax avant de revenir
à l’appel de la fonction grâce à l’instruction nasm ret
    """

    if current_function is None:
        raise Exception("return en dehors d'une fonction")

    ty_expr = gen_expression(return_.value, symbol_table)

    if current_function.return_type != ty_expr:
        raise Exception("return de type différent de la fonction")

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
    elif isinstance(instruction, arbre_abstrait.If):
        gen_if(instruction, symbol_table)
    elif isinstance(instruction, arbre_abstrait.While):
        gen_while(instruction, symbol_table)
    elif isinstance(instruction, arbre_abstrait.Declaration):
        gen_declaration(instruction, symbol_table)
    else:
        ty_expr = gen_expression(instruction, symbol_table)
        if ty_expr != Type.VIDE:
            nasm_instruction("pop", "eax", "", "", "")


def gen_declaration(declaration: arbre_abstrait.Declaration,
                    symbol_table: SymbolTable):
    """
    Affiche le code nasm correspondant à une déclaration
    """

    if current_function is None:
        raise Exception("declaration en dehors d'une fonction")

    ty_decl = declaration._type
    if declaration.value is None:
        if ty_decl == Type.ENTIER:
            declaration.value = arbre_abstrait.Entier(0)
        elif ty_decl == Type.BOOLEEN:
            declaration.value = arbre_abstrait.Booleen(False)
    ty_val = gen_expression(declaration.value, symbol_table)
    check_type(ty_decl, ty_val)

    offset = symbol_table.next_address()
    symbol_table.add(Variable(declaration.name, ty_decl, offset,
                              current_depth))

    nasm_instruction("pop", "eax", "", "", "")
    nasm_instruction("mov", f"[ebp-{offset}]", "eax", "", "")


def gen_if(if_: arbre_abstrait.If, symbol_table: SymbolTable):
    """
    Affiche le code nasm correspondant à un if
    """
    ty_cond = gen_expression(if_.condition, symbol_table)
    check_type(Type.BOOLEEN, ty_cond)
    nasm_instruction("pop", "eax", "", "", "")
    nasm_instruction("cmp", "eax", "0", "", "")
    if if_.orelse.instructions:
        etiq_else = nasm_nouvelle_etiquette()
        nasm_instruction("je", etiq_else, "", "", "")
        gen_listeInstructions(if_.body.instructions, symbol_table)
        etiq_fin = nasm_nouvelle_etiquette()
        nasm_instruction("jmp", etiq_fin, "", "", "")
        nasm_instruction(etiq_else + ":", "", "", "", "")
        gen_listeInstructions(if_.orelse.instructions, symbol_table)
        nasm_instruction(etiq_fin + ":", "", "", "", "")
    else:
        etig_fin = nasm_nouvelle_etiquette()
        nasm_instruction("je", etig_fin, "", "", "")
        gen_listeInstructions(if_.body.instructions, symbol_table)
        nasm_instruction(etig_fin + ":", "", "", "", "")


def gen_while(while_: arbre_abstrait.While, symbol_table: SymbolTable):
    """
    Affiche le code nasm correspondant à un while
    """
    etiq_debut = nasm_nouvelle_etiquette()
    etiq_fin = nasm_nouvelle_etiquette()
    nasm_instruction(etiq_debut + ":", "", "", "", "")
    ty_cond = gen_expression(while_.condition, symbol_table)
    check_type(Type.BOOLEEN, ty_cond)
    nasm_instruction("pop", "eax", "", "", "")
    nasm_instruction("cmp", "eax", "0", "", "")
    nasm_instruction("je", etiq_fin, "", "", "")
    gen_listeInstructions(while_.body.instructions, symbol_table)
    nasm_instruction("jmp", etiq_debut, "", "", "")
    nasm_instruction(etiq_fin + ":", "", "", "", "")


class Builtins:

    @staticmethod
    def ecrire(arg: arbre_abstrait.AST, symbol_table: SymbolTable) -> Type:
        """
        Affiche le code nasm correspondant au fait d'envoyer la valeur entière d'une expression sur la sortie standard
        """
        # on calcule et empile la valeur d'expression
        gen_expression(arg, symbol_table)
        # on dépile la valeur d'expression sur eax
        nasm_instruction("pop", "eax", "", "", "")
        # on envoie la valeur d'eax sur la sortie standard
        nasm_instruction("call", "iprintLF", "", "", "")
        return Type.VIDE

    @staticmethod
    def lire(symbol_table: SymbolTable) -> Type:
        """
        Affiche le code nasm correspondant au fait de lire un entier sur l'entrée standard et de le mettre dans une variable
        """
        nasm_instruction("mov", "eax", "sinput", "", "")
        nasm_instruction("call", "readline", "", "", "")
        nasm_instruction("call", "atoi", "", "", "")
        nasm_instruction("push", "eax", "", "", "")
        return Type.ENTIER


def gen_appel_fonction(fonction: arbre_abstrait.AppelFonction,
                       symbol_table: SymbolTable) -> Type:
    """
    Affiche le code nasm correspondant à l'appel d'une fonction
    """
    if fct := getattr(Builtins, fonction.name.valeur, None):
        return fct(*fonction.args, symbol_table=symbol_table)
    elif fonction.name in symbol_table:
        return gen_appel_fonction_user(fonction, symbol_table)
    else:
        raise Exception("fonction inconnue", fonction.name.to_json())


def gen_appel_fonction_user(fonction_call: arbre_abstrait.AppelFonction,
                            symbol_table: SymbolTable) -> Type:
    """
    Affiche le code nasm correspondant à l'appel d'une fonction utilisateur
    """

    f_args = symbol_table.args(fonction_call.name)

    # on empile la valeur de ebp avant de la changer (ancien esp-4) (ou -8).
    nasm_instruction("push", "ebp", "", "", "")

    # on déplace ebp pour qu'il pointe sur l'ancien esp
    nasm_instruction("mov", "ebp", "esp", "", "")

    nasm_instruction("sub", "esp",
                     str(symbol_table.memory_size_locals(fonction_call.name)),
                     "", "")

    # on empile les arguments de la fonction
    for i, arg in enumerate(fonction_call.args):
        ty_arg = gen_expression(arg, symbol_table)
        if i >= len(f_args) or f_args[i].type() != ty_arg:
            raise Exception("type d'argument différent de la fonction: ",
                            ty_arg, f_args[i].to_json())

    # on appelle la fonction
    nasm_instruction("call", f"_{fonction_call.name.valeur}", "", "", "")

    # on désalloue la mémoire de la fonction (en déplaçant esp)
    nasm_instruction("add", "esp",
                     str(symbol_table.memory_size(fonction_call.name)), "", "")

    # on dépile la valeur de ebp avant de la changer (ancien esp+4) (ou +8).
    nasm_instruction("pop", "ebp", "", "", "")

    # on empile la valeur de retour de la fonction
    nasm_instruction("push", "eax", "", "", "")

    return symbol_table.type(fonction_call.name)


def gen_function(fonction: arbre_abstrait.Function, symbol_table: SymbolTable):
    """
    Affiche le code nasm correspondant à la définition d'une fonction
    """
    printift(fonction)

    global current_function, afficher_nasm
    current_function = fonction

    printifm(f"_{fonction.name.valeur}:")

    # on ajoute les arguments de la fonction dans la table des symboles
    for i, arg in enumerate(fonction.args):
        symbol_table.add(
            Variable(arg.name, arg.type(), i * 4 + 4, current_depth))

    afficher_nasm = False
    gen_listeInstructions(fonction.body.instructions, symbol_table)
    afficher_nasm = True
    gen_listeInstructions(fonction.body.instructions, symbol_table)

    current_function = None
    # on supprime les arguments de la fonction de la table des symboles
    for arg in fonction.args:
        symbol_table.remove(arg.name)


def gen_variable(id: arbre_abstrait.Identifiant,
                 symbol_table: SymbolTable) -> Type:
    """
    Affiche le code nasm correspondant à l'accès à une variable
    """

    var = symbol_table.get(id)
    if not isinstance(var, Variable):
        raise Exception("identifiant inconnu", id)

    nasm_instruction("mov", "eax", f"[ebp-{var.offset}]", "", "")
    nasm_instruction("push", "eax", "", "", "")
    return var.type


def gen_expression(expression: arbre_abstrait.AST,
                   symbol_table: SymbolTable) -> arbre_abstrait.Type:
    """
    Affiche le code nasm pour calculer et empiler la valeur d'une expression
    """
    if type(expression) == arbre_abstrait.Operation:
        # on calcule et empile la valeur de l'opération
        return gen_operation(expression, symbol_table)
    elif type(expression) == arbre_abstrait.OperationUnaire:
        return gen_operation_unaire(expression, symbol_table)
    elif type(expression) == arbre_abstrait.Entier:
        # on met sur la pile la valeur entière
        nasm_instruction("push", str(int(expression.valeur)), "", "", "")
        return arbre_abstrait.Type.ENTIER
    elif type(expression) == arbre_abstrait.Booleen:
        # on met sur la pile la valeur booléenne (0 ou 1)
        nasm_instruction("push", str(int(expression.valeur)), "", "", "")
        return arbre_abstrait.Type.BOOLEEN
    elif type(expression) == arbre_abstrait.AppelFonction:
        return gen_appel_fonction(expression, symbol_table)
    elif type(expression) == arbre_abstrait.Identifiant:
        return gen_variable(expression, symbol_table)
    elif type(expression) == arbre_abstrait.Assignment:
        return gen_assignment(expression, symbol_table)
    else:
        raise Exception("type d'expression inconnu: " + str(type(expression)) +
                        ", " + str(expression.to_json()))


def gen_assignment(assignment: arbre_abstrait.Assignment,
                   symbol_table: SymbolTable) -> Type:
    """
    Affiche le code nasm pour l'assignation d'une variable
    """
    type = gen_expression(assignment.value, symbol_table)
    var = symbol_table.get(assignment.name)
    if not isinstance(var, Variable):
        raise Exception("identifiant inconnu", assignment.name)

    nasm_instruction("pop", "eax", "", "", "")
    nasm_instruction("mov", f"[ebp-{var.offset}]", "eax", "", "")
    return Type.VIDE


def gen_operation(operation: arbre_abstrait.Operation,
                  symbol_table: SymbolTable) -> Type:
    """
    Affiche le code nasm pour calculer l'opération et la mettre en haut de la pile
    """

    op = operation.op

    type_lhs = gen_expression(
        operation.lhs, symbol_table)  # on calcule et empile la valeur de exp1
    type_rhs = gen_expression(
        operation.rhs, symbol_table)  # on calcule et empile la valeur de exp2

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
        check_type(Type.ENTIER, type_lhs, type_rhs)

        nasm_instruction(
            code[op], "eax", "ebx", "", "effectue l'opération eax" + op +
            "ebx et met le résultat dans eax")
        res_type = Type.ENTIER
    elif op == '*':
        check_type(Type.ENTIER, type_lhs, type_rhs)

        nasm_instruction(
            code[op], "ebx", "", "", "effectue l'opération eax" + op +
            "ebx et met le résultat dans eax")
        res_type = Type.ENTIER
    elif op == '/':
        check_type(Type.ENTIER, type_lhs, type_rhs)

        nasm_instruction("mov", "edx", "0", "", "met edx à 0")

        nasm_instruction(
            code[op], "ebx", "", "", "effectue l'opération edx:eax" + op +
            "ebx et met le résultat dans eax")
        res_type = Type.ENTIER
    elif op == '%':
        check_type(Type.ENTIER, type_lhs, type_rhs)

        nasm_instruction("mov", "edx", "0", "", "met edx à 0")
        nasm_instruction(
            "idiv", "ebx", "", "", "effectue l'opération eax" + op +
            "ebx et met le résultat dans edx")
        res_type = Type.ENTIER
    elif op in ["ou", "et"]:
        check_type(arbre_abstrait.Type.BOOLEEN, type_lhs, type_rhs)

        nasm_instruction(
            code[op], "eax", "ebx", "", "effectue l'opération eax" + op +
            "ebx et met le résultat dans eax")
        res_type = Type.BOOLEEN
    elif op in ["<", "<=", ">", ">=", "==", "!="]:
        gen_comparison(operation, type_lhs, type_rhs)
        res_type = Type.BOOLEEN
    else:
        raise Exception("type d'opération inconnu", op)

    target = "edx" if op == "%" else "eax"

    nasm_instruction("push", target, "", "", "empile le résultat")
    return res_type


def gen_operation_unaire(operation: arbre_abstrait.OperationUnaire,
                         symbol_table: SymbolTable) -> Type:
    op = operation.op

    ty_expr = gen_expression(
        operation.exp, symbol_table)  # on calcule et empile la valeur de exp
    nasm_instruction("pop", "eax", "", "",
                     "dépile la première operande dans eax")

    if op == '-':
        check_type(Type.ENTIER, ty_expr)
        nasm_instruction("neg", "eax", "", "", "effectue l'opération -eax")
        res_type = Type.ENTIER
    elif op == "non":
        check_type(Type.BOOLEEN, ty_expr)
        nasm_instruction("xor", "eax", "1", "", "effectue l'opération not eax")
        res_type = Type.BOOLEEN
    else:
        raise Exception("type d'opération unaire inconnu")

    nasm_instruction("push", "eax", "", "", "empile le résultat")
    return res_type


def gen_comparison(expr: arbre_abstrait.Operation, lhs_type: Type,
                   rhs_type: Type):
    """
    Génère le code pour une comparaison
    """

    check_type(Type.ENTIER, lhs_type, rhs_type)

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
        raise Exception("type de comparaison inconnu")
