"""macOS CoreMIDI virtual-port bridge via ctypes (stdlib only, no deps).

Creates a virtual MIDI *source* (e.g. "LaunchpadMK2Bridge") that appears
system-wide in every CoreMIDI client — including Mixxx, which lists it as a
MIDI input device. The emulator sends bridge messages (notes for buttons,
CCs for continuous values) into Mixxx through this port.

Why ctypes and not python-rtmidi: no compiler/conda feed needed, zero new
dependencies, and we only need MIDI *output* (the emulator GUI *is* the
input device).
"""
import ctypes
import ctypes.util

_core = ctypes.CDLL("/System/Library/Frameworks/CoreMIDI.framework/CoreMIDI")
_cf = ctypes.CDLL("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")

_OSStatus = ctypes.c_int32
_MIDIClient = ctypes.c_void_p
_MIDIEndpoint = ctypes.c_uint32
_kCFStringEncodingUTF8 = 0x08000100


def _cfstr(text: str):
    _cf.CFStringCreateWithCString.restype = ctypes.c_void_p
    _cf.CFStringCreateWithCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32]
    return _cf.CFStringCreateWithCString(None, text.encode("utf-8"), _kCFStringEncodingUTF8)


class _Packet(ctypes.Structure):
    _fields_ = [("timestamp", ctypes.c_uint64),
                ("length", ctypes.c_uint16),
                ("data", ctypes.c_ubyte * 256)]


class _PacketList(ctypes.Structure):
    _fields_ = [("numPackets", ctypes.c_uint32),
                ("packet", _Packet)]


_core.MIDIClientCreate.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
                                   ctypes.POINTER(_MIDIClient)]
_core.MIDIClientCreate.restype = _OSStatus
_core.MIDISourceCreate.argtypes = [_MIDIClient, ctypes.c_void_p, ctypes.POINTER(_MIDIEndpoint)]
_core.MIDISourceCreate.restype = _OSStatus
_core.MIDIReceived.argtypes = [_MIDIEndpoint, ctypes.POINTER(_PacketList)]
_core.MIDIReceived.restype = _OSStatus
_core.MIDIEndpointDispose.argtypes = [_MIDIEndpoint]
_core.MIDIClientDispose.argtypes = [_MIDIClient]
_core.MIDIGetNumberOfSources.restype = ctypes.c_int
_core.MIDIGetSource.argtypes = [ctypes.c_int]
_core.MIDIGetSource.restype = _MIDIEndpoint
_core.MIDIObjectGetStringProperty.argtypes = [_MIDIEndpoint, ctypes.c_void_p,
                                              ctypes.POINTER(ctypes.c_void_p)]
_core.MIDIObjectGetStringProperty.restype = _OSStatus
_cf.CFStringGetCString.restype = ctypes.c_bool
_cf.CFStringGetCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_long, ctypes.c_uint32]


def list_sources() -> list:
    """Display names of all CoreMIDI sources visible system-wide."""
    names = []
    for i in range(_core.MIDIGetNumberOfSources()):
        ep = _core.MIDIGetSource(i)
        out = ctypes.c_void_p()
        if _core.MIDIObjectGetStringProperty(ep, _cfstr("displayName"), ctypes.byref(out)) == 0 and out.value:
            buf = ctypes.create_string_buffer(256)
            _cf.CFStringGetCString(out.value, buf, 256, _kCFStringEncodingUTF8)
            names.append(buf.value.decode("utf-8", "replace"))
    return names


class VirtualMidiPort:
    """A virtual MIDI source Mixxx can open as a controller input."""

    def __init__(self, name: str = "LaunchpadMK2Bridge"):
        self.name = name
        client = _MIDIClient()
        st = _core.MIDIClientCreate(_cfstr(name), None, None, ctypes.byref(client))
        if st != 0:
            raise RuntimeError(f"MIDIClientCreate failed: {st}")
        ep = _MIDIEndpoint()
        st = _core.MIDISourceCreate(client, _cfstr(name), ctypes.byref(ep))
        if st != 0:
            raise RuntimeError(f"MIDISourceCreate failed: {st}")
        self._client, self._endpoint = client, ep

    def send(self, status: int, data1: int, data2: int):
        pl = _PacketList()
        pl.numPackets = 1
        pl.packet.timestamp = 0  # now
        pl.packet.length = 3
        pl.packet.data[0], pl.packet.data[1], pl.packet.data[2] = status, data1, data2
        st = _core.MIDIReceived(self._endpoint, ctypes.byref(pl))
        if st != 0:
            raise RuntimeError(f"MIDIReceived failed: {st}")

    def send_note(self, channel: int, note: int, velocity: int):
        self.send(0x90 | (channel & 0x0F), note & 0x7F, velocity & 0x7F)

    def send_cc(self, channel: int, cc: int, value: int):
        self.send(0xB0 | (channel & 0x0F), cc & 0x7F, value & 0x7F)

    def close(self):
        _core.MIDIEndpointDispose(self._endpoint)
        _core.MIDIClientDispose(self._client)


if __name__ == "__main__":
    port = VirtualMidiPort("LaunchpadMK2Bridge")
    print("port created; visible sources:")
    for n in list_sources():
        print("  -", n)
    assert "LaunchpadMK2Bridge" in list_sources(), "virtual port NOT visible!"
    port.send_cc(0, 0x10, 64)
    port.send_note(0, 0x30, 127)
    port.send_note(0, 0x30, 0)
    print("send OK (cc + note on/off)")
    port.close()
    print("closed OK")
