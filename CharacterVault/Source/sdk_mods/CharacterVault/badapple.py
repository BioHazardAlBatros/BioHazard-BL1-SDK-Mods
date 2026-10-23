import unrealsdk
import os
import struct
import ctypes
from unrealsdk import logging
from unrealsdk.unreal import UObject, WrappedStruct
from typing import Tuple, Optional
from mods_base import get_pc, ENGINE
from .api import get_asset_path

#BadApple Test
SoundNodeWave = unrealsdk.find_class("SoundNodeWave")
SoundCue = unrealsdk.find_class("SoundCue")
SoundNode = unrealsdk.find_class("SoundNode")
AudioComponent = unrealsdk.find_class("AudioComponent")
EDecompressionType = unrealsdk.find_enum("EDecompressionType")
EAudioStreamType = unrealsdk.find_enum("EAudioStreamType")
ESoundClassName = unrealsdk.find_enum("ESoundClassName")
ASType = unrealsdk.find_enum("ASType")

_cached_cue = None
_cached_wave = None
_bulk_buffer = None
_cached_audio_component = None

def parse_wav(file_path: str) -> Tuple[bytes, int, int, int, float]:
    with open(file_path, 'rb') as f:
        data = f.read()

    pos = 0
    sample_rate = 0
    num_channels = 0
    last_granule = 0
    found_id = False

    while pos < len(data):
        if data[pos:pos+4] != b'OggS':
            next_ogg = data.find(b'OggS', pos)
            if next_ogg == -1:
                break
            pos = next_ogg
            continue

        granule = int.from_bytes(data[pos+6:pos+14], 'little')
        if granule > last_granule:
            last_granule = granule

        num_segments = data[pos+26]
        segment_table_start = pos + 27
        segment_table = data[segment_table_start:segment_table_start+num_segments]
        total_seg_len = sum(segment_table)
        payload_start = segment_table_start + num_segments
        payload = data[payload_start:payload_start+total_seg_len]

        if not found_id:
            sig = b'\x01vorbis'
            idx = payload.find(sig)
            if idx != -1 and len(payload) >= idx + 16:
                num_channels = payload[idx+11]
                sample_rate = int.from_bytes(payload[idx+12:idx+16], 'little')
                found_id = True

        pos = payload_start + total_seg_len

    if not found_id:
        raise ValueError("No Vorbis identification header found in OGG file")

    duration = last_granule / sample_rate if sample_rate > 0 else 0.0
    return data, sample_rate, num_channels, 0, duration

def find_first_sound_node_wave(node: Optional[SoundNode]) -> Optional[SoundNodeWave]:
    if node is None:
        return None
    if node.Class.Name == "SoundNodeWave":
        return node
    if hasattr(node, 'ChildNodes'):
        for child in node.ChildNodes:
            result = find_first_sound_node_wave(child)
            if result:
                return result
    return None

def create_bulk_data_from_bytes(data: bytes):
    global _bulk_buffer
    _bulk_buffer = ctypes.create_string_buffer(data)
    addr = ctypes.addressof(_bulk_buffer)

    null_ptr = unrealsdk.make_struct("Pointer")
    null_ptr.Dummy = 0

    data_ptr = unrealsdk.make_struct("Pointer")
    data_ptr.Dummy = addr

    bulk = unrealsdk.make_struct("UntypedBulkData_Mirror")
    bulk.VfTable = null_ptr
    bulk.BulkDataFlags = 8
    bulk.ElementCount = len(data)
    bulk.BulkDataOffsetInFile = 0
    bulk.BulkDataSizeOnDisk = len(data)
    bulk.SavedBulkDataFlags = 0
    bulk.SavedElementCount = 0
    bulk.SavedBulkDataOffsetInFile = 0
    bulk.SavedBulkDataSizeOnDisk = 0
    bulk.BulkData = data_ptr
    bulk.LockStatus = 0
    bulk.AttachedAr = null_ptr
    bulk.bShouldFreeOnEmpty = 0
    return bulk

def init_sound_cue(file_path: str) -> bool:
    global _cached_cue, _cached_wave
    if _cached_cue is not None:
        return True

    pcm_data, sample_rate, num_channels, _, duration = parse_wav(file_path)
    logging.info(f"OGG: {num_channels}ch, {sample_rate}Hz, {duration:.2f}s")

    template_cue = ENGINE.DynamicLoadObject("Interface.User_Interface.UI_BackCue", SoundCue, False)
    template_wave = find_first_sound_node_wave(template_cue.FirstNode)

    transient_pkg = unrealsdk.find_object("Package", "Transient")
    if transient_pkg is None:
        logging.info("Transient package not found, using None")
        transient_pkg = None

    wave = unrealsdk.construct_object("SoundNodeWave", transient_pkg, "MySoundWave", 0x4000, template_wave)
    cue = unrealsdk.construct_object("SoundCue", transient_pkg, "MySoundCue", 0x4000, template_cue)

    bulk_data = create_bulk_data_from_bytes(pcm_data)
    template_bulk = template_wave.RawData
    #if template_bulk is not None and hasattr(template_bulk, 'VfTable'):
    #    bulk_data.VfTable.Dummy = template_bulk.VfTable.Dummy

    wave.NumChannels = num_channels
    wave.SampleRate = sample_rate
    wave.Duration = duration
    wave.DecompressionType = EDecompressionType.DTYPE_RealTime
    wave.bForceRealTimeDecompression = True
    wave.bLoopingSound = False
    wave.CompressionQuality = 0
    wave.StreamingType = EAudioStreamType.ASTYPE_RealTime
    wave.StreamBufferSize = 0
    wave.Volume = 1.0

    wave.RawData = bulk_data
    cue.FirstNode = wave
    cue.VolumeMultiplier = 1.0
    cue.PitchMultiplier = 1.0

    _cached_wave = wave
    _cached_cue = cue
    return True

