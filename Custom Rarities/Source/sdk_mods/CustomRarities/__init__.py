import unrealsdk, json
from unrealsdk.hooks import Type
from mods_base import ENGINE, build_mod, NestedOption, GroupedOption, SliderOption, SpinnerOption, ButtonOption, SETTINGS_DIR, get_pc, keybind, EInputEvent,hook
from .rarities import DROP_ShortLived, DROP_LongLived, DROP_LiveForever, ModifiedRarities, VanillaRarities, Rarity

def ByteFromInt(ColorHex: int, ByteIndex: int) -> int:
    return (ColorHex >> (ByteIndex * 8)) & 0xFF

def MakeColor(ColorHex: int):
    return unrealsdk.make_struct("Color", B=ByteFromInt(ColorHex, 0), G=ByteFromInt(ColorHex, 1), R=ByteFromInt(ColorHex, 2), A=ByteFromInt(ColorHex, 3))

def MakeRarity(newRarity: Rarity):
    return unrealsdk.make_struct("RarityLevelColor", MinLevel=newRarity.MinLevel, MaxLevel=newRarity.MaxLevel, Color=MakeColor(newRarity.Color), DropLifeSpanType=newRarity.DropLifeSpanType)

def GetRarityArray():
    return ENGINE.DynamicLoadObject("gd_globals.General.Globals", unrealsdk.find_class("GlobalsDefinition"), False).RarityLevelColors

def ReplaceRarities(newRarities: list[Rarity]):
    arr = GetRarityArray()
    arr.clear()
    for rarityInfo in newRarities:
        arr.append(MakeRarity(rarityInfo))

LIFESPAN_NAMES = {DROP_ShortLived: "ShortLived", DROP_LongLived: "LongLived", DROP_LiveForever: "LiveForever"}
LIFESPAN_VALUES = {v: k for k, v in LIFESPAN_NAMES.items()}

def patchRarityByIndex(index: int, group: GroupedOption):
    minLvl = group.children[0].value
    maxLvl = group.children[1].value
    a = int(group.children[2].value)
    r = int(group.children[3].value)
    g = int(group.children[4].value)
    b = int(group.children[5].value)
    colorInt = (a << 24) | (r << 16) | (g << 8) | b
    lifespanEnum = LIFESPAN_VALUES[group.children[6].value]
    
    arr = GetRarityArray()
    if index >= len(arr):
        return
    arr[index].MinLevel = int(minLvl)
    arr[index].MaxLevel = int(maxLvl)
    arr[index].Color = MakeColor(colorInt)
    arr[index].DropLifeSpanType = int(lifespanEnum)

def ChangePauseVisibility():
    pc = get_pc(possibly_loading=True)
    if pc is None:
        return
    manager = pc.GFxUIManager
    if manager is None:
        return
    if len(manager.ScreenMovies) > 0:
        manager.ScreenMovies[0].bRenderingDisabled = not manager.ScreenMovies[0].bRenderingDisabled 

@hook("WillowGame.WillowGFxMenuPause:HandleInputKey", Type.PRE)
def PauseHook(obj, args, ret, func):
    if args.ukey == "F1" and args.uevent == 0:
        ChangePauseVisibility()

def updateColorPreview(a:int, r: int, g: int, b: int):
    pc = get_pc(possibly_loading=True)
    if pc is None:
        return
    hud = pc.myHUD
    if hud is None:
        return
    movie = hud.GetHUDMovie()
    if movie is None:
        return
    movie.CriticalTextMessages[0].MessageArray.clear()
    color = unrealsdk.make_struct("Color", A=a, R=r, G=g, B=b)
    pc.DisplayHUDMessage(1, "COLOR PREVIEW [F1 toggles pause menu]", 0.5, color)

def watameFactory(index: int, group: GroupedOption):
    def on_change(option, value):
        patchRarityByIndex(index, group)
        updateColorPreview(int(group.children[2].value),int(group.children[3].value),int(group.children[4].value),int(group.children[5].value))
    return on_change

def MakeRarityNestedOption(index: int, rarity: Rarity) -> NestedOption:
    a = ByteFromInt(rarity.Color, 3)
    r = ByteFromInt(rarity.Color, 2)
    g = ByteFromInt(rarity.Color, 1)
    b = ByteFromInt(rarity.Color, 0)
    lifespan_name = LIFESPAN_NAMES.get(rarity.DropLifeSpanType, "ShortLived")

    minSlider = SliderOption(identifier="min_level", display_name="Min Level", value=rarity.MinLevel, min_value=-1, max_value=800, step=1, is_integer=True)
    maxSlider = SliderOption(identifier="max_level", display_name="Max Level", value=rarity.MaxLevel, min_value=-1, max_value=800, step=1, is_integer=True)
    alphaSlider = SliderOption(identifier="color_a", display_name="Alpha", value=a, min_value=0, max_value=255, step=1, is_integer=True)
    redSlider = SliderOption(identifier="color_r", display_name="Red", value=r, min_value=0, max_value=255, step=1, is_integer=True)
    greenSlider = SliderOption(identifier="color_g", display_name="Green", value=g, min_value=0, max_value=255, step=1, is_integer=True)
    blueSlider = SliderOption(identifier="color_b", display_name="Blue", value=b, min_value=0, max_value=255, step=1, is_integer=True)
    lifespanSpinner = SpinnerOption(identifier="lifespan", display_name="Drop Lifespan", value=lifespan_name, choices=["ShortLived", "LongLived", "LiveForever"], wrap_enabled=False)
    
    group = NestedOption(
        identifier=f"rarity_{index}", 
        display_name=f"[{index}]", 
        #display_name=f"[{index}] <font color='#{r:02X}{g:02X}{b:02X}'>Preview</font>", 
        children=[minSlider, maxSlider, alphaSlider, redSlider, greenSlider, blueSlider, lifespanSpinner])
    
    changeCallback = watameFactory(index, group)
    for option in group.children:
        option.on_change = changeCallback
    
    return group

