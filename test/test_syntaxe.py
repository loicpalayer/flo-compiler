import syrupy
from src.analyse_syntaxique import analyse_syntaxique
import json


def test_syntaxe(snapshot):
    input = """
    ecrire(- (a + b - c) * d / e % f);
    fonction1(a et non(b ou c));
    bonsoir(a == b != c < d <= e > f >= g);
    """

    out = analyse_syntaxique(input)
    actual = json.dumps(out, indent=2)

    assert snapshot == actual
