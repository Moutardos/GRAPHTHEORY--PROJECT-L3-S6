#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Implémentation d'un graphe non orienté à l'aide d'un dictionnaire: les clés
sont les sommets, et les valeurs sont les sommets adjacents à un sommet donné.
Les boucles sont autorisées. Les poids ne sont pas autorisés.

On utilise la représentation la plus simple: une arête {u, v} sera présente
deux fois dans le dictionnaire: v est dans l'ensemble des voisins de u, et u
est dans l'ensemble des voisins de v.
"""


class Graphe(object):
    def __init__(self):
        """Initialise un graphe sans arcs"""
        self.dictionnaire = dict()
        self.coord = dict()

    def ajouter_arc(self, u, v, capacite=1):
        """Ajoute une arc entre les sommmets u et v, en créant les sommets
        manquants le cas échéant."""
        # vérification de l'existence de u et v, et on remplace sinon
        if self.contient_arc(u,v):
            for arc in self.dictionnaire[u]:
                if arc[0] == v :
                    self.dictionnaire[u].remove(arc)
                    break;

        # Création si inexistant
        if u not in self.dictionnaire:
            self.ajouter_sommet(u)
        if v not in self.dictionnaire:
            self.ajouter_sommet(v)

        # ajout de u (resp. v) parmi les voisins de v (resp. u)
        self.dictionnaire[u].add((v, capacite))

    def ajouter_arcs(self, iterable):
        """Ajoute touts les arcs de l'itérable donné au graphe. N'importe
        quel type d'itérable est acceptable, mais il faut qu'il ne contienne
        que des couples d'éléments (quel que soit le type du couple)."""
        for u, v, capacite in iterable:
            self.ajouter_arc(u, v, capacite)

    def ajouter_sommet(self, sommet, coords=(0,0)):
        """Ajoute un sommet (de n'importe quel type hashable) au graphe."""
        self.dictionnaire[sommet] = set()
        self.coord[sommet] = coords

    def ajouter_sommets(self, iterable):
        """Ajoute tous les sommets de l'itérable donné au graphe. N'importe
        quel type d'itérable est acceptable, mais il faut qu'il ne contienne
        que des éléments hashables."""
        for (v, c) in iterable:
            self.ajouter_sommet(v, c)

    def arcs(self):
        """Renvoie l'ensemble des arcs du graphe. Un arc est représenté
        par un tuple (a, b, capacité).
        """
        return {
            tuple((u, v, c)) for u in self.dictionnaire
            for (v,c) in self.dictionnaire[u]
        }

    def boucles(self):
        """Renvoie les boucles du graphe, c'est-à-dire les arcs reliant un
        sommet à lui-même."""
        return {(u, u) for u in self.dictionnaire if u in {v for (v,c) in self.dictionnaire[u]}}

    def contient_arc(self, u, v):
        """Renvoie True si l'arc {u, v} existe, False sinon."""
        if self.contient_sommet(u) and self.contient_sommet(v):
            return v in {v for (v, c) in self.dictionnaire[u]}
        return False

    def contient_sommet(self, u):
        """Renvoie True si le sommet u existe, False sinon."""
        return u in self.dictionnaire

    def degre(self, sommet):
        """Renvoie le nombre de voisins du sommet; s'il n'existe pas, provoque
        une erreur."""
        return len(self.dictionnaire[sommet])

    def nombre_arc(self):
        """Renvoie le nombre d'arcs du graphe."""
        return len(self.arc())

    def nombre_boucles(self):
        """Renvoie le nombre d'arcs de la forme {u, u}."""
        return len(self.boucles())

    def nombre_sommets(self):
        """Renvoie le nombre de sommets du graphe."""
        return len(self.dictionnaire)

    def retirer_arc(self, u, v):
        """Retire l'arc {u, v} si il existe; provoque une erreur sinon."""

        for (j,c) in self.dictionnaire[u]:
            if v == j:
                self.dictionnaire[u].remove((v,c))
                break;

    def retirer_arcs(self, iterable):
        """Retire touts les arcs de l'itérable donné du graphe. N'importe
        quel type d'itérable est acceptable, mais il faut qu'il ne contienne
        que des couples d'éléments (quel que soit le type du couple)."""
        for u, v in iterable:
            self.retirer_arc(u, v)

    def retirer_sommet(self, sommet):
        """Efface le sommet du graphe, et retire tous les arcs qui lui
        sont incidents."""
        del self.dictionnaire[sommet]
        # retirer le sommet des ensembles
        for (u,v, c) in self.arcs():
            if v == sommet:
                self.retirer_arc(u,v)

    def retirer_sommets(self, iterable):
        """Efface les sommets de l'itérable donné du graphe, et retire tous
        les arcs incidents à ces sommets."""
        for sommet in iterable:
            self.retirer_sommet(sommet)

    def sommets(self):
        """Renvoie l'ensemble des sommets du graphe."""
        return set((u, self.coord[u]) for u in self.dictionnaire)

    def sous_graphe_induit(self, iterable):
        """Renvoie le sous-graphe induit par l'itérable de sommets donnés."""
        G = Graphe()
        G.ajouter_sommets(iterable)
        for (u,v, c) in self.arcs():
            if G.contient_sommet(u) and G.contient_sommet(v):
                G.ajouter_arc(u, v, c)
        return G

    def voisins(self, sommet):
        """Renvoie l'ensemble des voisins du sommet donné."""
        return self.dictionnaire[sommet]

    def sources(self):
        """Renvoie l'ensemble de sources dans le graphe"""
        return {u for u in self.dictionnaire if self.dictionnaire[u] != set() and all((not self.contient_arc(v,u) for v in self.dictionnaire ))}

    def puits(self):
        """Renvoie l'ensemble de puits dans le graphe"""
        return {u for u in self.dictionnaire if self.dictionnaire[u] == set()}

    def poids_arc(self, u, v):
        """Renvoie le de poid de l'arete u,v si elle existe, NULL sinon"""
        if self.contient_arc(u, v):
            for (j, c) in self.dictionnaire[u] :
                if  j == v:
                    return c
        else:
            return None

    def copy(self):
        Gcopy = type(self)()
        Gcopy.ajouter_sommets(self.sommets())
        Gcopy.ajouter_arcs(self.arcs())
        return Gcopy