def load_settings():
    settings_file = SETTINGS_DIR / "CustomRarities.json"
    if not settings_file.exists():
        return None
    try:
        with open(settings_file, 'r') as f:
            data = json.load(f)
        options = data.get('options', {})
        rarityEd = options.get('rarity_editor', {})
        rarities = []
        for key in sorted(rarityEd.keys(), key=lambda x: int(x.split('_')[1])):
            entry = rarityEd[key]
            minLvl = entry['min_level']
            maxLvl = entry['max_level']
            a = entry['color_a']
            r = entry['color_r']
            g = entry['color_g']
            b = entry['color_b']
            colorInt = (a << 24) | (r << 16) | (g << 8) | b
            lifespanEnum = LIFESPAN_VALUES[entry['lifespan']]
            rarities.append(Rarity(MinLevel=minLvl, MaxLevel=maxLvl, Color=colorInt, DropLifeSpanType=lifespanEnum))
        return rarities
    except:
        return None

LoadedRarities = load_settings()
if LoadedRarities is None:
    LoadedRarities = VanillaRarities

RarityStorage = []
for i, rarityInfo in enumerate(LoadedRarities):
    RarityStorage.append(MakeRarityNestedOption(i, rarityInfo))

RarityEditor = NestedOption(identifier="rarity_editor", display_name="Rarity Editor", children=RarityStorage)

def RebuildOptionMenu(newStorage):
    global RarityStorage, RarityEditor
    RarityStorage = newStorage
    RarityEditor.children = RarityStorage
    PushLiveUpdate()

def PushLiveUpdate():
    storage = []
    for i, group in enumerate(RarityStorage):
        minLvl = group.children[0].value
        maxLvl = group.children[1].value
        a = int(group.children[2].value)
        r = int(group.children[3].value)
        g = int(group.children[4].value)
        b = int(group.children[5].value)
        colorInt = (a << 24) | (r << 16) | (g << 8) | b
        lifespanEnum = LIFESPAN_VALUES[group.children[6].value]
        storage.append(Rarity(MinLevel=minLvl, MaxLevel=maxLvl, Color=colorInt, DropLifeSpanType=lifespanEnum))
    ReplaceRarities(storage)

def ApplyRaritiesCallback(button):
    PushLiveUpdate()

def ResetRaritiesCallback(button):
    newStorage = []
    for i, rarityInfo in enumerate(ModifiedRarities):
        newStorage.append(MakeRarityNestedOption(i, rarityInfo))
    RebuildOptionMenu(newStorage)

def LoadVanillaRaritiesCallback(button):
    newStorage = []
    for i, rarityInfo in enumerate(VanillaRarities):
        newStorage.append(MakeRarityNestedOption(i, rarityInfo))
    RebuildOptionMenu(newStorage)

def AddNewRarityCallback(button):
    newStorage = list(RarityStorage)
    newRarity = Rarity(MinLevel=0, MaxLevel=0, Color=0xFFFFFFFF, DropLifeSpanType=DROP_ShortLived)
    newStorage.append(MakeRarityNestedOption(len(newStorage), newRarity))
    RebuildOptionMenu(newStorage)

def RemoveLastRarityCallback(button):
    if len(RarityStorage) <= 1:
        return
    newStorage = RarityStorage[:-1]
    RebuildOptionMenu(newStorage)

build_mod(
    hooks=[PauseHook],
    options=[
        RarityEditor,
        #ButtonOption(identifier="apply_btn", display_name="Apply Current Rarities", on_press=ApplyRaritiesCallback),
        ButtonOption(identifier="reset_btn", display_name="Reset to Default Modified", on_press=ResetRaritiesCallback),
        ButtonOption(identifier="vanilla_btn", display_name="Load Vanilla Rarities", on_press=LoadVanillaRaritiesCallback),
        ButtonOption(identifier="add_btn", display_name="Add New Rarity", on_press=AddNewRarityCallback),
        ButtonOption(identifier="remove_btn", display_name="Remove Last Rarity", on_press=RemoveLastRarityCallback)
    ],
    on_enable=PushLiveUpdate
)