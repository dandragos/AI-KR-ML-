import copy
import sys
import time
from collections import deque

class NodParcurgere:
    def __init__(self, info, parinte, cost=0, h=0):
        self.info = info
        self.parinte = parinte
        self.g = cost
        self.h = h
        self.f = self.g + self.h

    def obtineDrum(self):
        l = [self]
        nod = self
        while nod.parinte is not None:
            l.insert(0, nod.parinte)
            nod = nod.parinte
        return l

    def afisDrum(self, afisCost=False, afisLung=False):
        l = self.obtineDrum()
        for i, nod in enumerate(l):
            print(i + 1, ")\n", str(nod), sep="")
            if i > 0:
                mutare = self.obtineMutare(l[i - 1], nod)
                print(mutare)
        if afisCost:
            print("Cost: ", self.g)
        if afisLung:
            print("Lungime: ", len(l))
        return len(l)

    def obtineMutare(self, nodAnterior, nodCurent):
        directii = ["sus", "jos", "stanga", "dreapta"]
        for i in range(len(nodAnterior.info)):
            for j in range(len(nodAnterior.info[0])):
                if nodAnterior.info[i][j] != nodCurent.info[i][j]:
                    placuta = nodAnterior.info[i][j]
                    lAnterior, cAnterior = i, j
                    lCurent, cCurent = self.gasestePozitie(placuta, nodCurent)
                    directie = self.gasesteDirectie(lAnterior, cAnterior, lCurent, cCurent)
                    return f"Placuta {placuta} s-a mutat {directie}, la coordonatele ({lCurent},{cCurent}), cu costul {placuta}"

    def gasestePozitie(self, placuta, nod):
        for i in range(len(nod.info)):
            for j in range(len(nod.info[0])):
                if nod.info[i][j] == placuta:
                    return i, j

    def gasesteDirectie(self, lAnterior, cAnterior, lCurent, cCurent):
        if lAnterior < lCurent:
            return "jos"
        elif lAnterior > lCurent:
            return "sus"
        elif cAnterior < cCurent:
            return "dreapta"
        elif cAnterior > cCurent:
            return "stanga"

    def contineInDrum(self, infoNodNou):
        nodDrum = self
        while nodDrum is not None:
            if infoNodNou == nodDrum.info:
                return True
            nodDrum = nodDrum.parinte
        return False

    def __repr__(self):
        return str(self.info)

    def __str__(self):
        sir = ""
        for linie in self.info:
            sir += " ".join([str(elem) for elem in linie]) + "\n"
        sir += "\n"
        return sir

