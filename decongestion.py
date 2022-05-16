from graphe import *
from random import *
class File(object):
	def __init__(self):
		self.file = []

	def enfiler(self, n):
		self.file.append(n)

	def defiler(self):
		return self.file.pop(0)

	def enfilers(self, it):
		for el in it:
			self.enfiler(el)

	def est_vide(self):
		return self.file == []


def unique_source_puits(G, sources=set(), puits=set()):
	'''Modifie G pour que utilise une source unique artificiel
	   Voisines de sources et puits si indiqué en parametre
	   ATTENTION: renvoie None si G n'a pas de source ou de puits'''
	if len(sources) == 1 :
		new_source = next(iter(sources))
	elif len(sources) > 1:
		for v in sources :
			G.ajouter_arc('0', v, 99999999) #capacité semi-infini
			new_source = '0'
	else:
		new_source = None
	if len(puits) == 1 :
		new_puits= next(iter(puits))
	elif len(puits) > 1:
		for v in puits :
			G.ajouter_arc(v, 'X', 99999999)
			new_puits = 'X'
	else:
		new_puits = None
	return new_source, new_puits

def reconstruire_G(G):
	for (u, v, c) in G.arcs():
		if c == 99999999 :
			G.retirer_arc(u,v)
	if G.contient_sommet('0'):
		G.retirer_sommet('0')
	if G.contient_sommet('X'):
		G.retirer_sommet('X')


def augmenter_flot(flot, P):
	capacite_min = min({c for (u,v,c) in P.arcs()})
	for (u,v, _) in P.arcs():
		if (u, v) in flot :
			flot[(u,v)] =  flot[(u,v)] + capacite_min 
		else:
			flot[(v,u)] = flot[(v,u)] - capacite_min

def reconstruire_chemin(G, debut, fin, parents):
	chemin = Graphe()
	v = fin
	while v != debut :
		if parents[v] == None:
			return None
		chemin.ajouter_arc(parents[v], v, G.poids_arc(parents[v], v))
		v = parents[v]
	return chemin

def chemin_augmentant(G, source, puits) :
	deja_visite = {u: False for (u, _) in G.sommets()}
	a_traiter = File()
	a_traiter.enfiler(source)
	parents = {u: None for (u, _) in G.sommets()}
	while not a_traiter.est_vide() :
		sommet = a_traiter.defiler()
		if sommet == puits :
			break
		if not deja_visite[sommet]:
			deja_visite[sommet] = True 
			for (suivant, c) in G.voisins(sommet):
				a_traiter.enfiler(suivant)
				if parents[suivant] == None:
					parents[suivant] = sommet
	return reconstruire_chemin(G, source, puits, parents)
'''
def flot_bloquant(G, Gl, flot, source, puits):
	arcs = set()
	chemin = chemin_augmentant(Gl, source, puits)
	while (chemin != None):
		augmenter_flot(flot, chemin)
		MAJ_DAGLargeur(G, Gl, chemin.arcs(), flot)
		
		arcs.update(chemin.arcs())
		
		chemin = chemin_augmentant(Gl, source, puits)
	return arcs
'''



def MAJ_residuel(G, Gf, arcs, flot):
	cheminf = dict()
	for (u, v, _) in arcs:
		if G.contient_arc(v, u):
			u, v = v, u
		cheminf[(u, v)] = G.poids_arc(u,v) - flot[(u,v)]
		cheminf[(v, u)] = flot[(u,v)]
	
	for (u, v, _) in arcs:
		if cheminf[(u,v)] > 0:
			Gf.ajouter_arc(u,v,cheminf[(u,v)])
		else:
			if (Gf.contient_arc(u,v)):
				Gf.retirer_arc(u,v)
		if cheminf[(v,u)] > 0:
			Gf.ajouter_arc(v,u,cheminf[(v,u)])
		else:
			if (Gf.contient_arc(v,u)):
				Gf.retirer_arc(v,u)

def flot_maximum(G):
	fake_source, fake_puits = unique_source_puits(G, sources=G.sources(), puits=G.puits())
	flot = {(u,v) : 0 for (u, v, _) in G.arcs()}
	Gf = G.copy()
	chemin = chemin_augmentant(G, fake_source, fake_puits)
	while (chemin != None):
		
		augmenter_flot(flot, chemin)
		MAJ_residuel(G, Gf, chemin.arcs(), flot)
		
		chemin = chemin_augmentant(Gf, fake_source, fake_puits)
	reconstruire_G(G)
	
	for p in G.puits():
		if p != fake_puits:
			del flot[(p,fake_puits)]
	for s in G.sources():
		if s != fake_source:
			del flot[(fake_source, s)]

	
	return (sum((flot[(u,v)] for (u,v) in flot.keys() if v in G.puits())),flot)


def reseau_residuel(reseau, flot):
	
	reseauf = type(reseau)()
	arcs = reseau.arcs()
	arcs.update({(v,u, c) for (u,v,c) in arcs})
	MAJ_residuel(reseau, reseauf, arcs, flot)
	return reseauf

def parcours_largeur_coupe(G, source):
	sommets = set(source)
	file = File()
	file.enfiler(source)
	old_current_level = set(source)
	while not file.est_vide() :
		actuel = file.defiler()
		
		if actuel in sommets : # On a atteint le nouveau niveau, les sommets dans la liste deviennent donc actuel
			old_current_level.update(sommets)
		for (v, _) in G.voisins(actuel):
			if v not in old_current_level: # Le voisin n'a pas deja été traité
				sommets.add(v)
				file.enfiler(v)
		for (u,v,_) in G.arcs():
			if v == actuel:
				old_current_level.add(u) #Evite les boucles...
	return sommets

