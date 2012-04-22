import ogre.renderer.OGRE as ogre
import random
import math

class TangentBundle:
    def __init__(self, sphere):
        self.sphere = sphere
        self.r = 1.0
        self.theta = 0.0
        self.phi = 0.0
        self.ru = ogre.Vector3()
        self.rv = ogre.Vector3()
        self.pos = ogre.Vector3()
    def newPosition(self):
        return self.pos
        
    def setPosition(self, pos):
        self.normal = pos - ogre.Vector3(0.0, 0.0, 0.0)
        self.normal.normalise()
        self.pos = self.normal * self.sphere[1]
      
    def setPosition2(self, pos):
        print "posIn: ", pos
        #self.r = ogre.Math.Sqrt(pos.x*pos.x + pos.y*pos.y + pos.z*pos.z)
        self.r = math.sqrt(pos.x*pos.x + pos.y*pos.y + pos.z*pos.z)
        #self.r = self.sphere[1]
        #print "r: ", self.r
        self.phi = math.acos(pos.z / self.r) #using python math because ogre.Math was not wrapped correctly
        #if(ogre.Math.RealEqual(self.phi, 2.0 * ogre.Math.PI, 0.0001)):
            #self.phi = 0.0
        self.theta = math.atan2(pos.y, pos.x)
        if(self.theta < 0.0):
            self.theta += ogre.Math.PI
      
        cos = ogre.Math.Cos
        sin = ogre.Math.Sin
        self.ru = ogre.Vector3(self.r * cos(self.phi) * cos(self.theta), self.r * cos(self.phi) * sin(self.theta), -self.r * sin(self.phi))
        self.rv = ogre.Vector3(-self.r * sin(self.phi) * sin(self.theta), self.r * sin(self.phi) * cos(self.theta), 0)
        self.ru.normalise()
        self.rv.normalise()
        self.normal = self.ru.crossProduct(self.rv)     
        self.normal.normalise()
        self.r = self.sphere[1] #reproject onto the initial space. Well I'm doing it this way is because I want to work in R^3 instead of in uv space.
        self.pos = ogre.Vector3(self.r * cos(self.theta) * sin(self.phi), self.r * sin(self.theta) * sin(self.phi), self.r * cos(self.phi))
        
        print "pos: ", self.pos
        print "theta: ", self.theta
        print "phi: ", self.phi

class Planet:
    def __init__(self, node, radius):
        self.node = node
        self.radius = radius

class WorldController:
    def __init__(self, scnMgr, entityController, camera):
        
        self.scnMgr = scnMgr
        globalNode = scnMgr.getRootSceneNode().createChildSceneNode()
        self.globalNode = globalNode
        self.planets = []
        self.camera = camera
        self.entityController = entityController
    
    def loadEntities(self):
        
        numOfEnts = 200
        for i in range(numOfEnts):
            tangentBundle = TangentBundle([self.homePlanet[0], self.homePlanet[1] * 1.2])
            entity = self.entityController.createEntity(self.scnMgr, tangentBundle)
            theta = random.uniform(0, 2.0 * ogre.Math.PI)
            phi = random.uniform(-ogre.Math.PI / 2, ogre.Math.PI / 2)
            rotTheta = ogre.Quaternion(ogre.Radian(theta), ogre.Vector3(0.0, 1.0, 0.0))
            rotPhi = ogre.Quaternion(ogre.Radian(phi), ogre.Vector3(1.0, 0.0, 0.0))
            orient = rotPhi * rotTheta
            entNode = entity.sceneNode
            #orient = entNode.getOrientation()
            planetNode = self.homePlanet[0]
            scale = self.homePlanet[1]
            pos = planetNode._getDerivedPosition()
            entNode.setPosition(pos + orient.yAxis() * scale * 1.2)
            entNode.setOrientation(orient)
    
    def loadPlayer(self, pageCoords):
        
        #pick a random planet
        randPlanetId = random.randint(0, len(self.planets) - 1)
        planet = self.planets[randPlanetId]
        self.homePlanet = planet
        
        tangentBundle = TangentBundle([self.homePlanet[0], self.homePlanet[1] * 1.2])
        entity = self.entityController.createEntity(self.scnMgr, tangentBundle)
        theta = random.uniform(0, 2.0 * ogre.Math.PI)
        
        entNode = entity.sceneNode
        orient = entNode.getOrientation()
        
        planetNode = self.homePlanet[0]
        scale = self.homePlanet[1]
        pos = planetNode._getDerivedPosition()
        entNode.setPosition(pos + orient.yAxis() * scale * 1.2)
        
        #entNode.attachObject(self.camera)
        #self.camera.setPosition(playerNode.getPosition() + ogre.Vector3(0.0, 25.0, 0.0))
        #self.camera.setAutoTracking(True, entNode)
        
        
    def onUpdate(self, dt):
        self.entityController.onUpdate(dt)   
         
    def onPageLoad(self, pageCoords):  
        self.loadPlanets(pageCoords)  
        self.loadPlayer(pageCoords)
        self.loadEntities()
        
        
    def loadPlanets(self, pageCoords):
        #create spheres
        numOfSpheres = 50
        
        
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
        mat = ogre.MaterialManager.getSingleton().getByName("GridNormalMap").setReceiveShadows(True)
        
        bb = ent.getMesh().getBoundingSphereRadius()
        scaleSphere = 1.0 / bb * scale
        print "radius: ", bb
        node = self.globalNode.createChildSceneNode()
        node.attachObject(ent)
        node.setPosition(pos)
        #rad = ogre.Degree(random.randrange(0.0, 120.0)).valueRadians()
        #tempOrient = ogre.Quaternion(ogre.Radian(rad), ogre.Vector3(1.0, 0.0, 0.0))
        #node.setOrientation(tempOrient)
        node.setScale(scaleSphere, scaleSphere, scaleSphere)
        self.planets.append((node, scale))
        
            
                                    
        
        
        
        
        