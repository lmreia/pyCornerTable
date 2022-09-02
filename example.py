import CornerTable
import numpy as np
import pywavefront


# Example 1
#cornerTable = CornerTable()
#cornerTable.insertTriangle(0,0,0, 1,0,0, 0,1,0)
#cornerTable.insertTriangle(0,0,0, 0,1,0, 0,0,1)
#print('c v t n p o l r')
#print(np.asarray(cornerTable.getFullCornerTable()))
#cornerTable.plotCornerTableMesh('simple', True)


# Example 2
scene = pywavefront.Wavefront('small_disk.obj', collect_faces = True, create_materials=True)

vertices = scene.vertices
faces = scene.mesh_list[0].faces

cornerTable = CornerTable.CornerTable()
for i in range(len(faces)):
    f0 = faces[i][0]
    f1 = faces[i][1]
    f2 = faces[i][2]
    p0 = vertices[f0]
    p1 = vertices[f1]
    p2 = vertices[f2]
    cornerTable.insertTriangle(
        p0[0], p0[1], p0[2], 
        p1[0], p1[1], p1[2], 
        p2[0], p2[1], p2[2]
    )

print('c v t n p o l r')
print(np.asarray(cornerTable.getFullCornerTable()))
cornerTable.plotCornerTableMesh('disk', True)

cornerTable.removeTriangles([26, 18, 20])
cornerTable.plotCornerTableMesh('disk', True)

cornerTable.removeVertex(vertices[15][0], vertices[15][1], vertices[15][2])
cornerTable.removeVertex(vertices[5][0], vertices[5][1], vertices[5][2])
cornerTable.plotCornerTableMesh('disk', True)