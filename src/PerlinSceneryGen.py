import matplotlib.delaunay as triang
import numpy
import ogre.renderer.OGRE as ogre
import ogre.addons.noise as noise

class PerlinSceneryGen:

    def __init__(self, tangentBundle, normalScale = 0.4, maxLevel = 8, numOfPoints=50):
        self.tangentBundle = tangentBundle
        self.tris = None
        self.x = None
        self.y = None
        self.perlin = noise.Perlin()
        self.perlin.SetFrequency(2)
        self.perlin.SetOctaveCount(6)
        self.normalScale = normalScale
        self.maxLevel = maxLevel
        self.numPts = numOfPoints
    def setMaterial(self, materialName):
        self.material = materialName
    def _genBasicMesh(self):
        x = numpy.array(numpy.random.uniform(0, 2.0 * ogre.Math.PI, self.numPts))
        y = numpy.array(numpy.random.uniform(0, ogre.Math.PI, self.numPts))
        cens, edg, tri, neig = triang.delaunay(x, y)
        self.x = x
        self.y = y
        self.tris = tri
            
    def generate(self, manMesh):
        
        self.manMesh = manMesh
        self._genBasicMesh()
        manMesh.clear()
        mat = ogre.MaterialManager.getSingleton().getByName(self.material)
        mat.setReceiveShadows(False)
        manMesh.begin(mat.getName())
        self._generateSection(manMesh) #generate is in a 'private' function because we may want to do beginUpdate later. The structure of the man meshes ought to remain the same.
        manMesh.end()
    
    def _getRandom(self, pos):
        rand = (self.perlin.GetValue(pos.x, pos.y, pos.z) + 1.0) * 0.5
        
        return rand
    
    def _generateSection(self, manMesh):
        x = self.x
        y = self.y
        maxLevel = self.maxLevel
        currentLevel = 0
        triIdx = 0
            
        for t in self.tris:
            
            pt0 = ogre.Vector2(x[t[0]], y[t[0]])
            pt1 = ogre.Vector2(x[t[1]], y[t[1]])
            pt2 = ogre.Vector2(x[t[2]], y[t[2]])
            triIdx = self._subdivide([pt0, pt1, pt2], currentLevel, maxLevel, triIdx)
    
            
    def _subdivide(self, pts, currentLevel, maxLevel, triIdx):
        if(currentLevel == maxLevel):
            uvBottomLeft = ogre.Vector2(0.0, 0.0)
            uvBottomRight = ogre.Vector2(1.0, 0.0)
            uvTopRight = ogre.Vector2(1.0, 1.0)
            uvTopLeft = ogre.Vector2(0.0, 1.0)
            manMesh = self.manMesh
            #extrude
            posOnSphere0, normal0, ru0 = self.tangentBundle.uvMap(pts[0])
            posOnSphere1, normal1, ru1 = self.tangentBundle.uvMap(pts[1])
            posOnSphere2, normal2, ru2 = self.tangentBundle.uvMap(pts[2])
            
            rand0 = self._getRandom(posOnSphere0)
            rand1 = self._getRandom(posOnSphere1)
            rand2 = self._getRandom(posOnSphere2)
            
            posOnSphere1Top = posOnSphere1 + normal1 * rand1 * self.normalScale
            posOnSphere0Top = posOnSphere0 + normal0 * rand0 * self.normalScale
            posOnSphere2Top = posOnSphere2 + normal2 * rand2 * self.normalScale
            
            #bottom left
            manMesh.position(posOnSphere0)
            manMesh.normal(ru0)
            manMesh.textureCoord(uvBottomLeft)
            
            #bottom right
            manMesh.position(posOnSphere1)
            manMesh.normal(ru1)
            manMesh.textureCoord(uvBottomRight)
            
            #top right
            manMesh.position(posOnSphere1Top)
            manMesh.normal(ru1)
            manMesh.textureCoord(uvTopRight)
            
            #top left
            manMesh.position(posOnSphere0Top)
            manMesh.normal(ru0)
            manMesh.textureCoord(uvTopLeft)
            
            manMesh.triangle(triIdx, triIdx + 1, triIdx + 3)
            manMesh.triangle(triIdx + 3, triIdx + 1, triIdx + 2)
            triIdx += 4
            
            #ANother side 
            #bottom left
            manMesh.position(posOnSphere1)
            manMesh.normal(ru1)
            manMesh.textureCoord(uvBottomLeft)
            
            #bottom right
            manMesh.position(posOnSphere2)
            manMesh.normal(ru2)
            manMesh.textureCoord(uvBottomRight)
            
            #top right
            manMesh.position(posOnSphere2Top)
            manMesh.normal(ru2)
            manMesh.textureCoord(uvTopRight)
            
            #top left
            manMesh.position(posOnSphere1Top)
            manMesh.normal(ru1)
            manMesh.textureCoord(uvTopLeft)
            
            manMesh.triangle(triIdx, triIdx + 1, triIdx + 3)
            manMesh.triangle(triIdx + 3, triIdx + 1, triIdx + 2)
            triIdx += 4
            
            #Final side 
            #bottom left
            manMesh.position(posOnSphere2)
            manMesh.normal(ru2)
            manMesh.textureCoord(uvBottomLeft)
            
            #bottom right
            manMesh.position(posOnSphere0)
            manMesh.normal(ru0)
            manMesh.textureCoord(uvBottomRight)
            
            #top right
            manMesh.position(posOnSphere0Top)
            manMesh.normal(ru0)
            manMesh.textureCoord(uvTopRight)
            
            #top left
            manMesh.position(posOnSphere2Top)
            manMesh.normal(ru2)
            manMesh.textureCoord(uvTopLeft)
            
            manMesh.triangle(triIdx, triIdx + 1, triIdx + 3)
            manMesh.triangle(triIdx + 3, triIdx + 1, triIdx + 2)
            triIdx += 4
            
            return triIdx
        #determine max length edge
        maxLen = -1.0
        startTIndex = 0
        for i in range(3):
            nextIdx = (i + 1) % 3
            ptA = pts[i]
            ptB = pts[nextIdx]
            len = ptA.distance(ptB)
            if len > maxLen:
                maxLen = len
                startTIndex = i 
        #cut in half
        t0 = startTIndex
        t1 = (startTIndex + 1) % 3
        t2 = (startTIndex + 2) % 3
        
        newPt = pts[t0] + (pts[t1] - pts[t0]) * 0.5
        triIdx = self._subdivide([pts[t0], newPt, pts[t2]], currentLevel + 1, maxLevel, triIdx)
        triIdx = self._subdivide([newPt, pts[t1], pts[t2]], currentLevel + 1, maxLevel, triIdx)
        
        return triIdx
            
                
      