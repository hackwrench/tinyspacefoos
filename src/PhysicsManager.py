"""This modules defines all functions pertaining to physics"""

import ogre.renderer.OGRE as ogre

import ogre.physics.bullet as bullet
import ogre.physics.OgreBulletC as collisions
import ogre.physics.OgreBulletD as dynamics

class OgreMotionState(bullet.btMotionState): 
    def __init__(self, initalPosition, node, tb=None, rb=None): 
        bullet.btMotionState.__init__(self)
        self.Pos=initalPosition 
        self.Position=ogre.Vector3() 
        self.Quaternion=ogre.Quaternion() 
        self.node = node
        self.tb = tb
        self.rb = rb
    def getWorldTransform(self, WorldTrans): 
        WorldTrans.setOrigin(self.Pos.getOrigin())
        WorldTrans.setBasis(self.Pos.getBasis())
        
    def setWorldTransform(self, WorldTrans):
        #print "setWorldTrans", WorldTrans 
        self.Position=ogre.Vector3(WorldTrans.getOrigin().x(),WorldTrans.getOrigin().y(),WorldTrans.getOrigin().z()) 
        self.Quaternion=ogre.Quaternion(WorldTrans.getRotation().w(),WorldTrans.getRotation().x(),WorldTrans.getRotation().y(),WorldTrans.getRotation().z()) 
     
        self.node.setPosition(self.Position)
        self.node.setOrientation(self.Quaternion)
        
        
        if(self.tb is not None):
            self.tb.setPosition(self.Position)
            normal = -self.tb.normal*3000.0 / self.tb.dsqr
            gravity = bullet.btVector3(normal.x, normal.y, normal.z)
            self.rb.setGravity(gravity)           
            self.rb.applyGravity() 
        
        
        
        #print "setWorldTrans", WorldTrans 
class ActionEntity():
    def __init__(self, world, ghostObject, sceneNode):
        self.ghostObject = ghostObject
        self.sceneNode= sceneNode
        self.world = world
    
    def setEntity(self, entity):
        self.entity = entity
        
    def updateAction(self, deltaTime):
        transform = bullet.btTransform()
        pos = self.sceneNode.getPosition()
        
        transform.setOrigin(bullet.btVector3(pos.x, pos.y, pos.z))
        
        self.ghostObject.setWorldTransform(transform)
        
        
        manifoldArray = bullet.btManifoldArray()
        pairArray = self.ghostObject.getOverlappingPairCache().getOverlappingPairArray()
        collision = False
        for i in range(pairArray.size()):
            manifoldArray.clear()
            pair = pairArray[i] 
            collisionPair = self.world.getPairCache().findPair(pair.m_pProxy0, pair.m_pProxy1)
            if collisionPair is None:
                continue
            proxyObject = collisionPair.m_pProxy1.m_clientObject
            if proxyObject == self.target:
                continue
            if (collisionPair.m_algorithm):
                collisionPair.m_algorithm.getAllContactManifolds(manifoldArray)
            
            for j in manifoldArray:
                directionSign = None
                if j.getBody0() == self.ghostObject:
                    directionSign = -1.0
                else:
                    directionSign = 1.0
                for k in range(j.getNumContacts()):
                    pt = j.getContactPoint(k)
                    if pt.getDistance() < 0.0:
                        collision = True
                        
        if collision:
            self.entity.onCollision()
            
    def debugDraw(self, debugDrawer):
        return 

