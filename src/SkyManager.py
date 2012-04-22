import ogre.renderer.OGRE as ogre
import ogre.addons.caelum as caelum
import ctypes
class SkyManager:
    def __init__(self, sceneManager, viewport):
        self.sceneManager = sceneManager
        
        
        componentMask = caelum.CaelumSystem.CaelumComponent (
                caelum.CaelumSystem.CAELUM_COMPONENT_SUN |                
                caelum.CaelumSystem.CAELUM_COMPONENT_MOON |
                caelum.CaelumSystem.CAELUM_COMPONENT_SKY_DOME |
                #caelum.CaelumSystem.CAELUM_COMPONENT_IMAGE_STARFIELD |
                caelum.CaelumSystem.CAELUM_COMPONENT_POINT_STARFIELD |
                caelum.CaelumSystem.CAELUM_COMPONENT_CLOUDS |
                caelum.CaelumSystem.CAELUM_COMPONENT_PRECIPITATION
                );
        
        #componentMask = caelum.CaelumSystem.CAELUM_COMPONENTS_DEFAULT
        
        self.caelumSystem = caelum.CaelumSystem(ogre.Root.getSingletonPtr(), self.sceneManager, componentMask)
        self.caelumSystem.attachViewport(viewport)
        
        self.caelumSystem.getUniversalClock().setGregorianDateTime(1999, 06, 06, 0, 0, 0.0)
        
        #self.caelumSystem.autoConfigure(componentMask)
        #self.caelumSystem.setObserverLatitude(ogre.Degree(0))
        #self.caelumSystem.setObserverLongitude(ogre.Degree(0))
        self.caelumSystem.setEnsureSingleLightSource(True)
        self.caelumSystem.getUniversalClock().setTimeScale(500)
        
        dome = self.caelumSystem.getSkyDome()
        
        
        self.caelumSystem.getSkyDome().setHazeEnabled(False)
        
        #self.caelumSystem.setSunLightColour()
        
        
        
        self.caelumSystem.setSceneFogDensityMultiplier(0.0001)
        self.caelumSystem.setManageSceneFog(ogre.FOG_NONE)
        
        sun = self.caelumSystem.getSun()
        sun.getMainLight().setCastShadows(True)
        #sun.setDiffuseMultiplier(ogre.ColourValue(0.01, 0.01, 0.01, 0.01))
        #sun.setLightColour(ogre.ColourValue(0.01, 0.01, 0.01, 0.01))
        #sun.setAmbientMultiplier(ogre.ColourValue(0.01, 0.01, 0.01, 0.01))
        
        moon = self.caelumSystem.getMoon()
        moon.setDiffuseMultiplier(ogre.ColourValue(0.00, 0.00, 0.00, 1.0))
        
        skydome = self.caelumSystem.getSkyDome()
        
        
        self.caelumSystem.setManageAmbientLight(True)
        
        cloud = self.caelumSystem.getCloudSystem().getLayer(0)
        cloud.setCloudCover(0.5)
        cloud.setCloudCoverVisibilityThreshold(0.0)
        cloud.setSunLightColour(ogre.ColourValue(0.0, 0.0, 0.0, 1.0))
        
        #self.caelumSystem.setGroundFog(None)
        
        #precip = caelum.PrecipitationController(self.sceneManager)
        #precip.createViewportInstance(viewport)
        #self.caelumSystem.setPrecipitationController(precip)
        precip = self.caelumSystem.getPrecipitationController()
        
        precip.setPresetType(caelum.PRECTYPE_DRIZZLE)
        #precip.setSpeed(0.001)
        precip.setIntensity(0.7)
        #precip.setAutoDisableThreshold(-1)
        #precip.setAutoCameraSpeed()
        precip.setManualCameraSpeed(ogre.Vector3(0.0, -0.1, -1.0))
        
        
        

        
        