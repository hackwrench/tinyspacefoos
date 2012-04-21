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

        #self.doc = canvas.Document(sceneManager, self.viewport, "DemoLayout.txt")
        self.doc = None
        sceneManager.setShadowUseInfiniteFarPlane(True)
        
        #setup compositor
        cm = ogre.CompositorManager.getSingleton()
        cm.addCompositor(self.viewport, "Bloom")
        cm.setCompositorEnabled(self.viewport, "Bloom", True)

        self.camera.setFarClipDistance(5000.0)
        self.camera.setNearClipDistance(1.0)
        self.camera.setPosition(0.0, 1.0, -1.1)

        
    def _createFrameListener(self):
        self.frameListener = SkyBoxListener(self.renderWindow, self.camera, self.sceneManager, self)
        self.frameListener.doc = self.doc
        self.root.addFrameListener(self.frameListener)


class SkyBoxListener(sf.FrameListener):
    def __init__(self, renderWindow, camera, sceneManager, app):
        sf.FrameListener.__init__(self, renderWindow, camera)
        self.sceneManager = sceneManager
        self.app=app
        self.lastTime = 0
        self.maxDrawsPerSecond = 1.0/50
        self.animateText = False
        self.totalTime = 0
        self.wireframe= False
        self.worldController = WorldController(self.sceneManager, self.camera)
        
        self.worldController.onPageLoad(ogre.Vector3(0.0, 0.0, 0.0))
        
        self.skyManager = SkyManager(self.sceneManager, self.renderWindow.getViewport(0))
                    
                          
    def frameRenderingQueued(self, frameEvent):
        retVal = True
        if self._isToggleKeyDown(OIS.KC_ESCAPE):
            retVal = False
        
        return retVal

if __name__ == '__main__':
    try:
        application = SkyBoxApplication()
        application.go()
    except ogre.OgreException, e:
        print e
