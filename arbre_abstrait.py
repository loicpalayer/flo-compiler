"""
Affiche une chaine de caractère avec une certaine identation
"""
def afficher(s,indent=0):
	print(" "*indent+s)
	
class Programme:
	def __init__(self,listeInstructions):
		self.listeInstructions = listeInstructions
	def afficher(self,indent=0):
		afficher("<programme>",indent)
		self.listeInstructions.afficher(indent+1)
		afficher("</programme>",indent)

class ListeInstructions:
	def __init__(self):
		self.instructions = []
	def afficher(self,indent=0):
		afficher("<listeInstructions>",indent)
		for instruction in self.instructions:
			instruction.afficher(indent+1)
		afficher("</listeInstructions>",indent)
			
class Ecrire:
	def __init__(self,exp):
		self.exp = exp
	def afficher(self,indent=0):
		afficher("<ecrire>",indent)
		self.exp.afficher(indent+1)
		afficher("</ecrire>",indent)
		
class Operation:
	def __init__(self,op,exp1,exp2):
		self.exp1 = exp1
		self.op = op
		self.exp2 = exp2
	def afficher(self,indent=0):
		afficher("<operation>",indent)
		afficher(self.op,indent+1)
		self.exp1.afficher(indent+1)
		self.exp2.afficher(indent+1)
		afficher("</operation>",indent)
class Entier:
	def __init__(self,valeur):
		self.valeur = valeur
	def afficher(self,indent=0):
		afficher("[Entier:"+str(self.valeur)+"]",indent)
