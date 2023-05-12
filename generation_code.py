import sys
from analyse_lexicale import FloLexer
from analyse_syntaxique import FloParser
import arbre_abstrait

num_etiquette_courante = -1  #Permet de donner des noms différents à toutes les étiquettes (en les appelant e0, e1,e2,...)

afficher_table = False
afficher_nasm = False


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


def gen_programme(programme: arbre_abstrait.Programme):
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
    printifm('_start:')
    gen_listeInstructions(programme.listeInstructions)
    nasm_instruction("mov", "eax", "1", "", "1 est le code de SYS_EXIT")
    nasm_instruction("int", "0x80", "", "", "exit")


def gen_listeInstructions(listeInstructions: arbre_abstrait.ListeInstructions):
    """
    Affiche le code nasm correspondant à une suite d'instructions
    """
    for instruction in listeInstructions.instructions:
        gen_instruction(instruction)


def gen_instruction(instruction: arbre_abstrait.AST):
    """
    Affiche le code nasm correspondant à une instruction
    """
    if type(instruction) == arbre_abstrait.AppelFonction:
        gen_appel_fonction(instruction)
    else:
        print("type instruction inconnu", type(instruction))
        exit(0)


def gen_ecrire(arg: arbre_abstrait.AST):
    """
    Affiche le code nasm correspondant au fait d'envoyer la valeur entière d'une expression sur la sortie standard
    """
    gen_expression(arg)  # on calcule et empile la valeur d'expression
    nasm_instruction("pop", "eax", "", "",
                     "")  # on dépile la valeur d'expression sur eax
    nasm_instruction("call", "iprintLF", "", "",
                     "")  # on envoie la valeur d'eax sur la sortie standard


def gen_appel_fonction(fonction: arbre_abstrait.AppelFonction):
    """
    Affiche le code nasm correspondant à l'appel d'une fonction
    """
    if fonction.name == "ecrire":
        gen_ecrire(fonction.args[0])
    else:
        print("type fonction inconnu", fonction.name)
        exit(0)


def gen_expression(expression: arbre_abstrait.AST):
    """
    Affiche le code nasm pour calculer et empiler la valeur d'une expression
    """
    if type(expression) == arbre_abstrait.Operation:
        gen_operation(
            expression)  #on calcule et empile la valeur de l'opération
    elif type(expression) == arbre_abstrait.Entier:
        nasm_instruction("push", str(expression.valeur), "", "", "")
        #on met sur la pile la valeur entière
    else:
        print("type d'expression inconnu", type(expression))
        exit(0)


def gen_operation(operation: arbre_abstrait.Operation):
    """
    Affiche le code nasm pour calculer l'opération et la mettre en haut de la pile
    """
    op = operation.op

    gen_expression(operation.lhs)  # on calcule et empile la valeur de exp1
    gen_expression(operation.rhs)  # on calcule et empile la valeur de exp2

    nasm_instruction("pop", "ebx", "", "",
                     "dépile la seconde operande dans ebx")
    nasm_instruction("pop", "eax", "", "",
                     "dépile la permière operande dans eax")

    code = {"+": "add", "*": "imul", "-": "sub", "/": "div", "%": "mod"}
    target = {"+": "eax", "*": "eax", "-": "eax", "/": "eax", "%": "edx"}
    # Un dictionnaire qui associe à chaque opérateur sa fonction nasm
    # Voir: https://www.bencode.net/blob/nasmcheatsheet.pdf
    if op in ['+', '-']:
        nasm_instruction(
            code[op], "eax", "ebx", "", "effectue l'opération eax" + op +
            "ebx et met le résultat dans eax")
    if op == '*':
        nasm_instruction(
            code[op], "ebx", "", "", "effectue l'opération eax" + op +
            "ebx et met le résultat dans eax")
    if op == '/':
        nasm_instruction("mov", "edx", "0", "", "met edx à 0")

        nasm_instruction(
            code[op], "ebx", "", "", "effectue l'opération edx:eax" + op +
            "ebx et met le résultat dans eax")
    if op == '%':
        nasm_instruction("mov", "edx", "0", "", "met edx à 0")
        nasm_instruction(
            "idiv", "ebx", "", "", "effectue l'opération eax" + op +
            "ebx et met le résultat dans edx")
    nasm_instruction("push", target[op], "", "", "empile le résultat")


def main():
    global afficher_nasm
    global afficher_tableSymboles

    afficher_nasm = True
    lexer = FloLexer()
    parser = FloParser()
    if len(sys.argv) < 3 or sys.argv[1] not in ["-nasm", "-table"]:
        print(
            "usage: python3 generation_code.py -nasm|-table NOM_FICHIER_SOURCE.flo"
        )
        exit(0)
    if sys.argv[1] == "-nasm":
        afficher_nasm = True
    else:
        afficher_tableSymboles = True
    with open(sys.argv[2], "r") as f:
        data = f.read()
        try:
            arbre = parser.parse(lexer.tokenize(data))
            gen_programme(arbre)
        except EOFError:
            exit()


if __name__ == "__main__":
    main()
