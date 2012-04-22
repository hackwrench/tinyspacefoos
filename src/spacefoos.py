# This code is in the Public Domain
# -----------------------------------------------------------------------------
# This source file is part of Python-Ogre
# For the latest info, see http://python-ogre.org/
#
# It is likely based on original code from OGRE and/or PyOgre
# For the latest info, see http://www.ogre3d.org/
#
# You may use this sample code for anything you like, it is not covered by the
# LGPL.
# -----------------------------------------------------------------------------
import sys
import os
sys.path.insert(0,'..')

import ogre.renderer.OGRE as ogre
import SampleFramework as sf
import ogre.gui.canvas as canvas
import ogre.io.OIS as OIS

from SkyManager import SkyManager

from WorldController import (WorldController)
from EntityController import (EntityController)
from PhysicsManager import (PhysicsManager)



from math import *


class SkyBoxApplication(sf.Application):
    def __del__ (self ):
        del self.doc
        sf.Application.__del__(self)
        
    def _setUpResources ( self ):
        # first load the default resources
        sf.Application._setUpResources ( self )
        # Now load any extra resource locations that we might need.. 
        path = os.path.join(os.getcwd(), 'media' ) 
        ogre.ResourceGroupManager.getSingleton().addResourceLocation(path,"FileSystem", "General")

    def _createScene(self):
        sceneManager = self.sceneManager
        sceneManager.ambientLight = ogre.ColourValue(0.5, 0.5, 0.5)
        #sceneManager.setSkyBox(True, "Examples/SpaceSkyBox")
        
        # Need a light 
        light = sceneManager.createLight('MainLight')
        light.setPosition (20, 80, 50)

        self.doc = canvas.Document(sceneManager, self.viewport, "DemoLayout.txt")
        #self.doc = None
        sceneManager.setShadowUseInfiniteFarPlane(True)
        
        #setup compositor
        cm = ogre.CompositorManager.getSingleton()
        cm.addCompositor(self.viewport, "Bloom")
        cm.setCompositorEnabled(self.viewport, "Bloom", True)

        self.camera.setFarClipDistance(5000.0)
        self.camera.setNearClipDistance(0.2)
        self.camera.setPosition(0.0, 1.0, -1.1)
        
        
        self.sceneManager.setShadowTechnique(ogre.SHADOWTYPE_TEXTURE_ADDITIVE)
        
        
        
        
    def _createFrameListener(self):
        self.frameListener = SkyBoxListener(self.renderWindow, self.camera, self.sceneManager, self, self.viewport)
        self.frameListener.doc = self.doc
        self.root.addFrameListener(self.frameListener)
        self.frameListener.showDebugOverlay(False)


class SkyBoxListener(sf.FrameListener):
    def __init__(self, renderWindow, camera, sceneManager, app, viewport):
        sf.FrameListener.__init__(self, renderWindow, camera)
        self.viewport=  viewport
        self.sceneManager = sceneManager
        self.app=app
        self.lastTime = 0
        self.maxDrawsPerSecond = 1.0/50
        self.animateText = False
        self.totalTime = 0
        self.wireframe= False
        
        self.entityController = EntityController()
        self.phyManager = PhysicsManager(self.sceneManager)
        #self.phyManager.createWeaponPool()
        self.worldController = WorldController(self.sceneManager, self.phyManager, self.entityController, self.camera)
        
        self.worldController.onPageLoad(ogre.Vector3(0.0, 0.0, 0.0))
        
        self.skyManager = SkyManager(self.sceneManager, self.renderWindow.getViewport(0))
        self.renderWindow.addListener(self.skyManager.caelumSystem)
        ogre.Root.getSingletonPtr().addFrameListener(self.skyManager.caelumSystem)
        
        self._setupInput()
    
    def _setupInput(self):
        # Initialize OIS.
        windowHnd = self.renderWindow.getCustomAttributeInt("WINDOW")
        self.InputManager = OIS.createPythonInputSystem([("WINDOW", str(windowHnd))])
 
        # Create all devices, only catch joystick exceptions since most people use Key/Mouse.
        self.Keyboard = self.InputManager.createInputObjectKeyboard(OIS.OISKeyboard, self.bufferedKeys)
        self.Mouse = self.InputManager.createInputObjectMouse(OIS.OISMouse, self.bufferedMouse)
        
        
        try:
            self.Joy = self.InputManager.createInputObjectJoyStick(OIS.OISJoyStick, self.bufferedJoy)
        except:
            self.Joy = False
 
        #Set initial mouse clipping size.
        self.windowResized(self.renderWindow)
 
        # Register as a Window listener.
        ogre.WindowEventUtilities.addWindowEventListener(self.renderWindow, self);
    
    def keyPressed(self, frameEvent):
        if self.Keyboard.isKeyDown(OIS.KC_ESCAPE):
            return False             
        
        if self.Keyboard.isKeyDown(OIS.KC_LEFT):
            self.worldController.onKeyDownEvent(OIS.KC_LEFT)
        if self.Keyboard.isKeyDown(OIS.KC_RIGHT):
            self.worldController.onKeyDownEvent(OIS.KC_RIGHT)
        if self.Keyboard.isKeyDown(OIS.KC_UP):
            self.worldController.onKeyDownEvent(OIS.KC_UP)
        if self.Keyboard.isKeyDown(OIS.KC_DOWN):
            self.worldController.onKeyDownEvent(OIS.KC_DOWN)
        if self.Keyboard.isKeyDown(OIS.KC_SPACE):
            self.worldController.onKeyDownEvent(OIS.KC_SPACE)
        if self.Keyboard.isKeyDown(OIS.KC_LSHIFT):
        #if self._isToggleKeyDown(OIS.KC_LSHIFT, 0.1): #why this no work?
            self.worldController.onKeyDownEvent(OIS.KC_LSHIFT)
        
        return True   
                          
    def frameRenderingQueued(self, frameEvent):
        retVal = True
        #cm = ogre.CompositorManager.getSingleton()
        #cm.setCompositorEnabled(self.viewport, "Bloom", False)
        #status = self.app.doc.getElementByName("stats")
        #status.setText("HELLO WORLD")
        
        #self.app.doc.update()
        
        #cm.setCompositorEnabled(self.viewport, "Bloom", True)
        
        self.Keyboard.capture()
        self.Mouse.capture()
        
        if not self.keyPressed(frameEvent):
            return False
       
        self.worldController.onUpdate(frameEvent.timeSinceLastFrame)
        self.phyManager.update(frameEvent.timeSinceLastFrame)
        
        return retVal

if __name__ == '__main__':
    try:
        application = SkyBoxApplication()
        application.go()
    except ogre.OgreException, e:
        print e
