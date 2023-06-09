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


def test_invalid_call(snapshot, capsys):
    input = """
    entier f() {
        retourner 3;
    }
    ecrire(f(3));
    """

    try:
        get_out(input, capsys)
        assert False
    except Exception as e:
        assert e == snapshot


def test_invalid1(snapshot, capsys):
    input = """
    retourner 3;
    """

    try:
        get_out(input, capsys)
        assert False
    except Exception as e:
        assert e == snapshot


def test_invalid2(snapshot, capsys):
    input = """
        booleen f() {
        retourner 3;
    }
    """

    try:
        get_out(input, capsys)
        assert False
    except Exception as e:
        assert e == snapshot


def test_invalid3(snapshot, capsys):
    input = """
    entier f() {
        retourner Vrai;
    }
    """

    try:
        get_out(input, capsys)
        assert False
    except Exception as e:
        assert e == snapshot


def test_function_with_param(snapshot, capsys):
    input = """
    entier f(entier e) {
        ecrire(e);
        retourner 1;
    }
    """
    assert get_out(input, capsys) == snapshot


def test_affectation(snapshot, capsys):
    input = """
    entier f(entier e) {
        e = 7;
        ecrire(e);
        retourner 5;
    }
    f(5);
    """
    assert get_out(input, capsys) == snapshot