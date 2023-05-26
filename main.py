from src.analyse_syntaxique import analyse_syntaxique
import sys


def main():
    if len(sys.argv) < 2:
        print("usage: python3 analyse_syntaxique.py NOM_FICHIER_SOURCE.flo")
    else:
        with open(sys.argv[1], "r") as f:
            data = f.read()
            try:
                arbre = analyse_syntaxique(data)
                print(arbre)
            except EOFError:
                exit()


if __name__ == '__main__':
    main()