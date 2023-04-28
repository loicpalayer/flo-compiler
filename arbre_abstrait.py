"""
Affiche une chaine de caractère avec une certaine identation
"""


def afficher(s, indent=0):
    print(" " * indent + s)


class Programme:

    def __init__(self, listeInstructions):
        self.listeInstructions = listeInstructions

    def __str__(self):
        return f"""<programme>
    {self.listeInstructions}
</programme>"""


class ListeInstructions:

    def __init__(self):
        self.instructions = []

    def __str__(self):
        instructions = '\n'.join([str(i) for i in self.instructions])
        return f"""<listeInstructions>
    {instructions}
</listeInstructions>"""


class Operation:

    def __init__(self, op, exp1, exp2):
        self.exp1 = exp1
        self.op = op
        self.exp2 = exp2

    def __str__(self):
        return f"""<operation>
    {self.exp1}
    {self.op}
    {self.exp2}
</operation>"""


class Entier:

    def __init__(self, valeur):
        self.valeur = valeur

    def __str__(self):
        return f"<entier>{self.valeur}</entier>"


class Booleen:

    def __init__(self, valeur):
        self.valeur = valeur

    def __str__(self):
        return f"<booleen>{self.valeur}</booleen>"


class Identifiant:

    def __init__(self, valeur):
        self.valeur = valeur

    def __str__(self):
        return f"<identifiant>{self.valeur}</identifiant"


class AppelFonction:

    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __str__(self):
        return f"""<appelFonction>
    {self.name}
    {self.args}
</appelFonction>"""
