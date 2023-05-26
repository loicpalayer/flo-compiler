import sys
from sly import Parser
from src.analyse_lexicale import FloLexer
import src.arbre_abstrait as arbre_abstrait


class FloParser(Parser):
    # On récupère la liste des lexèmes de l'analyse lexicale
    tokens = FloLexer.tokens

    precedence = (
        ('left', 'ET'),
        ('left', 'OU'),
        ('right', 'NON'),
        ('right', 'EGAL'),
        ('left', 'DIFFERENT', 'INFERIEUR_OU_EGAL', 'SUPERIEUR_OU_EGAL',
         'INFERIEUR', 'SUPERIEUR'),
        ('left', '+', '-'),
        ('left', '*', '/', '%'),
        ('nonassoc', 'UMOINS'),
    )

    # Règles gramaticales et actions associées

    @_('listeInstructions')
    def prog(self, p):
        return arbre_abstrait.Programme(p[0])

    @_('instruction')
    def listeInstructions(self, p):
        l = arbre_abstrait.ListeInstructions()
        l.instructions.append(p[0])
        return l

    @_('instruction listeInstructions')
    def listeInstructions(self, p):
        p[1].instructions.append(p[0])
        return p[1]

    @_('ECRIRE "(" expr ")" ";"')
    def instruction(self, p):
        return arbre_abstrait.Ecrire(p.expr)

    @_('bool')
    def expr(self, p):
        return p[0]

    @_('BOOLEEN')
    def bool(self, p):
        return arbre_abstrait.Booleen(p[0])

    @_('bool ET bool')
    def bool(self, p):
        return arbre_abstrait.Operation('et', p[0], p[2])

    @_('bool OU bool')
    def bool(self, p):
        return arbre_abstrait.Operation('ou', p[0], p[2])

    @_('NON bool')
    def bool(self, p):
        return arbre_abstrait.OperationUnaire('non', p[1])

    @_('exprArith')
    def bool(self, p):
        return p[0]

    @_('exprArith "+" exprArith', 'exprArith "-" exprArith',
       'exprArith "*" exprArith', 'exprArith "/" exprArith',
       'exprArith "%" exprArith', 'exprArith INFERIEUR exprArith',
       'exprArith SUPERIEUR exprArith', 'exprArith EGAL exprArith',
       'exprArith DIFFERENT exprArith',
       'exprArith INFERIEUR_OU_EGAL exprArith',
       'exprArith SUPERIEUR_OU_EGAL exprArith')
    def exprArith(self, p):
        return arbre_abstrait.Operation(p[1], p[0], p[2])

    @_('"-" exprArith %prec UMOINS')
    def exprArith(self, p):
        return arbre_abstrait.OperationUnaire('-', p[1])

    @_('"(" bool ")"')
    def exprArith(self, p):
        return p[1]

    @_('facteur')
    def exprArith(self, p):
        return p[0]

#    @_('IDENTIFIANT "(" function_arg ")"')
#    def facteur(self, p):
#        return arbre_abstrait.AppelFonction(p.IDENTIFIANT, p.function_arg)

    @_('ENTIER')
    def facteur(self, p):
        return arbre_abstrait.Entier(p.ENTIER)

    @_('IDENTIFIANT')
    def facteur(self, p):
        return arbre_abstrait.Identifiant(p.IDENTIFIANT)


#    @_('expr "," function_arg ')
#    def function_arg(self, p):
#        p.function_arg.append(p.expr)
#        return p.function_arg

#    @_('expr')
#    def function_arg(self, p):
#        return [p.expr]


def analyse_syntaxique(input):
    lexer = FloLexer()
    parser = FloParser()
    return parser.parse(lexer.tokenize(input)).to_json()