class PhysicsManager:
    """
    A Physics manager class. 
    """
    def __init__(self, sceneManager):
       
        self.sceneManager = sceneManager
        """
        bounds = ogre.AxisAlignedBox(-100.0, -100.0, -100.0, 100.0, 100.0, 100.0)
        self.world = dynamics.DynamicsWorld(self.sceneManager, bounds, ogre.Vector3(0.0, -9.91, 0.0))
        """
        self.collisionConfiguration = bullet.get_btDefaultCollisionConfiguration()
        self.dispatcher = bullet.get_btCollisionDispatcher1(self.collisionConfiguration)
        
        self.broadphase = bullet.btDbvtBroadphase()
        self.solver = bullet.btSequentialImpulseConstraintSolver()
        
        self.world = bullet.btDiscreteDynamicsWorld(self.dispatcher, self.broadphase, self.solver, self.collisionConfiguration)
        self.world.setGravity(bullet.btVector3(0, 0, 0))
        
        self.bodies = []
        self.shapes = []
        self.cubes = []
        self.motionStates = []
        self.elapsedTime = 0.0
        self.duration = 10.0
        
        self.curCubeIdx = 0
        
        self.tangentBundle = None
        
        return None
    
    def __del__(self):
        del self.world
        for i in self.shapes:
            del i
        for i in self.bodies:
            del i
    
    def setTangentBundle(self, bundle):
        self.tangentBundle
        
    def fireCube(self, pos, force):
        cube = self.cubes[(self.curCubeIdx) % len(self.cubes)]
        self.curCubeIdx += 1
        transform = bullet.btTransform()
        transform.setOrigin(bullet.btVector3(pos.x, pos.y, pos.z))
        cube.clearForces()
        cube.setLinearVelocity(bullet.btVector3(0.0, 0.0, 0.0))
        cube.setWorldTransform(transform)
        impulse = bullet.btVector3(force.x, force.y, force.z)
        cube.applyImpulse(impulse, bullet.btVector3(0.0, 0.0, 0.0))
        #cube.applyForce(impulse, bullet.btVector3(0.0, 0.0, 0.0))
            
    def createWeaponPool(self, tb):
        poolNum = 50
        pos = ogre.Vector3(0, 0, 0)
        for i in range(0, poolNum):
            self.cubes.append(self._addCube(pos, ogre.Vector3(0.05, 0.05, 0.05), tangentBundle=tb))    
    
    def createSphere(self, pos, radius, node):
        
        mass = 1.0
        res = 0.1
        bodyFriction = 0.8
        fallInertia = bullet.btVector3(0, 0, 0)
        sphereId = len(self.bodies)
        
        sphereShape = bullet.btSphereShape(radius)
        sphereShape.calculateLocalInertia(mass, fallInertia)
        sphereMotionState = OgreMotionState(bullet.btTransform(bullet.btQuaternion(0, 0, 0, 1), bullet.btVector3(pos.x, pos.y, pos.z)), node)
        sphereBodyCI = bullet.btRigidBody.btRigidBodyConstructionInfo(mass, sphereMotionState, sphereShape, fallInertia)
        sphereBody = bullet.btRigidBody(sphereBodyCI)
        sphereBody.setActivationState(4)
        sphereBody.setCollisionFlags(bullet.btCollisionObject.CF_KINEMATIC_OBJECT)
        self.world.addRigidBody(sphereBody)
        
        self.motionStates.append(sphereMotionState)
        
        self.bodies.append(sphereBody)
        self.shapes.append(sphereShape)
        
        return None
    def createGhostObjectEntity(self, sceneNode, radius):
        
        pos = sceneNode.getPosition()
        transform = bullet.btTransform()
        transform.setIdentity()
        transform.setOrigin(bullet.btVector3(pos.x, pos.y, pos.z))
        
        ghostObject = bullet.btPairCachingGhostObject()
        
        ghostObject.setWorldTransform(transform)
        
        sphereShape = bullet.btSphereShape(1.0)
        
        ghostObject.setCollisionShape(sphereShape)
        #ghostObject.setCollisionFlags(bullet.btCollisionObject.CO_GHOST_OBJECT)
        
        
        
        actionEntity = ActionEntity(self.world, ghostObject, sceneNode)
        
        self.world.addCollisionObject(ghostObject, bullet.btBroadphaseProxy.SensorTrigger, bullet.btBroadphaseProxy.AllFilter)
        #self.world.getBroadphase().getOverlappingPairCache().setInternalGhostPairCallback(bullet.btGhostPairCallback())
        #self.world.addAction(actionEntity)
        
        self.shapes.append(sphereShape)
        
        return actionEntity       
    def _addCube(self, pos, cubeBounds=ogre.Vector3(0.3, 0.3, 0.3), tangentBundle=None):
        #cubeBounds=bullet.btVector3(0.3, 0.3, 0.3)):
        ent = self.sceneManager.createEntity("Bulletbox.mesh")
        ent.setMaterialName("GridNormalMap3")
        node = self.sceneManager.getRootSceneNode().createChildSceneNode()
        node.attachObject(ent)
        node.scale(cubeBounds)
        #node.scale(cubeBounds.getX(), cubeBounds.getY(), cubeBounds.getZ())
        mass = 1.0
        res = 0.01
        bodyFriction = 0.2
        fallInertia = bullet.btVector3(0, 0, 0)
        cubeIdx = len(self.bodies)
        
        cubeShape = bullet.btBoxShape(collisions.OgreBtConverter.to(cubeBounds))
        cubeShape.calculateLocalInertia(mass, fallInertia)
        cubeMotionState = OgreMotionState(bullet.btTransform(bullet.btQuaternion(0, 0, 0, 1), bullet.btVector3(pos.x, pos.y, pos.z)), node, tb=tangentBundle)
        cubeBodyCI = bullet.btRigidBody.btRigidBodyConstructionInfo(mass, cubeMotionState, cubeShape, fallInertia)
        cubeBody = bullet.btRigidBody(cubeBodyCI)
        cubeBody.setActivationState(4) #state is never deactivate
        cubeMotionState.rb = cubeBody
        self.world.addRigidBody(cubeBody)
        
        self.motionStates.append(cubeMotionState)
        
        """
        cubeShape = collisions.BoxCollisionShape(cubeBounds)
        cubeBody = dynamics.RigidBody("cube" + str(cubeIdx), self.world)
        cubeBody.setShape(node, cubeShape, res, bodyFriction, mass, pos)
        cubeBody.getBulletRigidBody().setActivationState(4)
        """
        self.bodies.append(cubeBody)
        self.shapes.append(cubeShape)
        return cubeBody
            
    
    def update(self, dt):
        
        self.world.stepSimulation(dt, 10)
        
        
        return None