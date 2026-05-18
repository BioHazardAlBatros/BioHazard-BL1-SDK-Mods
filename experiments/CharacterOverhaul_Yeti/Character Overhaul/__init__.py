import unrealsdk
from mods_base import build_mod
from unrealsdk import logging
from CharacterVault import add_custom_character_class

def on_enable():
    add_custom_character_class("BerserkerRB","Brick Rebalanced","BrickRebalanced.Character.CharacterClass_BrickRB","Slab",3)
    add_custom_character_class("SirenRB","Lilith Rebalanced","LilithRebalanced.Character.CharacterClass_LilithRB","Sup",2)
    add_custom_character_class("HunterRB","Mordecai Rebalanced","MordRebalanced.Character.CharacterClass_MordecaiRB","Birdman",1)
    add_custom_character_class("RolandRB","Roland Rebalanced","RolandRebalanced.Character.CharacterClass_RolandRB","Kevin Hart",0)

build_mod()