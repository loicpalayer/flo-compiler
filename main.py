from src.analyse_syntaxique import analyse_syntaxique
import sys

from src.generation_code import gen_entrypoint


def main(args):
    if len(args) < 2:
        print(
            "usage: python3 analyse_syntaxique.py NOM_FICHIER_SOURCE.flo [--ast]]"
        )
    else:
        with open(args[1], "r") as f:
            data = f.read()
            try:
                arbre = analyse_syntaxique(data)
                if len(args) > 2 and args[2] == "--ast":
                    print(arbre)
                else:
                    gen_entrypoint(arbre)
            except EOFError:
                exit()


if __name__ == '__main__':
    main(sys.argv)