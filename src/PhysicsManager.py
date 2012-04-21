"""This modules defines all functions pertaining to physics"""

import ogre.renderer.OGRE as ogre

import ogre.physics.bullet as bullet
import ogre.physics.OgreBulletC as collisions
import ogre.physics.OgreBulletD as dynamics

class OgreMotionState(bullet.btMotionState): 
    def __init__(self, initalPosition, node): 
        bullet.btMotionState.__init__(self)
        self.Pos=initalPosition 
        self.Position=ogre.Vector3() 
        self.Quaternion=ogre.Quaternion() 
        self.node = node
    def getWorldTransform(self, WorldTrans): 
        WorldTrans.setOrigin(self.Pos.getOrigin())
        WorldTrans.setBasis(self.Pos.getBasis())
        
    def setWorldTransform(self, WorldTrans):
        #print "setWorldTrans", WorldTrans 
        self.Position=ogre.Vector3(WorldTrans.getOrigin().x(),WorldTrans.getOrigin().y(),WorldTrans.getOrigin().z()) 
        self.Quaternion=ogre.Quaternion(WorldTrans.getRotation().w(),WorldTrans.getRotation().x(),WorldTrans.getRotation().y(),WorldTrans.getRotation().z()) 
     
        self.node.setPosition(self.Position)
        self.node.setOrientation(self.Quaternion)
        
        
        #print "setWorldTrans", WorldTrans 

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
        self.world.setGravity(bullet.btVector3(0, -10, 0))
        
        self.bodies = []
        self.shapes = []
        self.cubes = []
        self.motionStates = []
        self.elapsedTime = 0.0
        self.duration = 10.0
        return None
    
    def __del__(self):
        del self.world
        for i in self.shapes:
            del i
        for i in self.bodies:
            del i
        
        
    
    def createWorldRep(self):
        #create a ground plane.
        
        """
        groundShape = collisions.StaticPlaneCollisionShape(ogre.Vector3(0, 1, 0), 0)
        groundBody = dynamics.RigidBody("GroundPlane", self.world)
        groundBody.setStaticShape(groundShape, 0.1, 0.8)
        """
        groundShape = bullet.btStaticPlaneShape(bullet.btVector3(0.0, 1.0, 0.0), 0.0)
        groundMotionState = bullet.btDefaultMotionState(bullet.btTransform(bullet.btQuaternion(0, 0, 0, 1), bullet.btVector3(0, 0, 0)))
        
        groundBodyCI = bullet.btRigidBody.btRigidBodyConstructionInfo(0, groundMotionState, groundShape, bullet.btVector3(0, 0, 0))
        groundBody = bullet.btRigidBody(groundBodyCI)
        
        self.world.addRigidBody(groundBody)
        
        self.shapes.append(groundShape)
        self.bodies.append(groundBody)
        self.motionStates.append(groundMotionState)
        
        #self.world.getDispatchInfo().m_enableSPU = True
        
        #create cubes
        startY = 1.0
        startX = -8.0
        dx = 1.0
        dy = 1.0
        numOfCubes = 50
        for i in range(0, numOfCubes):
            pos = ogre.Vector3(startX + i * dx, startY + i * dy, -15.0)
            self.cubes.append(self._addCube(pos))
        self.startY = startY
        self.startX = startX
        self.dx = dx
        self.dy = dy
        
    
    def createSphere(self, pos):
        
        return None
        
    def _addCube(self, pos, cubeBounds=ogre.Vector3(0.3, 0.3, 0.3)):
        #cubeBounds=bullet.btVector3(0.3, 0.3, 0.3)):
        ent = self.sceneManager.createEntity("Bulletbox.mesh")
        ent.setMaterialName("TronNormalMap")
        node = self.sceneManager.getRootSceneNode().createChildSceneNode()
        node.attachObject(ent)
        node.scale(cubeBounds)
        #node.scale(cubeBounds.getX(), cubeBounds.getY(), cubeBounds.getZ())
        mass = 1.0
        res = 0.1
        bodyFriction = 0.8
        fallInertia = bullet.btVector3(0, 0, 0)
        cubeIdx = len(self.bodies)
        
        cubeShape = bullet.btBoxShape(collisions.OgreBtConverter.to(cubeBounds))
        cubeShape.calculateLocalInertia(mass, fallInertia)
        cubeMotionState = OgreMotionState(bullet.btTransform(bullet.btQuaternion(0, 0, 0, 1), bullet.btVector3(pos.x, pos.y, pos.z)), node)
        cubeBodyCI = bullet.btRigidBody.btRigidBodyConstructionInfo(mass, cubeMotionState, cubeShape, fallInertia)
        cubeBody = bullet.btRigidBody(cubeBodyCI)
        cubeBody.setActivationState(4) #state is never deactivate
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
        """
        cubeShape = bullet.btBoxShape(cubeBounds)
        cubeShape.calculateLocalInertia(mass, fallInertia)
        cubeMotionState = OgreMotionState(bullet.btTransform(bullet.btQuaternion(0, 0, 0, 1), bullet.btVector3(pos.x, pos.y, pos.z)), node)
        cubeBodyCI = bullet.btRigidBody.btRigidBodyConstructionInfo(mass, cubeMotionState, cubeShape, fallInertia)
        cubeBody = bullet.btRigidBody(cubeBodyCI)
        self.world.addRigidBody(cubeBody)
        
        self.motionStates.append(cubeMotionState)
        self.shapes.append(cubeShape)
        self.bodies.append(cubeBody)
        """
        
    def createHenchmen(self, pos, cubeBounds):
        
        cubeBody = self._addCube(pos + ogre.Vector3(0.0, 1.5, 0.0), cubeBounds)
        return cubeBody
    
    def update(self, dt):
        
        if(self.elapsedTime > self.duration):
            self.elapsedTime = 0.0
            for i in range(0, len(self.cubes)):
                pos = ogre.Vector3(self.startX + i * self.dx, self.startY + i * self.dy, -15.0 - i * self.dx)
                cube = self.cubes[i]
                transform = bullet.btTransform()
                transform.setOrigin(bullet.btVector3(pos.x, pos.y, pos.z))
                #cube.getBulletRigidBody().setWorldTransform(transform)
                cube.setWorldTransform(transform)
        self.elapsedTime += dt
        self.world.stepSimulation(dt, 10)
        
        
        
        return None