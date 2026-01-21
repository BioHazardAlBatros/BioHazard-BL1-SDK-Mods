import unrealsdk
from mods_base import build_mod, ENGINE
#from unrealsdk import logging

oldPitch = 0 
oldYaw = 0

def patch():
    global oldPitch, oldYaw
    InjuredShared = ENGINE.DynamicLoadObject("gd_PlayerShared.injured.PlayerInjuredDefinition",unrealsdk.find_class("InjuredDefinition"),False) #KEEP_ALIVE flag is not needed since this object is always in memory

    isPostProcessAllowed = not InjuredShared.SinglePlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.bEnableSceneEffect
    InjuredShared.MultiPlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.bEnableSceneEffect = isPostProcessAllowed
    InjuredShared.SinglePlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.bEnableSceneEffect = isPostProcessAllowed
    
    newPitch, newYaw = oldPitch, oldYaw
    oldPitch, oldYaw = InjuredShared.InjuredRotationLean.Pitch, InjuredShared.InjuredRotationLean.Yaw
    InjuredShared.InjuredRotationLean.Pitch = newPitch
    InjuredShared.InjuredRotationLean.Yaw = newYaw

on_enable = patch
on_disable = patch

build_mod()

__version__: str
__version_info__: tuple[int, ...]

#logging.info(f"Comfy FFYL Loaded: {__version__}, {__version_info__}")