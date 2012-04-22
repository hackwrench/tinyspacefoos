import ogre.renderer.OGRE as ogre
import random
import math


class EntityController:
    def __init__(self):
        
        self.ents = []
        
        return None
    
    def createEntity(self, scnMgr, phyMgr, tangentBundle):
        
        playerNode = scnMgr.getRootSceneNode().createChildSceneNode()
        playerEnt = scnMgr.createEntity("RZR-002.mesh")
        playerEnt.setCastShadows(True)
        playerNode.attachObject(playerEnt)
        scale = 0.02
        playerNode.setScale(0.01, 0.02, 0.01)

        #This is not working!!!
        #phyEntity = phyMgr.createGhostObjectEntity(playerNode, scale)
        
        entity = Entity(playerNode, tangentBundle, None)
        entity.rotU = random.uniform(0.0, 2.0 * ogre.Math.PI)
        entity.rotV = random.uniform(0.0, 2.0 * ogre.Math.PI)
        
        #phyEntity.setEntity(entity)
        
        self.ents.append(entity)
        
        
        
        return entity
    
    def onUpdate(self, dt):
        for ent in self.ents:
            ent._advance(dt)


    
class Entity: 
    def __init__(self, node, tangentBundle, phyEntity, isPlayer=False):
        self.sceneNode = node
        self.phyEntity = phyEntity
        self.tangentBundle = tangentBundle
        self.speed = 1.0 / ogre.Math.PI * random.uniform(0.5, 10.0)#angular speed
        self.rotU = 0.0
        self.rotV = 0.0
        self.direction = 1.0
        self.signal = ogre.Vector3(0, 0, 0)
        
        self.timer = ogre.Timer()
        self.weaponCycleTimer = ogre.Timer()
        self.shootDuration = 100
        self.weaponCycleDuration = 1000
        
        self.numberOfWeaponTypes = 3
        self.weaponType = 2
        
        self.isPlayer = isPlayer
        
        return None
    
    def onCollision(self):
        if self.isPlayer:
           print "Plyaer collide" 
    
    def onSignal(self, signal):
        """
        Note, signal components must be independent! left/right maps to x, up/down maps to y.
        """
        self.signal += signal
    
    def onWeaponFire(self, phyMgr, sounds):
        
        if(self.timer.getMilliseconds() > self.shootDuration):
             impulse = self.sceneNode.getOrientation().zAxis()
             
             weaponSelect = self.weaponType % self.numberOfWeaponTypes
             power = 17.0
             if(weaponSelect == 0):
                 sounds[0].play()
                 power = 17.0
             elif weaponSelect == 1:
                 sounds[0].play()
                 power = 10.0
             elif weaponSelect == 2:
                 power = 5.0
                 sounds[1].play()
             
             impulse *= power#7.0
             phyMgr.fireCube(self.sceneNode.getPosition(), impulse)
             self.timer.reset()
             
             
        
        
    def onCycleWeapon(self):
        if (self.weaponCycleTimer.getMilliseconds() > self.weaponCycleDuration):
            self.weaponCycleTimer.reset()
            self.weaponType += 1
        
        
    def getBasisFromDirection(self, side, upVector):
        
        xVec = side.normalisedCopy()
        
        #zVec = upVector.crossProduct(xVec)
        zVec = xVec.crossProduct(upVector)
        if zVec.isZeroLength():
            zVec = ogre.Vector3(0.0, 0.0, 1.0)
            
        zVec.normalise()
        #yVec = zVec.crossProduct(xVec)
        #yVec.normalise()
        yVec = upVector.normalisedCopy()
        return xVec, yVec, zVec
    
    def _advance(self, dt):
        
        #self.phyEntity.updateAction(dt)
        
        tangentBundle = self.tangentBundle
        tangentBundle.setPosition(self.sceneNode.getPosition())
        orient = self.sceneNode.getOrientation()
        xVec, yVec, zVec = self.getBasisFromDirection(orient.xAxis(), tangentBundle.normal)
        pos = tangentBundle.newPosition()
        orient = ogre.Quaternion(xVec, yVec, zVec)
        xAxis = orient.xAxis()
        xAxis *= self.signal.x
        
        self.tangentBundle.changeHeight(self.signal.y, dt)
        
                    
        self.signal = ogre.Vector3(0, 0, 0)
        
        self.sceneNode.setPosition(pos + (orient.zAxis() + xAxis) * self.speed * dt)
        self.sceneNode.setOrientation(orient)
            
    def _advance4(self, dt):
        tangentBundle = self.tangentBundle
        tangentBundle.setPosition(self.sceneNode.getPosition())
        pos = self.tangentBundle.newPosition()
        orient = ogre.Quaternion(tangentBundle.ru, tangentBundle.normal, tangentBundle.rv)
        #self.sceneNode.setOrientation(orient)
        #pos = self.sceneNode.getPosition()
        self.sceneNode.setPosition(pos + orient.zAxis() * self.speed * dt) #should use physics engine to do this
        
        
    