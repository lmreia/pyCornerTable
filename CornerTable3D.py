#########################
# Author: lmreia
# License: GNU General Public License v3 (GPL-3)
#########################

import numpy as np
import matplotlib.pyplot as plt

class CornerTable3D:
    # Para a estrutura de corner table é necessário armazenar, para cada corner:
    #       cv (índice do vértice correspondente);
    #       co (índice do corner oposto);
    # e, para cada vértice, armazenar a posição (x,y,z) do vértice.
    # Estamos armazenando também os corners incidentes em cada vértice
    # para facilitar os cálculos de corner oposto.

    __NTetr = 0 # Quantidade de tetraedros na corner table.
    __Corners = [] # Lista de corners (índices dos vértices / cv).
    __OppositeCorners = [] # Lista de corners opostos (co).

    __NVertex = 0 # Quantidade de vértices na lista de vértices.
    __Vertices = [] # Lista de posições dos vértices.

    __IncidentCorners = [] # Lista de corners incidentes em cada vértice.

    __eps = 1e-10 # Erro admitido para ponto flutuante.

    # o tetraedro está sendo armazenado na seguinte ordem:
    #           B
    #          /|\
    #       /   |  \
    #  A <------|----> D
    #      \    |   /
    #        \  |  /
    #          \|/
    #           C
    # se eu faço o produto vetorial de AC com AD, o vetor resultante deve estar na direção de B.
    # significa que o produto escalar do vetor resultante com AB deve ser positivo.

    def __checkOrientation(self, x0, y0, z0, x1, y1, z1, x2, y2, z2, x3, y3, z3):
        A = np.asarray([x0, y0, z0])
        B = np.asarray([x1, y1, z1])
        C = np.asarray([x2, y2, z2])
        D = np.asarray([x3, y3, z3])
        AB = B-A
        AC = C-A
        AD = D-A
        return np.sign(np.dot(AB, np.cross(AC, AD)))

    # look-up table para verificar tetraedros vizinhos.
    # para cada vértice, lista as 3 faces que o vértice compõe.
    # em cada face os vértices estão em sentido anti-horário (para fora, regra da mão direita).
    __face_lut = np.asarray(
        [
            [[2, 1], [1, 3], [3, 2]],
            [[3, 0], [0, 2], [2, 3]],
            [[1, 0], [0, 3], [3, 1]],
            [[1, 2], [2, 0], [0, 1]]
        ], dtype=np.int32)

    __opposite_lut = np.asarray(
        [
            [3, 2, 1],
            [2, 3, 0],
            [3, 1, 0],
            [0, 1, 2]
        ], dtype=np.int32)

    # corner next.
    def cn(self, c):
        return int(np.floor(c / 4) * 4 + np.mod(c + 1, 4))
    
    # corner previous.
    def cp(self, c):
        return int(self.cn(self.cn(self.cn(c))))

    # obter o índice do tetraedro a partir do corner.
    def ct(self, c):
        return int(np.floor(c / 4))

    # corner A do tetraedro correspondente.
    def ca(self, c):
        return int(self.ct(c) * 4 + 0)

    # corner B do tetraedro correspondente.
    def cb(self, c):
        return int(self.ct(c) * 4 + 1)

    # corner C do tetraedro correspondente.
    def cc(self, c):
        return int(self.ct(c) * 4 + 2)

    # corner D do tetraedro correspondente.
    def cd(self, c):
        return int(self.ct(c) * 4 + 3)

    # # corner right.
    # def cr(self, c):
    #   return int(self.__OppositeCorners[self.cp(c)])
    #
    # # corner left.
    # def cl(self, c):
    #   return int(self.__OppositeCorners[self.cn(c)])

    # obter o índice do vértice correspondene ao corner.
    def cv(self, c):
      return int(self.__Corners[c])
    
    # opposite corner.
    def co(self, c):
        return int(self.__OppositeCorners[c])

    def __inVertices(self, x, y, z):
        if self.__NVertex > 0:
            # busca linear sobre a lista de vértices para encontrar o vértice
            # desejado.
            for i in range(self.__NVertex):
                dx = abs(self.__Vertices[i][0] - x)
                dy = abs(self.__Vertices[i][1] - y)
                dz = abs(self.__Vertices[i][2] - z)
                if dx < self.__eps and dy < self.__eps and dz < self.__eps:
                    return i
        return -1

    def __insertVertex(self, x, y, z, corner):
        # verificando se o vértice já existe na lista.
        Position = self.__inVertices(x, y, z)
        if Position == -1:
            # criando um vértice novo.
            self.__Vertices.append([x, y, z])
            Position = self.__NVertex
            self.__NVertex += 1
            # criando a lista de corners incidentes no vértice inserido.
            self.__IncidentCorners.append([corner])
        else:
            # utilizando um vértice já existente.
            # atualizando a lista de corners incidentes no vértice inserido.
            self.__IncidentCorners[Position].append(corner)
        return Position

    # Função para inserir um tetraedro na corner table a partir das
    # posições dos vértices.
    # Argumentos:
    #       posições (x, y, z) de cada um dos 4 vértices.
    def insertTetrahedron(self, x0, y0, z0, x1, y1, z1, x2, y2, z2, x3, y3, z3):
        # verificando orientação dos vértices.
        # se a orientação não estiver certa, faz swap dos vértices 1 e 2.
        if self.__checkOrientation(x0, y0, z0, x1, y1, z1, x2, y2, z2, x3, y3, z3) < 0:
            temp_x1 = x1
            temp_y1 = y1
            temp_z1 = z1
            x1 = x2
            y1 = y2
            z1 = z2
            x2 = temp_x1
            y2 = temp_y1
            z2 = temp_z1
        if self.__checkOrientation(x0, y0, z0, x1, y1, z1, x2, y2, z2, x3, y3, z3) < 0:
            raise Exception("Wrong vertices order")

        # inserindo os vértices.
        Position0 = self.__insertVertex(x0, y0, z0, self.__NTetr * 4 + 0)
        Position1 = self.__insertVertex(x1, y1, z1, self.__NTetr * 4 + 1)
        Position2 = self.__insertVertex(x2, y2, z2, self.__NTetr * 4 + 2)
        Position3 = self.__insertVertex(x3, y3, z3, self.__NTetr * 4 + 3)

        # inserindo os corners.
        self.__Corners.append(Position0) # c.v 0
        self.__Corners.append(Position1) # c.v 1
        self.__Corners.append(Position2) # c.v 2
        self.__Corners.append(Position3) # c.v 3
        self.__NTetr += 1

        # inserindo os corners opostos.
        # considerando que no python os índices começam em 0, o valor -1
        # significa que não existe corner oposto.
        # aqui os valores são apenas inicializados, mas o cálculo é realizado
        # abaixo.
        self.__OppositeCorners.append(-1) # c.o 0
        self.__OppositeCorners.append(-1) # c.o 1
        self.__OppositeCorners.append(-1) # c.o 2
        self.__OppositeCorners.append(-1) # c.o 3

        # calculando os corners opostos relativos aos vértices inseridos.
        # sendo c0 e c1 dois corners incidentes no mesmo vértice,
        # eu comparo cada face do tetraedro em c0 com cada face em c1.
        # o corner vai ser oposto se as faces corresponderem.
        for vertexIndex in [Position0, Position1, Position2, Position3]:
            incidentCornersLength = len(self.__IncidentCorners[vertexIndex])
            incidentCornersForV = self.__IncidentCorners[vertexIndex]
            for incidentCornerIndex1 in range(incidentCornersLength):
                for incidentCornerIndex2 in range(incidentCornersLength):
                    ic1 = incidentCornersForV[incidentCornerIndex1] # corner
                    ic2 = incidentCornersForV[incidentCornerIndex2]
                    it1 = self.ct(ic1) # tetraedro
                    it2 = self.ct(ic2)
                    icl1 = ic1 - it1 * 4 # corner local (em referência ao tetraedro)
                    icl2 = ic2 - it2 * 4
                    for f1 in range(3): # comparando cada face de um corner com cada face do outro corner
                        for f2 in range(3):
                            if self.__Corners[it1 * 4 + self.__face_lut[icl1][f1][0]] == self.__Corners[it2 * 4 + self.__face_lut[icl2][f2][1]] and self.__Corners[it1 * 4 + self.__face_lut[icl1][f1][1]] == self.__Corners[it2 * 4 + self.__face_lut[icl2][f2][0]]:
                                self.__OppositeCorners[it1 * 4 + self.__opposite_lut[icl1][f1]] = it2 * 4 + self.__opposite_lut[icl2][f2]
                                self.__OppositeCorners[it2 * 4 + self.__opposite_lut[icl2][f2]] = it1 * 4 + self.__opposite_lut[icl1][f1]


    # Função para remover um vértice da corner table a partir de sua
    # posição (x, y, z). Remove também todos os tetraedros que compartilham
    # este vértice e posteriormente remove os vértices que ficaram sem
    # nenhum corner após a remoção dos tetraedros.
    # Argumentos:
    #       posição (x, y, z) do vértice
    def removeVertex(self, x, y, z):
        # obtendo o índice do vértice na lista de vértices.
        removedVertexIndex = self.__inVertices(x, y, z)
        
        # se o vértice não existir na corner table, não é necessário
        # removê-lo.
        if removedVertexIndex == -1: 
            return
        
        # não pode simplesmente remover o vértice de todas as listas, 
        # porque iria bagunçar todas as referências de índices que
        # são feitas na corner table.
        # por este motivo, foi decidido dar swap com o último elemento em
        # vez de remover, e alterar apenas as referências a este único
        # elemento modificado.
        # deste modo, o último vértice vai assumir a posição do vértice
        # que está sendo removido.
        lastVertex = self.__NVertex - 1
        
        # pegando os corners incidentes no vértice que está sendo removido.
        incidentCornersForV = self.__IncidentCorners[removedVertexIndex]
        
        # quando remove um vértice, tem que remover todos os tetraedros
        # ligados neste vértice.
        # pegando a lista de tetraedros que vão ser removidos devido à
        # remoção do vértice
        # de forma análoga ao vértice, cada tetraedro removido será
        # substituído pelo último tetraedro da lista (swap com o último).
        tetrahedraToBeRemoved = []
        for i in range(len(incidentCornersForV)):
            tetrahedraToBeRemoved.append(self.ct(incidentCornersForV[i]))

        # vai remover de baixo para cima.
        tetrahedraToBeRemoved.sort(reverse=True)
        
        # ao remover múltiplos tetraedros, pode acontecer de outros vértices
        # também serem removidos (caso não sobre nenhum corner incidente
        # nestes vértices).
        # lista de vértices que serão marcados para remoção ao final da
        # função.
        vertexMarkedForRemoval = []
        
        # removendo os tetraedros e todos os seus corners.
        for tetrahedronIndex in tetrahedraToBeRemoved:
            # corners do tetraedro sendo removido.
            c0 = tetrahedronIndex * 4 + 0
            c1 = tetrahedronIndex * 4 + 1
            c2 = tetrahedronIndex * 4 + 2
            c3 = tetrahedronIndex * 4 + 3

            # removendo estes corners da lista de incident corners de cada 
            # vértice respectivamente.
            for cornerIndex in [c0, c1, c2, c3]:
                tetrahedronVertexIndex = self.__Corners[cornerIndex]
                for i in range(len(self.__IncidentCorners[tetrahedronVertexIndex])):
                    if self.__IncidentCorners[tetrahedronVertexIndex][i] == cornerIndex:
                        del self.__IncidentCorners[tetrahedronVertexIndex][i]
                        break
                # se __IncidentCorners[tetrahedronVertexIndex] ficar vazio,
                # este vértice tem que ser removido também.
                if not self.__IncidentCorners[tetrahedronVertexIndex]:
                    vertexMarkedForRemoval.append(self.__Vertices[tetrahedronVertexIndex])
            
            # atualizando os incident corners dos vértices dos corners do
            # último tetraedro (que vai mudar de posição).
            for j in range(4):
                lastCornerIndex = (self.__NTetr - 1) * 4 + j
                removedCornerIndex = tetrahedronIndex * 4 + j
                tetrahedronVertexIndex = self.__Corners[lastCornerIndex]
                for i in range(len(self.__IncidentCorners[tetrahedronVertexIndex])):
                    if self.__IncidentCorners[tetrahedronVertexIndex][i] == lastCornerIndex:
                        self.__IncidentCorners[tetrahedronVertexIndex][i] = removedCornerIndex
                        break

            # removendo os corners dos opposite corners.
            if self.__OppositeCorners[c0] >= 0:
                self.__OppositeCorners[self.__OppositeCorners[c0]] = -1
                self.__OppositeCorners[c0] = -1
            if self.__OppositeCorners[c1] >= 0:
                self.__OppositeCorners[self.__OppositeCorners[c1]] = -1
                self.__OppositeCorners[c1] = -1
            if self.__OppositeCorners[c2] >= 0:
                self.__OppositeCorners[self.__OppositeCorners[c2]] = -1
                self.__OppositeCorners[c2] = -1
            if self.__OppositeCorners[c3] >= 0:
                self.__OppositeCorners[self.__OppositeCorners[c3]] = -1
                self.__OppositeCorners[c3] = -1
            
            # substituindo os corners pelo último tetraedro.
            if self.__OppositeCorners[(self.__NTetr - 1) * 4 + 0] >= 0:
                self.__OppositeCorners[self.__OppositeCorners[(self.__NTetr - 1) * 4 + 0]] = c0
            if self.__OppositeCorners[(self.__NTetr - 1) * 4 + 1] >= 0:
                self.__OppositeCorners[self.__OppositeCorners[(self.__NTetr - 1) * 4 + 1]] = c1
            if self.__OppositeCorners[(self.__NTetr - 1) * 4 + 2] >= 0:
                self.__OppositeCorners[self.__OppositeCorners[(self.__NTetr - 1) * 4 + 2]] = c2
            if self.__OppositeCorners[(self.__NTetr - 1) * 4 + 3] >= 0:
                self.__OppositeCorners[self.__OppositeCorners[(self.__NTetr - 1) * 4 + 3]] = c3
            
            self.__Corners[c0] = self.__Corners[(self.__NTetr - 1) * 4 + 0]
            self.__Corners[c1] = self.__Corners[(self.__NTetr - 1) * 4 + 1]
            self.__Corners[c2] = self.__Corners[(self.__NTetr - 1) * 4 + 2]
            self.__Corners[c3] = self.__Corners[(self.__NTetr - 1) * 4 + 3]
            self.__OppositeCorners[c0] = self.__OppositeCorners[(self.__NTetr - 1) * 4 + 0]
            self.__OppositeCorners[c1] = self.__OppositeCorners[(self.__NTetr - 1) * 4 + 1]
            self.__OppositeCorners[c2] = self.__OppositeCorners[(self.__NTetr - 1) * 4 + 2]
            self.__OppositeCorners[c3] = self.__OppositeCorners[(self.__NTetr - 1) * 4 + 3]
            del self.__Corners[(self.__NTetr - 1) * 4 + 3]
            del self.__Corners[(self.__NTetr - 1) * 4 + 2]
            del self.__Corners[(self.__NTetr - 1) * 4 + 1]
            del self.__Corners[(self.__NTetr - 1) * 4 + 0]
            del self.__OppositeCorners[(self.__NTetr - 1) * 4 + 3]
            del self.__OppositeCorners[(self.__NTetr - 1) * 4 + 2]
            del self.__OppositeCorners[(self.__NTetr - 1) * 4 + 1]
            del self.__OppositeCorners[(self.__NTetr - 1) * 4 + 0]
            
            # atualizando a quantidade de tetraedros.
            self.__NTetr -= 1
        
        # removendo o vértice da matriz de posições.
        self.__Vertices[removedVertexIndex] = self.__Vertices[lastVertex]
        del self.__Vertices[lastVertex]
        
        # atualizando as referências dos corners ao último vértice, que vai
        # mudar de posição.
        incidentCornersForLastV = self.__IncidentCorners[lastVertex]
        for cornerIndex in incidentCornersForLastV:
            self.__Corners[cornerIndex] = removedVertexIndex
        
        # removendo o vértice da lista de incident corners.
        self.__IncidentCorners[removedVertexIndex] = self.__IncidentCorners[lastVertex]
        del self.__IncidentCorners[lastVertex]
        
        # atualizando a quantidade de vértices.
        self.__NVertex -= 1
        
        # removendo os vértices vazios que sobraram.
        for i in range(len(vertexMarkedForRemoval)):
            self.removeVertex(vertexMarkedForRemoval[i][0], vertexMarkedForRemoval[i][1], vertexMarkedForRemoval[i][2])
        
    # Função para remover tetraedros a partir de seus índices
    # Argumentos:
    #       índices dos tetraedros a serem removidos.
    def removeTetrahedra(self, tetrahedraToBeRemoved):
        # remove de baixo para cima.
        tetrahedraToBeRemoved.sort(reverse = True)
        
        # ao remover múltiplos tetraedros, pode acontecer de outros vértices
        # também serem removidos (caso não sobre nenhum corner incidente
        # nestes vértices).
        # lista de vértices que serão marcados para remoção ao final da
        # função.
        vertexMarkedForRemoval = []
        
        # removendo os tetraedros e todos os seus corners.
        for tetrahedronIndex in tetrahedraToBeRemoved:
            # se o índice do tetraedro for maior do que a quantidade de
            # tetraedros, significa que o tetraedro não existe
            if tetrahedronIndex >= self.__NTetr:
                continue
            
            # corners do tetraedro sendo removido
            c0 = tetrahedronIndex * 4 + 0
            c1 = tetrahedronIndex * 4 + 1
            c2 = tetrahedronIndex * 4 + 2
            c3 = tetrahedronIndex * 4 + 3

            # removendo estes corners da lista de incident corners de cada 
            # vértice respectivamente.
            for cornerIndex in [c0, c1, c2, c3]:
                tetrahedronVertexIndex = self.__Corners[cornerIndex]
                for i in range(len(self.__IncidentCorners[tetrahedronVertexIndex])):
                    if self.__IncidentCorners[tetrahedronVertexIndex][i] == cornerIndex:
                        del self.__IncidentCorners[tetrahedronVertexIndex][i]
                        break
                # se IncidentCorners[tetrahedronVertexIndex] ficar vazio,
                # este vértice tem que ser removido também.
                if not self.__IncidentCorners[tetrahedronVertexIndex]:
                    vertexMarkedForRemoval.append(self.__Vertices[tetrahedronVertexIndex])
            
            # atualizando os incident corners dos vértices dos corners do
            # último tetraedro (que vai mudar de posição).
            for j in range(4):
                lastCornerIndex = (self.__NTetr - 1) * 4 + j
                removedCornerIndex = tetrahedronIndex * 4 + j
                tetrahedronVertexIndex = self.__Corners[lastCornerIndex]
                for i in range(len(self.__IncidentCorners[tetrahedronVertexIndex])):
                    if self.__IncidentCorners[tetrahedronVertexIndex][i] == lastCornerIndex:
                        self.__IncidentCorners[tetrahedronVertexIndex][i] = removedCornerIndex
                        break
            
            # removendo os corners dos opposite corners.
            if self.__OppositeCorners[c0] >= 0:
                self.__OppositeCorners[self.__OppositeCorners[c0]] = -1
                self.__OppositeCorners[c0] = -1
            if self.__OppositeCorners[c1] >= 0:
                self.__OppositeCorners[self.__OppositeCorners[c1]] = -1
                self.__OppositeCorners[c1] = -1
            if self.__OppositeCorners[c2] >= 0:
                self.__OppositeCorners[self.__OppositeCorners[c2]] = -1
                self.__OppositeCorners[c2] = -1
            if self.__OppositeCorners[c3] >= 0:
                self.__OppositeCorners[self.__OppositeCorners[c3]] = -1
                self.__OppositeCorners[c3] = -1

            # substituindo os corners pelo último tetraedro.
            if self.__OppositeCorners[(self.__NTetr - 1) * 4 + 0] >= 0:
                self.__OppositeCorners[self.__OppositeCorners[(self.__NTetr - 1) * 4 + 0]] = c0
            if self.__OppositeCorners[(self.__NTetr - 1) * 4 + 1] >= 0:
                self.__OppositeCorners[self.__OppositeCorners[(self.__NTetr - 1) * 4 + 1]] = c1
            if self.__OppositeCorners[(self.__NTetr - 1) * 4 + 2] >= 0:
                self.__OppositeCorners[self.__OppositeCorners[(self.__NTetr - 1) * 4 + 2]] = c2
            if self.__OppositeCorners[(self.__NTetr - 1) * 4 + 3] >= 0:
                self.__OppositeCorners[self.__OppositeCorners[(self.__NTetr - 1) * 4 + 3]] = c3
            
            self.__Corners[c0] = self.__Corners[(self.__NTetr - 1) * 4 + 0]
            self.__Corners[c1] = self.__Corners[(self.__NTetr - 1) * 4 + 1]
            self.__Corners[c2] = self.__Corners[(self.__NTetr - 1) * 4 + 2]
            self.__Corners[c3] = self.__Corners[(self.__NTetr - 1) * 4 + 3]
            self.__OppositeCorners[c0] = self.__OppositeCorners[(self.__NTetr - 1) * 4 + 0]
            self.__OppositeCorners[c1] = self.__OppositeCorners[(self.__NTetr - 1) * 4 + 1]
            self.__OppositeCorners[c2] = self.__OppositeCorners[(self.__NTetr - 1) * 4 + 2]
            self.__OppositeCorners[c3] = self.__OppositeCorners[(self.__NTetr - 1) * 4 + 3]
            del self.__Corners[(self.__NTetr - 1) * 4 + 3]
            del self.__Corners[(self.__NTetr - 1) * 4 + 2]
            del self.__Corners[(self.__NTetr - 1) * 4 + 1]
            del self.__Corners[(self.__NTetr - 1) * 4 + 0]
            del self.__OppositeCorners[(self.__NTetr - 1) * 4 + 3]
            del self.__OppositeCorners[(self.__NTetr - 1) * 4 + 2]
            del self.__OppositeCorners[(self.__NTetr - 1) * 4 + 1]
            del self.__OppositeCorners[(self.__NTetr - 1) * 4 + 0]
            
            # atualizando a quantidade de tetraedros.
            self.__NTetr -= 1
        
        # removendo os vértices vazios que sobraram.
        for i in range(len(vertexMarkedForRemoval)):
            self.removeVertex(vertexMarkedForRemoval[i][0], vertexMarkedForRemoval[i][1], vertexMarkedForRemoval[i][2])

    # Gerar a corner table completa.
    def getFullCornerTable(self):
        fullCornerTable = []
        for c in range(len(self.__Corners)):
            fullCornerTable.append(
                [
                    c,
                    self.cv(c),
                    self.ct(c),
                    self.cn(c),
                    self.cp(c),
                    self.co(c),
                    self.ca(c),
                    self.cb(c),
                    self.cc(c),
                    self.cd(c)
                    # ,
                    # self.cl(c),
                    # self.cr(c)
                ]
            )
        return fullCornerTable

    # Função para plotar a mesh que compõe uma corner table
    # Argumentos:
    #       titleString = título do plot.
    #       displayLabels = true ou false, habilitar desenho dos labels no plot.
    def plotCornerTableMesh(self, title = None, displayLabels = False):
        vertices = np.asarray(self.__Vertices)
        indexes = np.asarray(self.__Corners).reshape((self.__NTetr, 4))

        # Exibindo a mesh.
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        for i in range(indexes.shape[0]):
            a = vertices[indexes[i,0],:]
            b = vertices[indexes[i,1],:]
            c = vertices[indexes[i,2],:]
            d = vertices[indexes[i,3],:]
            x = np.asarray([a[0], c[0], b[0], a[0], d[0], b[0], c[0], d[0]])
            y = np.asarray([a[1], c[1], b[1], a[1], d[1], b[1], c[1], d[1]])
            z = np.asarray([a[2], c[2], b[2], a[2], d[2], b[2], c[2], d[2]])
            ax.plot(x, y, z, 'k-')
        #ax.plot_trisurf(vertices[:, 0], vertices[:,1], triangles = indexes, Z = vertices[:,2])

        # Desenhando as labels dos vértices/corners.
        if displayLabels:
            # Plotando os labels dos vértices.
            for i in range(self.__NVertex):
                coord = self.__Vertices[i]
                ax.text(coord[0],coord[1],coord[2], 'v'+str(i), color = 'blue' , fontweight = 'bold', horizontalalignment = 'center')
            # Plotando os labels dos corners.
            for i in range(len(self.__Corners)):
                c = i
                cn = self.cn(c)
                cn2 = self.cn(cn)
                cp = self.cp(c)
                v = self.cv(c)
                vn = self.cv(cn)
                vn2 = self.cv(cn2)
                vp = self.cv(cp)
                coord = np.asarray(self.__Vertices[v])
                coordn = np.asarray(self.__Vertices[vn])
                coordn2 = np.asarray(self.__Vertices[vn2])
                coordp = np.asarray(self.__Vertices[vp])

                coordtext = ((coordn - coord) + (coordn2 - coord) + (coordp - coord)) / 10 + coord
                ax.text(coordtext[0],coordtext[1],coordtext[2],'c'+str(c), color = 'red', fontweight = 'normal', horizontalalignment = 'center')
            # Plotando os labels dos tetraedros.
            for i in range(self.__NTetr):
                c1 = i * 4
                c2 = self.cn(c1)
                c4 = self.cn(c2)
                c3 = self.cp(c1)
                v1 = self.cv(c1)
                v2 = self.cv(c2)
                v4 = self.cv(c4)
                v3 = self.cv(c3)
                coord1 = np.asarray(self.__Vertices[v1])
                coord2 = np.asarray(self.__Vertices[v2])
                coord4 = np.asarray(self.__Vertices[v4])
                coord3 = np.asarray(self.__Vertices[v3])

                coordtext = (coord1 + coord2 + coord3 + coord4) / 4
                ax.text(coordtext[0],coordtext[1],coordtext[2],'t'+str(i), color = 'black' , fontweight = 'bold', horizontalalignment = 'center')

        # Adicionando título e nomes dos eixos.
        if title:
            ax.set_title(title)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
        plt.show()

