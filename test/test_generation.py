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


def test_if(snapshot, capsys):
    input = """
    entier f(entier e) {
        si (e > 5) {
            ecrire(e);
        }
        sinon {
            ecrire(5);
            ecrire(6);
        }
        retourner 1;
    }
    f(5);
    """
    assert get_out(input, capsys) == snapshot


def test_var_local1(snapshot, capsys):
    input = """
    entier f(entier e) {
        entier a = lire();
        retourner a + e;
    }
    f(5);
    """
    assert get_out(input, capsys) == snapshot


def test_var_local2(snapshot, capsys):
    input = """
    entier f(entier e) {
        si (e == 0) {
            entier a = 5;
        }
        si (e == 0) {
            entier a = 5;
        }
        si (e == 0) {
            entier a = 5;
        }
    }
    f(5);
    """
    assert get_out(input, capsys) == snapshot


def test_var_local3(snapshot, capsys):
    input = """
    entier f(entier e) {
        entier a = lire();
        si (a > 2) {
            entier b = a * a;
            si (b > 3 * a) {
                entier c = 25;
            }
            sinon {
                entier d = 26;
            }
        }
    }
    f(5);
    """
    assert get_out(input, capsys) == snapshot


def test_var_local_invalid1(snapshot, capsys):
    input = """
    entier f(booleen b) {
        si (b) {
            entier a = lire();
            ecrire(a);
        }
        ecrire(a + 5);
        retourner 1;
    }
    f(Vrai);
    """

    try:
        get_out(input, capsys)
        assert False
    except Exception as e:
        assert e == snapshot


def test_var_local_invalid2(snapshot, capsys):
    input = """
    entier f() {
        entier a;
    }
    entier g() {
        a = 5;
    }
    f();
    """

    try:
        get_out(input, capsys)
        assert False
    except Exception as e:
        assert e == snapshot


def test_var_local_invalid3(snapshot, capsys):
    input = """
    entier f(booleen b) {
        tantque (b) {
            entier rep = lire();
            si (rep > 10) {
                b = Faux;
            }
        }
        retourner rep;
    }
    f(Vrai);
    """

    try:
        get_out(input, capsys)
        assert False
    except Exception as e:
        assert e == snapshot


def test_var_global(snapshot, capsys):
    input = """
    entier f() {
        retourner 123;
    }
    entier a = f();
    """
    assert get_out(input, capsys) == snapshot
