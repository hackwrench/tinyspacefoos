import ogre.renderer.OGRE as ogre
import random

class Planet:
    def __init__(self, node):
        self.node = node


class WorldController:
    def __init__(self, scnMgr, camera):
        
        self.scnMgr = scnMgr
        globalNode = scnMgr.getRootSceneNode().createChildSceneNode()
        self.globalNode = globalNode
        self.planets = []
        self.camera = camera
    
    def loadPlayer(self, pageCoords):
        
        playerNode = self.scnMgr.getRootSceneNode().createChildSceneNode()
        playerEnt = self.scnMgr.createEntity("RZR-002.mesh")
        
        playerNode.attachObject(playerEnt)
        playerNode.setScale(0.005, 0.005, 0.005)
        
        #pick a random planet
        randPlanetId = random.randint(0, len(self.planets) - 1)
        planet = self.planets[randPlanetId]
        node = planet[0]
        scale = planet[1]
        #for now just place the playerEnt over. 
        pos = node._getDerivedPosition()
        playerNode.setPosition(pos + playerNode.getOrientation().yAxis() * scale * 1.2)
        playerNode.attachObject(self.camera)
        #self.camera.setPosition(playerNode.getPosition() + ogre.Vector3(0.0, 25.0, 0.0))
        self.camera.setAutoTracking(True, playerNode)
        
        
        
    
    def onPageLoad(self, pageCoords):  
        self.loadPlanets(pageCoords)  
        self.loadPlayer(pageCoords)
    def loadPlanets(self, pageCoords):
        #create spheres
        numOfSpheres = 100
        
        
        self._createPlanet(pageCoords, 1.0)
        
        for i in range(1, numOfSpheres):
            #WARNING: Does not generate uniform randoms on the sphere
            randAnglePhi = ogre.Radian(random.uniform(0.0, 2.0 * ogre.Math.PI))
            randAnglePho = ogre.Radian(random.uniform(-ogre.Math.PI / 2.0, ogre.Math.PI / 2.0))
            randomOrient = ogre.Quaternion(randAnglePhi, ogre.Vector3(0.0, 1.0, 0.0))
            randomOrient = randomOrient * ogre.Quaternion(randAnglePho, ogre.Vector3(1.0, 0.0, 0.0))
            
            randDistance = random.uniform(3.0, 15.0)
            randScale = random.uniform(1.0, 50.0)
            self._createPlanet(pageCoords + randomOrient.zAxis() * randDistance, 1.0)
            
    def _createPlanet(self, pos, scale):
        ent = self.scnMgr.createEntity("geosphere4500.mesh")
        ent.setMaterialName("GridNormalMap")
        bb = ent.getMesh().getBoundingSphereRadius()
        scaleSphere = 1.0 / bb * scale
        print "radius: ", bb
        node = self.globalNode.createChildSceneNode()
        node.attachObject(ent)
        node.setPosition(pos)
        rad = ogre.Degree(random.randrange(0.0, 120.0)).valueRadians()
        tempOrient = ogre.Quaternion(ogre.Radian(rad), ogre.Vector3(1.0, 0.0, 0.0))
        node.setOrientation(tempOrient)
        node.setScale(scaleSphere, scaleSphere, scaleSphere)
        self.planets.append((node, scale))
        
            
                                    
        
        
        
        
        