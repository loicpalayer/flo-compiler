import syrupy
from src.analyse_syntaxique import analyse_syntaxique
import json


def get_out(input) -> str:
    out = analyse_syntaxique(input)
    return json.dumps(out, indent=2)


def test_syntaxe(snapshot):
    input = """
    ecrire(- (a + b - c) * d / e % f);
    fonction1(a et non(b ou c));
    bonsoir(a == b != c < d <= e > f >= g);
    """

    assert get_out(input) == snapshot


def test_parse_while(snapshot):
    input = """
   tantque (a) {
       ecrire(a);
   }
   """

    assert get_out(input) == snapshot


def test_parse_if(snapshot):
    input = """
    si (a) {
        ecrire(a);
    }
    sinonsi (b) {
        ecrire(b);
    }
    sinonsi (c) {
        ecrire(c);
        ecrire(d);
    }
    sinon {
        ecrire(c);
    }
    """

    assert get_out(input) == snapshot


def test_invalid_parse_if():
    INVALID = [
        """
    si (a) {
        ecrire(a);
    }
    sinon {
        ecrire(d);
    }
    sinonsi (b) {
        ecrire(b);
    }
    """,
        """
    sinon {
        ecrire(a);
    }
    """,
    ]

    for input in INVALID:
        try:
            get_out(input)
            assert False
        except Exception:
            pass


def test_declare_assign(snapshot):
    input = """
    entier a;
    a = 1;
    booleen b = vrai;
    """

    assert get_out(input) == snapshot


def test_return(snapshot):
    input = """
    retourner 1;
    """

    assert get_out(input) == snapshot


def test_function_call(snapshot):
    input = """
    fonction1(a, b, c);
    """

    assert get_out(input) == snapshot


def test_function_declare(snapshot):
    input = """
    entier fonction1(entier a, booleen b, booleen c) {
        ecrire(a + b % c);
        retourner a;
    }

    booleen fonction2 () {
        retourner 1;
    }

    fonction1(a, b, c);
    fonction2();
    """

    assert get_out(input) == snapshot