def coupe_minimum(residuel, source):
	fake_source, _ = unique_source_puits(residuel, sources=source)
	S = parcours_largeur_coupe(residuel, fake_source)
	T = set(filter(lambda s: (s not in S), {u for (u,_) in residuel.sommets()}))
	reconstruire_G(residuel)
	return (S,T)

def augmentations_uniques_utiles(graphe, flot_max):
	to_augmente  = set()
	residuel = reseau_residuel(graphe, flot_max)
	S, T = coupe_minimum(residuel, graphe.sources()) #On envoie les voisins entre la coupe
	
	for s in S :
		for t in T :
			if graphe.contient_arc(s,t):
				to_augmente.add((s,t))
	return to_augmente

def augmentations_uniques_utiles_calibrees(graphe, flot_max):
	''' On parcoure un chemin de la source du graphe jusqu'a la source de l'arc qui va etre amélioré, on aditionne 
		toute les capacité disponible, on fait de meme ensuite pour le chemin de la destination de l'arc vers le puits.
		On peut ensuite précalculer de combien le flot_maximum va monter après l'augmentation de la cible'''
	f_old, _ = flot_maximum(graphe)
	
	new_graphe = graphe.copy() # Pour eviter de modifier le graphe d'origine
	
	fake_source, fake_puits = unique_source_puits(new_graphe, sources=graphe.sources(), puits=graphe.puits())
	to_augmente  = augmentations_uniques_utiles(graphe, flot_max)
	result = {}
	for (S,T) in to_augmente :		
		flot = flot_max.copy()
		Gf = graphe.copy()
		residuel = reseau_residuel(new_graphe, flot)
		
		calibre = 0
		chemin_from_source = chemin_augmentant(new_graphe,fake_source, S)
		chemin_to_puits = chemin_augmentant(new_graphe,T, fake_puits)

		while (chemin_from_source != None and chemin_from_source.arcs() != set()):
			for (u,v,c) in chemin_from_source.arcs():
				if residuel.contient_arc(u,v):
					
					calibre += residuel.poids_arc(u,v)

			augmenter_flot(flot, chemin_from_source)
			MAJ_residuel(new_graphe, Gf, chemin_from_source.arcs(), flot)
			chemin_from_source = chemin_augmentant(Gf, fake_source, S)

		while (chemin_to_puits != None and chemin_to_puits.arcs() != set()):
			for (u,v,c) in chemin_to_puits.arcs():
				if residuel.contient_arc(u,v):
					
					calibre += residuel.poids_arc(u,v)	
			augmenter_flot(flot, chemin_to_puits)
			MAJ_residuel(new_graphe, Gf, chemin_to_puits.arcs(), flot)
			chemin_to_puits = chemin_augmentant(Gf, T, fake_puits)
		
		new_graphe.ajouter_arc(S,T, new_graphe.poids_arc(S,T) + calibre)
		
		f_new, _= flot_maximum(new_graphe)
		
		gain = f_new - f_old
		
		if gain<= 0:
			if (new_graphe.poids_arc(S,T) > flot[(S,T)]):
				result[(S,T)] = new_graphe.poids_arc(S,T) - flot[(S,T)]
			else :
				result[(S,T)] = 1
		else:

			result[(S,T)] = gain
		new_graphe = graphe.copy()
	return result

#Permet de pointer vers le meilleur chemin 
class Path(object) :
	def __init__(self):
		self.cost = 0
		self.step = {}
		self.value = 0
		self.reseau = Graphe()
		self.flot_max = None
		self.decisions = [] #Pour les mutations

	def update_flot(self):
		_, self.flot_max = flot_maximum(self.reseau)

def create_path_random(graphe, goal, path=None):
	if path == None:
		path = Path()
	if graphe != None:
		path.reseau = graphe.copy()
	random = Random()
	random.seed()
	while path.value < goal:
		path.update_flot()
		((u,v),cost) = random.choice(list(augmentations_uniques_utiles_calibrees(path.reseau, path.flot_max).items()))
		path.decisions.append((u,v,cost))
		capacity = path.reseau.poids_arc(u,v) + cost
		path.step[(u,v)] = capacity
		path.reseau.ajouter_arc(u,v, capacity)
		path.cost += cost
		path.value, _ = flot_maximum(path.reseau)
	return path

def mutating_path(graphe, path, goal):
	if len(path.decisions) == 1:
		return create_path_random(None, goal, path)
	muted_path = Path()
	muted_path.reseau = graphe.copy()
	random = Random()
	indice = random.randrange(1, len(path.decisions)) # Choisis a partir de quand la mutation va diverger de l'original
	unchanged = path.decisions[1:indice]
	for (u,v,cost) in unchanged:
		capacity = path.reseau.poids_arc(u,v) + cost
		muted_path.reseau.ajouter_arc(u,v, capacity)
		muted_path.cost += cost
		muted_path.value, _ = flot_maximum(path.reseau)
	return create_path_random(None, goal, path=path)

def ensemble_minimum_augmentations_utiles_calibrees(graphe, flot_max,value):
	flot_value, _ = flot_maximum(graphe)
	goal = flot_value + value
	paths = []
	alph = 10
	beta = 30
	gamma = 10
	#Programmation genetique de 128 paths en gardant 15 meilleurs, 60 mutations, 40 randoms
	for i in range(50):
		paths.append(create_path_random(graphe, goal))

	for i in range(100):
		paths.sort(key=lambda p: (p.cost,len(p.step)))
		for i in range(50):
			if i < alph :
				continue
			elif i < beta :
				paths[i] = mutating_path(graphe, paths[i % alph], goal)
			elif i < gamma :
				paths[i]  = create_path_random(graphe,goal)

	return paths[0].step




if __name__ == "__main__" :
	None