def play_cached_sound() -> None:
    global _cached_audio_component
    if _cached_cue is None:
        if not init_sound_cue(get_asset_path("badapple.ogg")):
            logging.info("fck")
            return

    pc = get_pc()
    if pc is None:
        return

    if _cached_audio_component is None:
        audio_comp = unrealsdk.construct_object("AudioComponent", None, "MyMusicComponent", 0x4000)
        if audio_comp is None:
            logging.info("Failed to create AudioComponent")
            return
        _cached_audio_component = audio_comp

    audio_comp = _cached_audio_component
    audio_comp.SoundCue = _cached_cue
    audio_comp.bAutoPlay = True
    audio_comp.bStopWhenOwnerDestroyed = True
    audio_comp.bIsMusic = True
    audio_comp.bIsUISound = False
    audio_comp.bIsDialog = False
    audio_comp.bIsAmbience = False
    audio_comp.VolumeMultiplier = 1.0
    audio_comp.PitchMultiplier = 1.0
    audio_comp.Location = pc.Location
    audio_comp.Play()
    logging.info("AudioComponent (Music) Play() called")

def create_empty_movie_clip(hud: UObject, movie_path : str, name : str, depth: int):
    invoker = WrappedStruct(hud.Invoke.func)
    invoker.Method = f"{movie_path}.createEmptyMovieClip"
    invoker.args.emplace_struct(Type=ASType.AS_String, S=name)
    invoker.args.emplace_struct(Type=ASType.AS_Number, N=depth)
    hud.Invoke(invoker)

def duplicate_movie_clip(hud: UObject, movie_path : str, name : str, depth: int):
    invoker = WrappedStruct(hud.Invoke.func)
    invoker.Method = f"{movie_path}.duplicateMovieClip"
    invoker.args.emplace_struct(Type=ASType.AS_String, S=name)
    invoker.args.emplace_struct(Type=ASType.AS_Number, N=depth)
    hud.Invoke(invoker)

def attach_movie(hud: UObject, movie_path : str, export_name : str, name : str, depth: int):
    invoker = WrappedStruct(hud.Invoke.func)
    invoker.Method = f"{movie_path}.attachMovie"
    invoker.args.emplace_struct(Type=ASType.AS_String, S=export_name)
    invoker.args.emplace_struct(Type=ASType.AS_String, S=name)
    invoker.args.emplace_struct(Type=ASType.AS_Number, N=depth)
    hud.Invoke(invoker)

def load_movie(hud: UObject, movie_path : str, asset : str):
    hud.SingleArgInvokeS(f"{movie_path}.loadMovie",asset_path)

def load_custom_movie(hud: UObject, asset : str, movie_path : str, name : str, depth: int):
    asset_path = get_asset_path(asset)
    invoker = WrappedStruct(hud.Invoke.func)
    invoker.Method = f"{movie_path}.createEmptyMovieClip"
    invoker.args.emplace_struct(Type=ASType.AS_String, S=name)
    invoker.args.emplace_struct(Type=ASType.AS_Number, N=depth)
    hud.Invoke(invoker)
    hud.SingleArgInvokeS(f"{movie_path}.{name}.loadMovie",asset_path)
    invoker = WrappedStruct(hud.Invoke.func)
    invoker.Method = f"{movie_path}.{name}.gotoAndPlay"
    hud.Invoke(invoker)

def load_custom_icon(hud: UObject, asset : str, movie_path : str):
    asset_path = get_asset_path(asset)
    hud.SingleArgInvokeS(f"{movie_path}.loadMovie", asset_path)
    hud.SingleArgInvokeS(f"{movie_path}.gotoAndStop", "ready")

def invoke_apple(hud: UObject):
    invoker = WrappedStruct(hud.Invoke.func)
    invoker.Method = f"_root.badapple.createApple"
    hud.Invoke(invoker)

def hide_apple(hud: UObject):
    invoker = WrappedStruct(hud.Invoke.func)
    invoker.Method = f"_root.badapple.setAppleVisible"
    hud.Invoke(invoker)


def reload_apple(hud: UObject):
    load_custom_movie(hud, "badapple.swf", "_root","badapple",9999)

def ShowApple(HUD):
    #load_custom_icon(HUD, "HUDBL2.swf", "p1")
    #get_pc().PlaySound(_cached_cue)
    #manually get lyrics starting from 3rd minute
    #return
    if HUD.GetVariableString("_root.badapple") == "_level0.badapple" and HUD.GetVariableBool("p1.character._visible") is True:
        invoke_apple(HUD)
    else:
        reload_apple(HUD)

def HideApple(obj, args, ret, func):
    return
    pc = get_pc()
    if pc is None:
        return;
    hide_apple(pc.MyHud.HUDMovie)

