#########################
# Author: lmreia
# License: GNU General Public License v3 (GPL-3)
#########################

import numpy as np
import matplotlib.pyplot as plt

class CornerTable:
    # Para a estrutura de corner table é necessário armazenar, para cada corner:
    #       cv (índice do vértice correspondente);
    #       co (índice do corner oposto);
    # e, para cada vértice, armazenar a posição (x,y,z) do vértice.
    # Estamos armazenando também os corners incidentes em cada vértice
    # para facilitar os cálculos de corner oposto.

    __NTri = 0 # Quantidade de triângulos na corner table.
    __Corners = [] # Lista de corners (índices dos vértices / cv).
    __OppositeCorners = [] # Lista de corners opostos (co).

    __NVertex = 0 # Quantidade de vértices na lista de vértices.
    __Vertices = [] # Lista de posições dos vértices.

    __IncidentCorners = [] # Lista de corners incidentes em cada vértice.

    __eps = 1e-10 # Erro admitido para ponto flutuante.

    # corner next.
    def cn(self, c):
        return int(np.floor(c / 3) * 3 + np.mod(c + 1, 3))
    
    # corner previous.
    def cp(self, c):
        return int(self.cn(self.cn(c)))

    # obter o índice do triângulo a partir do corner.
    def ct(self, c):
        return int(np.floor(c / 3))

    # corner right.
    def cr(self, c):
      return int(self.__OppositeCorners[self.cp(c)])
          
    # corner left.
    def cl(self, c):
      return int(self.__OppositeCorners[self.cn(c)])

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

    # Função para inserir um triângulo na corner table a partir das
    # posições dos vértices.
    # Argumentos:
    #       posições (x, y, z) de cada um dos 3 vértices, ordenados em sentido
    #       anti-horário.
    def insertTriangle(self, x0, y0, z0, x1, y1, z1, x2, y2, z2):
        # inserindo os vértices.
        Position0 = self.__insertVertex(x0, y0, z0, self.__NTri * 3 + 0)
        Position1 = self.__insertVertex(x1, y1, z1, self.__NTri * 3 + 1)
        Position2 = self.__insertVertex(x2, y2, z2, self.__NTri * 3 + 2)

        # inserindo os corners.
        self.__Corners.append(Position0) # c.v 0
        self.__Corners.append(Position1) # c.v 1
        self.__Corners.append(Position2) # c.v 2
        self.__NTri += 1

        # inserindo os corners opostos.
        # considerando que no python os índices começam em 0, o valor -1
        # significa que não existe corner oposto.
        # aqui os valores são apenas inicializados, mas o cálculo é realizado
        # abaixo.
        self.__OppositeCorners.append(-1) # c.o 0
        self.__OppositeCorners.append(-1) # c.o 1
        self.__OppositeCorners.append(-1) # c.o 2

        # calculando os corners opostos relativos aos vértices inseridos.
        # sendo c0 e c1 dois corners incidentes no mesmo vértice,
        # se cv(cn(c0)) == cv(cp(c1)), então co(cp(c0)) = cn(c1)
        #                                  e co(cn(c1)) = cp(c0).
        for vertexIndex in [Position0, Position1, Position2]:
            incidentCornersLength = len(self.__IncidentCorners[vertexIndex])
            incidentCornersForV = self.__IncidentCorners[vertexIndex]
            for incidentCornerIndex1 in range(incidentCornersLength):
                for incidentCornerIndex2 in range(incidentCornersLength):
                    ic1 = incidentCornersForV[incidentCornerIndex1]
                    ic2 = incidentCornersForV[incidentCornerIndex2]
                    if self.__Corners[self.cn(ic1)] == self.__Corners[self.cp(ic2)]:
                        self.__OppositeCorners[self.cp(ic1)] = self.cn(ic2)
                        self.__OppositeCorners[self.cn(ic2)] = self.cp(ic1)

    # Função para remover um vértice da corner table a partir de sua
    # posição (x, y, z). Remove também todos os triângulos que compartilham
    # este vértice e posteriormente remove os vértices que ficaram sem
    # nenhum corner após a remoção dos triângulos.
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
        
        # quando remove um vértice, tem que remover todos os triângulos
        # ligados neste vértice.
        # pegando a lista de triângulos que vão ser removidos devido à
        # remoção do vértice
        # de forma análoga ao vértice, cada triângulo removido será 
        # substituído pelo último triângulo da lista (swap com o último).
        trianglesToBeRemoved = []
        for i in range(len(incidentCornersForV)):
            trianglesToBeRemoved.append(self.ct(incidentCornersForV[i]))

        # vai remover de baixo para cima.
        trianglesToBeRemoved.sort(reverse=True)
        
        # ao remover múltiplos triângulos, pode acontecer de outros vértices
        # também serem removidos (caso não sobre nenhum corner incidente
        # nestes vértices).
        # lista de vértices que serão marcados para remoção ao final da
        # função.
        vertexMarkedForRemoval = []
        
        # removendo os triângulos e todos os seus corners.
        for triangleIndex in trianglesToBeRemoved:
            # corners do triangulo sendo removido.
            c0 = triangleIndex * 3 + 0
            c1 = triangleIndex * 3 + 1
            c2 = triangleIndex * 3 + 2
            
            # removendo estes corners da lista de incident corners de cada 
            # vértice respectivamente.
            for cornerIndex in [c0, c1, c2]:
                triangleVertexIndex = self.__Corners[cornerIndex]
                for i in range(len(self.__IncidentCorners[triangleVertexIndex])):
                    if self.__IncidentCorners[triangleVertexIndex][i] == cornerIndex:
                        del self.__IncidentCorners[triangleVertexIndex][i]
                        break
                # se __IncidentCorners[triangleVertexIndex] ficar vazio,
                # este vértice tem que ser removido também.
                if not self.__IncidentCorners[triangleVertexIndex]:
                    vertexMarkedForRemoval.append(self.__Vertices[triangleVertexIndex])
            
            # atualizando os incident corners dos vértices dos corners do
            # último triângulo (que vai mudar de posição).
            for j in range(3):
                lastCornerIndex = (self.__NTri - 1) * 3 + j
                removedCornerIndex = triangleIndex * 3 + j
                triangleVertexIndex = self.__Corners[lastCornerIndex]
                for i in range(len(self.__IncidentCorners[triangleVertexIndex])):
                    if self.__IncidentCorners[triangleVertexIndex][i] == lastCornerIndex:
                        self.__IncidentCorners[triangleVertexIndex][i] = removedCornerIndex
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
            
            # substituindo os corners pelo último triângulo.
            if self.__OppositeCorners[(self.__NTri - 1) * 3 + 0] >= 0:
                self.__OppositeCorners[self.__OppositeCorners[(self.__NTri - 1) * 3 + 0]] = c0
            if self.__OppositeCorners[(self.__NTri - 1) * 3 + 1] >= 0:
                self.__OppositeCorners[self.__OppositeCorners[(self.__NTri - 1) * 3 + 1]] = c1
            if self.__OppositeCorners[(self.__NTri - 1) * 3 + 2] >= 0:
                self.__OppositeCorners[self.__OppositeCorners[(self.__NTri - 1) * 3 + 2]] = c2
            
            self.__Corners[c0] = self.__Corners[(self.__NTri - 1) * 3 + 0]
            self.__Corners[c1] = self.__Corners[(self.__NTri - 1) * 3 + 1]
            self.__Corners[c2] = self.__Corners[(self.__NTri - 1) * 3 + 2]
            self.__OppositeCorners[c0] = self.__OppositeCorners[(self.__NTri - 1) * 3 + 0]
            self.__OppositeCorners[c1] = self.__OppositeCorners[(self.__NTri - 1) * 3 + 1]
            self.__OppositeCorners[c2] = self.__OppositeCorners[(self.__NTri - 1) * 3 + 2]
            del self.__Corners[(self.__NTri - 1) * 3 + 2]
            del self.__Corners[(self.__NTri - 1) * 3 + 1]
            del self.__Corners[(self.__NTri - 1) * 3 + 0]
            del self.__OppositeCorners[(self.__NTri - 1) * 3 + 2]
            del self.__OppositeCorners[(self.__NTri - 1) * 3 + 1]
            del self.__OppositeCorners[(self.__NTri - 1) * 3 + 0]
            
            # atualizando a quantidade de triângulos.
            self.__NTri -= 1
        
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
        
    # Função para remover triângulos a partir de seus índices
    # Argumentos:
    #       índices dos triângulos a serem removidos.
    def removeTriangles(self, trianglesToBeRemoved):
        # remove de baixo para cima.
        trianglesToBeRemoved.sort(reverse = True)
        
        # ao remover múltiplos triângulos, pode acontecer de outros vértices
        # também serem removidos (caso não sobre nenhum corner incidente
        # nestes vértices).
        # lista de vértices que serão marcados para remoção ao final da
        # função.
        vertexMarkedForRemoval = []
        
        # removendo os triângulos e todos os seus corners.
        for triangleIndex in trianglesToBeRemoved:
            # se o índice do triângulo for maior do que a quantidade de
            # triângulos, significa que o triângulo não existe
            if triangleIndex > self.__NTri:
                continue
            
            # corners do triangulo sendo removido
            c0 = triangleIndex * 3 + 0
            c1 = triangleIndex * 3 + 1
            c2 = triangleIndex * 3 + 2
            
            # removendo estes corners da lista de incident corners de cada 
            # vértice respectivamente.
            for cornerIndex in [c0, c1, c2]:
                triangleVertexIndex = self.__Corners[cornerIndex]
                for i in range(len(self.__IncidentCorners[triangleVertexIndex])):
                    if self.__IncidentCorners[triangleVertexIndex][i] == cornerIndex:
                        del self.__IncidentCorners[triangleVertexIndex][i]
                        break
                # se IncidentCorners[triangleVertexIndex] ficar vazio,
                # este vértice tem que ser removido também.
                if not self.__IncidentCorners[triangleVertexIndex]:
                    vertexMarkedForRemoval.append(self.__Vertices[triangleVertexIndex])
            
            # atualizando os incident corners dos vértices dos corners do
            # último triângulo (que vai mudar de posição).
            for j in range(3):
                lastCornerIndex = (self.__NTri - 1) * 3 + j
                removedCornerIndex = triangleIndex * 3 + j
                triangleVertexIndex = self.__Corners[lastCornerIndex]
                for i in range(len(self.__IncidentCorners[triangleVertexIndex])):
                    if self.__IncidentCorners[triangleVertexIndex][i] == lastCornerIndex:
                        self.__IncidentCorners[triangleVertexIndex][i] = removedCornerIndex
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
            
            # substituindo os corners pelo último triângulo.
            if self.__OppositeCorners[(self.__NTri - 1) * 3 + 0] >= 0:
                self.__OppositeCorners[self.__OppositeCorners[(self.__NTri - 1) * 3 + 0]] = c0
            if self.__OppositeCorners[(self.__NTri - 1) * 3 + 1] >= 0:
                self.__OppositeCorners[self.__OppositeCorners[(self.__NTri - 1) * 3 + 1]] = c1
            if self.__OppositeCorners[(self.__NTri - 1) * 3 + 2] >= 0:
                self.__OppositeCorners[self.__OppositeCorners[(self.__NTri - 1) * 3 + 2]] = c2
            
            self.__Corners[c0] = self.__Corners[(self.__NTri - 1) * 3 + 0]
            self.__Corners[c1] = self.__Corners[(self.__NTri - 1) * 3 + 1]
            self.__Corners[c2] = self.__Corners[(self.__NTri - 1) * 3 + 2]
            self.__OppositeCorners[c0] = self.__OppositeCorners[(self.__NTri - 1) * 3 + 0]
            self.__OppositeCorners[c1] = self.__OppositeCorners[(self.__NTri - 1) * 3 + 1]
            self.__OppositeCorners[c2] = self.__OppositeCorners[(self.__NTri - 1) * 3 + 2]
            del self.__Corners[(self.__NTri - 1) * 3 + 2]
            del self.__Corners[(self.__NTri - 1) * 3 + 1]
            del self.__Corners[(self.__NTri - 1) * 3 + 0]
            del self.__OppositeCorners[(self.__NTri - 1) * 3 + 2]
            del self.__OppositeCorners[(self.__NTri - 1) * 3 + 1]
            del self.__OppositeCorners[(self.__NTri - 1) * 3 + 0]
            
            # atualizando a quantidade de triângulos.
            self.__NTri -= 1
        
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
                    self.cl(c),
                    self.cr(c)
                ]
            )
        return fullCornerTable

    # Função para plotar a mesh que compõe uma corner table
    # Argumentos:
    #       titleString = título do plot.
    #       displayLabels = true ou false, habilitar desenho dos labels no plot.
    def plotCornerTableMesh(self, title = None, displayLabels = False):
        vertices = np.asarray(self.__Vertices)
        indexes = np.asarray(self.__Corners).reshape((self.__NTri, 3))

        # Exibindo a mesh.
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_trisurf(vertices[:, 0], vertices[:,1], triangles = indexes, Z = vertices[:,2])

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
                cp = self.cp(c)
                v = self.cv(c)
                vn = self.cv(cn)
                vp = self.cv(cp)
                coord = np.asarray(self.__Vertices[v])
                coordn = np.asarray(self.__Vertices[vn])
                coordp = np.asarray(self.__Vertices[vp])

                coordtext = ((coordn - coord) + (coordp - coord)) / 10 + coord
                ax.text(coordtext[0],coordtext[1],coordtext[2],'c'+str(c), color = 'red', fontweight = 'normal', horizontalalignment = 'center')
            # Plotando os labels dos triângulos.
            for i in range(self.__NTri):
                c1 = i * 3
                c2 = self.cn(c1)
                c3 = self.cp(c1)
                v1 = self.cv(c1)
                v2 = self.cv(c2)
                v3 = self.cv(c3)
                coord1 = np.asarray(self.__Vertices[v1])
                coord2 = np.asarray(self.__Vertices[v2])
                coord3 = np.asarray(self.__Vertices[v3])

                coordtext = (coord1 + coord2 + coord3) / 3
                ax.text(coordtext[0],coordtext[1],coordtext[2],'t'+str(i), color = 'black' , fontweight = 'bold', horizontalalignment = 'center')

        # Adicionando título e nomes dos eixos.
        if title:
            ax.set_title(title)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
        plt.show()