class Graph:
    def __init__(self, nume_fisier):
        self.start = self.citeste_stare_initiala(nume_fisier)
        if not self.validare():
            print("Eroare: Starea initiala din fisierul dat nu este valida.")
            sys.exit(0)

        self.scop = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]

    def citeste_stare_initiala(self, nume_fisier):
        try:
            with open(nume_fisier, "r") as f:
                stare_initiala = []
                for linie in f:
                    stare_initiala.append([int(x) for x in linie.strip().split()])
                return stare_initiala
        except FileNotFoundError:
            print("Eroare: Fisierul", nume_fisier, "nu a fost gasit.")
            sys.exit(0)

    def validare(self):
        if len(self.start) != 3:
            return False
        for linie in self.start:
            if len(linie) != 3:
                return False
        numere = set(range(9))
        for linie in self.start:
            for numar in linie:
                if numar not in numere:
                    return False
        return not self.nuAreSolutii(self.start)

    def testeaza_scop(self, nodCurent):
        return nodCurent.info == self.scop

    def nuAreSolutii(self, infoNod):
        listaMatrice = sum(infoNod, [])
        nrInversiuni = 0
        for i in range(len(listaMatrice)):
            if listaMatrice[i] != 0:
                for j in range(i + 1, len(listaMatrice)):
                    if listaMatrice[j] != 0:
                        if listaMatrice[i] > listaMatrice[j]:
                            nrInversiuni += 1
        return nrInversiuni % 2 == 1

    def genereazaSuccesori(self, nodCurent, tip_euristica="euristica banala"):
        listaSuccesori = []
        for lGol in range(len(nodCurent.info)):
            try:
                cGol = nodCurent.info[lGol].index(0)
                break
            except:
                pass
        directii = [
            [lGol, cGol - 1],
            [lGol, cGol + 1],
            [lGol - 1, cGol],
            [lGol + 1, cGol],
        ]
        for lPlacuta, cPlacuta in directii:
            if 0 <= lPlacuta < 3 and 0 <= cPlacuta < 3:
                copieMatrice = copy.deepcopy(nodCurent.info)
                copieMatrice[lGol][cGol] = copieMatrice[lPlacuta][cPlacuta]
                copieMatrice[lPlacuta][cPlacuta] = 0
                if not nodCurent.contineInDrum(copieMatrice):
                    costArc = 1
                    listaSuccesori.append(
                        NodParcurgere(
                            copieMatrice,
                            nodCurent,
                            nodCurent.g + costArc,
                            self.estimeaza_h(copieMatrice, tip_euristica),
                        )
                    )
        return listaSuccesori

    def estimeaza_h(self, infoNod, euristica="euristica banala"):
        if infoNod == self.scop:
            return 0

        if euristica == "euristica banala":
            return 1

        elif euristica == "euristica mutari":
            numar_placute_gresite = 0
            for lPlacutaC in range(len(infoNod)):
                for cPlacutaC in range(len(infoNod[0])):
                    if infoNod[lPlacutaC][cPlacutaC] != 0:
                        placuta = infoNod[lPlacutaC][cPlacutaC]
                        lPlacutaF = (placuta - 1) // len(infoNod[0])
                        cPlacutaF = (placuta - 1) % len(infoNod[0])
                        if lPlacutaC != lPlacutaF or cPlacutaC != cPlacutaF:
                            numar_placute_gresite += 1
            return numar_placute_gresite

        elif euristica == "euristica mutari cost":
            cost_total = 0
            for lPlacutaC in range(len(infoNod)):
                for cPlacutaC in range(len(infoNod[0])):
                    if infoNod[lPlacutaC][cPlacutaC] != 0:
                        placuta = infoNod[lPlacutaC][cPlacutaC]
                        lPlacutaF = (placuta - 1) // len(infoNod[0])
                        cPlacutaF = (placuta - 1) % len(infoNod[0])
                        if lPlacutaC != lPlacutaF or cPlacutaC != cPlacutaF:
                            cost_total += placuta
            return cost_total

        elif euristica == "euristica manhattan":
            distanta_totala = 0
            for lPlacutaC in range(len(infoNod)):
                for cPlacutaC in range(len(infoNod[0])):
                    if infoNod[lPlacutaC][cPlacutaC] != 0:
                        placuta = infoNod[lPlacutaC][cPlacutaC]
                        lPlacutaF = (placuta - 1) // len(infoNod[0])
                        cPlacutaF = (placuta - 1) % len(infoNod[0])
                        distanta_totala += abs(lPlacutaF - lPlacutaC) + abs(cPlacutaF - cPlacutaC)
            return distanta_totala

        elif euristica == "euristica manhattan costuri":
            cost_total = 0
            for lPlacutaC in range(len(infoNod)):
                for cPlacutaC in range(len(infoNod[0])):
                    if infoNod[lPlacutaC][cPlacutaC] != 0:
                        placuta = infoNod[lPlacutaC][cPlacutaC]
                        lPlacutaF = (placuta - 1) // len(infoNod[0])
                        cPlacutaF = (placuta - 1) % len(infoNod[0])
                        distanta_manhattan = abs(lPlacutaF - lPlacutaC) + abs(cPlacutaF - cPlacutaC)
                        cost_total += placuta * distanta_manhattan
            return cost_total

        elif euristica == "euristica neadmisibila":
            # Returnăm o valoare mare care face ca estimația să fie neadmisibilă
            return float('inf')

        else:
            raise ValueError("Euristică necunoscută: " + euristica)

    def BFS(self, nodStart):
        noduri_vizitate = set()
        coada = deque([nodStart])

        while coada:
            nodCurent = coada.popleft()
            if self.testeaza_scop(nodCurent):
                return nodCurent
            noduri_vizitate.add(nodCurent)
            lSuccesori = self.genereazaSuccesori(nodCurent)
            for succesor in lSuccesori:
                if succesor not in noduri_vizitate:
                    coada.append(succesor)
                    noduri_vizitate.add(succesor)

    def DFS(self, nodStart):
        noduri_vizitate = set()
        stiva = [nodStart]

        while stiva:
            nodCurent = stiva.pop()
            if self.testeaza_scop(nodCurent):
                return nodCurent
            noduri_vizitate.add(nodCurent)
            lSuccesori = self.genereazaSuccesori(nodCurent)
            for succesor in reversed(lSuccesori):
                if succesor not in noduri_vizitate:
                    stiva.append(succesor)
                    noduri_vizitate.add(succesor)


def a_star(gr, nrSolutiiCautate, tip_euristica):
    if gr.nuAreSolutii(gr.start):
        print("Nu are solutii!")
        return
    c = [NodParcurgere(gr.start, None, 0, gr.estimeaza_h(gr.start))]

    while len(c) > 0:
        nodCurent = c.pop(0)
        if gr.testeaza_scop(nodCurent):
            print("Solutie: ")
            nodCurent.afisDrum(afisCost=True, afisLung=True)

            print("\n----------------\n")
            input()
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return
        lSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica=tip_euristica)
        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(c)):
                if c[i].f >= s.f:
                    gasit_loc = True
                    break
            if gasit_loc:
                c.insert(i, s)
            else:
                c.append(s)
if __name__ == "__main__":
    # print("Solutii obtinute cu A*:")
    # t1 = time.time()
    gr = Graph("input.txt")
    # a_star(gr, nrSolutiiCautate=3, tip_euristica="euristica mutari cost")



    nod1 = NodParcurgere([[1, 2, 3], [4, 5, 6], [7, 8, 0]], None)
    nod2 = NodParcurgere([[1, 2, 3], [4, 0, 6], [7, 5, 8]], None)




    # print("Succesorii pentru nodul 1:")
    # succesori_nod1 = gr.genereazaSuccesori(nod1)
    # for succesor in succesori_nod1:
    #     print(succesor)
    #
    # print("\nSuccesorii pentru nodul 2:")
    # succesori_nod2 = gr.genereazaSuccesori(nod2)
    # for succesor in succesori_nod2:
    #     print(succesor)
    #
    #
    # print("\n\n##################\nSolutii obtinute cu BFS:")
    # t1 = time.time()
    # nodScopBFS = gr.BFS(NodParcurgere(gr.start, None))
    # if nodScopBFS:
    #     nodScopBFS.afisDrum(afisCost=True, afisLung=True)
    #     print(time.time() - t1, "secunde")
    #     print("----------------")

    print("\n\n##################\nSolutii obtinute cu DFS:")
    t1 = time.time()
    nodScopDFS = gr.DFS(NodParcurgere(gr.start, None))
    if nodScopDFS:
        nodScopDFS.afisDrum(afisCost=True, afisLung=True)
        print(time.time() - t1, "secunde")
        print("----------------")