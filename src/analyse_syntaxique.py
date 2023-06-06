# type: ignore

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
    @_('instruction')
    def prog(self, p):
        return arbre_abstrait.Programme([p.instruction])

    @_('prog instruction')
    def prog(self, p):
        p.prog.addInstruction(p.instruction)
        return p.prog

    @_('expr ";"')
    def instruction(self, p):
        return p.expr

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

    @_('identifiant "(" function_arg ")"')
    def facteur(self, p):
        return arbre_abstrait.AppelFonction(p.identifiant, p.function_arg)

    @_('identifiant "("  ")"')
    def facteur(self, p):
        return arbre_abstrait.AppelFonction(p.identifiant,
                                            arbre_abstrait.FunctionArgs([]))

    @_('ENTIER')
    def facteur(self, p):
        return arbre_abstrait.Entier(p.ENTIER)

    @_('IDENTIFIANT')
    def facteur(self, p):
        return arbre_abstrait.Identifiant(p.IDENTIFIANT)

    @_('IDENTIFIANT')
    def identifiant(self, p):
        return arbre_abstrait.Identifiant(p.IDENTIFIANT)

    @_('SI "(" expr ")" "{" prog "}"')
    def si(self, p):
        return arbre_abstrait.If(p.expr, p.prog, None)

    @_('si SINONSI "(" expr ")" "{" prog "}"')
    def si(self, p):
        p.si.add_elif(p.expr, p.prog)
        return p.si

    @_('si SINON "{" prog "}"')
    def cond(self, p):
        p.si.add_else(p.prog)
        return p.si

    @_('TANTQUE "(" expr ")" "{" prog "}"')
    def instruction(self, p):
        return arbre_abstrait.While(p.expr, p.prog)

    @_('cond')
    def instruction(self, p):
        return p.cond

    @_('TYPE identifiant')
    def decl(self, p):
        return arbre_abstrait.Declaration(p.identifiant,
                                          arbre_abstrait.Type.from_str(p.TYPE),
                                          None)

    @_('decl ";"')
    def instruction(self, p):
        return p.decl

    @_('TYPE identifiant "=" expr ";"')
    def instruction(self, p):
        return arbre_abstrait.Declaration(p.identifiant,
                                          arbre_abstrait.Type.from_str(p.TYPE),
                                          p.expr)

    @_('identifiant "=" expr ";"')
    def instruction(self, p):
        return arbre_abstrait.Assignment(p.identifiant, p.expr)

    @_('RETOURNER expr ";"')
    def instruction(self, p):
        return arbre_abstrait.Return(p.expr)

    @_('function_arg "," expr')
    def function_arg(self, p):
        p.function_arg.append(p.expr)
        return p.function_arg

    @_('expr')
    def function_arg(self, p):
        return arbre_abstrait.FunctionArgs([p.expr])

    @_('decl')
    def function_decl_arg(self, p):
        return [p.decl]

    @_('function_decl_arg "," decl')
    def function_decl_arg(self, p):
        p.function_decl_arg.append(p.decl)
        return p.function_decl_arg

    @_('TYPE identifiant "(" function_decl_arg ")" "{" prog "}"')
    def function(self, p):
        return arbre_abstrait.Function(p.identifiant, p.function_decl_arg,
                                       p.prog,
                                       arbre_abstrait.Type.from_str(p.TYPE))

    @_('TYPE identifiant "(" ")" "{" prog "}"')
    def function(self, p):
        return arbre_abstrait.Function(p.identifiant, [], p.prog,
                                       arbre_abstrait.Type.from_str(p.TYPE))

    @_('function')
    def instruction(self, p):
        return p.function


def analyse_syntaxique(input: str) -> arbre_abstrait.Programme:
    lexer = FloLexer()
    parser = FloParser()
    return parser.parse(lexer.tokenize(input))
