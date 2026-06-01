import unrealsdk
from mods_base import build_mod, hook,ENGINE, BoolOption
from unrealsdk.hooks import Type
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction
from unrealsdk import logging
from typing import Any

SaturationOption : BoolOption
BoostFactor = 0.5 # maybe should become an option
def setOnes(obj: UObject):
    dominantColor = min(obj.X, obj.Y, obj.Z)
    obj.X = obj.X + (obj.X - dominantColor) * BoostFactor
    obj.Y = obj.Y + (obj.Y - dominantColor) * BoostFactor
    obj.Z = obj.Z + (obj.Z - dominantColor) * BoostFactor
    return

def changePP(PostProcessEffect : UObject, DesaturationOnly: bool):
    PostProcessEffect.Scene_Desaturation = 0.0
    if DesaturationOnly:
        return
    setOnes(PostProcessEffect.Scene_Highlights)
    setOnes(PostProcessEffect.Scene_MidTones)
    return

def patchAllPP(option: BoolOption, value: bool):
    volumes = unrealsdk.find_all("PostProcessVolume")
    for volume in volumes:
        changePP(volume.Settings, value)

def on_enable():
    ubers = unrealsdk.find_all("UberPostProcessEffect") # does something on some maps, but not main menu
    for uber in ubers:
        uber.SceneDesaturation = 0.0
    patchAllPP(SaturationOption, SaturationOption.value)

@hook(hook_func="WillowGame.WillowGameInfo:PostCommitMapChange", hook_type=Type.POST)
def MapChanged(obj:UObject, args:WrappedStruct, ret:Any, func:BoundFunction) -> Any:
    patchAllPP(SaturationOption, SaturationOption.value)

SaturationOption = BoolOption("Remove desaturation only", True, "Yes", "No", description="With this enabled, only desaturation will be removed. Note: You'll see reverted changes only in the next map.", on_change = patchAllPP )

build_mod(hooks=[MapChanged],options=[SaturationOption])
logging.info(f"Color Enhancer Loaded.")