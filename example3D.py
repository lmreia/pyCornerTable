import CornerTable3D
import numpy as np


# Example 1
cornerTable3D = CornerTable3D.CornerTable3D()
cornerTable3D.insertTetrahedron(-1,1,0, 0,0,1, 0,-1,0, 1,1,0)
cornerTable3D.insertTetrahedron(-1,1,0, 0,0,-1, 0,-1,0, 1,1,0)
cornerTable3D.insertTetrahedron(-1,1,0, 0,0,1, 0,-1,0, -1,-1,0)
cornerTable3D.insertTetrahedron(-1,1,0, 0,0,-1, 0,-1,0, -1,-1,0)
cornerTable3D.insertTetrahedron(-1,1,0, 0,0,-1, -1,0,-1, -1,-1,0)
print('c v t n p o a b c d')
print(np.asarray(cornerTable3D.getFullCornerTable()))
cornerTable3D.plotCornerTableMesh('simple', True)

cornerTable3D.removeVertex(0,0,1)
print('c v t n p o a b c d')
print(np.asarray(cornerTable3D.getFullCornerTable()))
cornerTable3D.plotCornerTableMesh('vertex removed', True)

cornerTable3D.removeTetrahedra([0])
print('c v t n p o a b c d')
print(np.asarray(cornerTable3D.getFullCornerTable()))
cornerTable3D.plotCornerTableMesh('tertrahedron removed', True)
