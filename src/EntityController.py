import ogre.renderer.OGRE as ogre
import random
import math


class EntityController:
    def __init__(self):
        
        self.ents = []
        
        return None
    
    def createEntity(self, scnMgr, tangentBundle):
        
        playerNode = scnMgr.getRootSceneNode().createChildSceneNode()
        playerEnt = scnMgr.createEntity("RZR-002.mesh")
        playerEnt.setCastShadows(True)
        playerNode.attachObject(playerEnt)
        playerNode.setScale(0.005, 0.005, 0.005)

        entity = Entity(playerNode, tangentBundle)
        entity.rotU = random.uniform(0.0, 2.0 * ogre.Math.PI)
        entity.rotV = random.uniform(0.0, 2.0 * ogre.Math.PI)
        self.ents.append(entity)
        
        return entity
    
    def onUpdate(self, dt):
        for ent in self.ents:
            ent._advance(dt)
    
class Entity: 
    def __init__(self, node, tangentBundle):
        self.sceneNode = node
        self.tangentBundle = tangentBundle
        self.speed = 1.0 / ogre.Math.PI * random.uniform(1.0, 10.0)#angular speed
        self.rotU = 0.0
        self.rotV = 0.0
        self.direction = 1.0
        return None
    
    def getBasisFromDirection(self, side, upVector):
        
        xVec = side.normalisedCopy()
        
        #zVec = upVector.crossProduct(xVec)
        zVec = xVec.crossProduct(upVector)
        if zVec.isZeroLength():
            zVec = ogre.Vector3(0.0, 0.0, 1.0)
            
        zVec.normalise()
        yVec = zVec.crossProduct(xVec)
        yVec.normalise()
        return xVec, yVec, zVec
    
    def _advance(self, dt):
        tangentBundle = self.tangentBundle
        tangentBundle.setPosition(self.sceneNode.getPosition())
        orient = self.sceneNode.getOrientation()
        xVec, yVec, zVec = self.getBasisFromDirection(orient.xAxis(), tangentBundle.normal)
        pos = tangentBundle.newPosition()
        orient = ogre.Quaternion(xVec, yVec, zVec)
        self.sceneNode.setPosition(pos + orient.zAxis() * self.speed * dt)
        self.sceneNode.setOrientation(orient)
            
    def _advance4(self, dt):
        tangentBundle = self.tangentBundle
        tangentBundle.setPosition(self.sceneNode.getPosition())
        pos = self.tangentBundle.newPosition()
        orient = ogre.Quaternion(tangentBundle.ru, tangentBundle.normal, tangentBundle.rv)
        #self.sceneNode.setOrientation(orient)
        #pos = self.sceneNode.getPosition()
        self.sceneNode.setPosition(pos + orient.zAxis() * self.speed * dt) #should use physics engine to do this
        
        
    