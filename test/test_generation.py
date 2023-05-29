import syrupy

from src.analyse_syntaxique import analyse_syntaxique
from src.generation_code import gen_entrypoint


def get_out(input: str, capsys):
    out = analyse_syntaxique(input)
    gen_entrypoint(out)
    captured = capsys.readouterr()
    return captured.out


def test_function(snapshot, capsys):
    input = """
    entier f() {
        retourner 3;
    }
    ecrire(f());
    """
    assert get_out(input, capsys) == snapshot