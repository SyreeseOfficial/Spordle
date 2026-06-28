import math, os, struct, subprocess, tempfile, threading, wave

_RATE = 22050

def _tone(freqs, dur, vol=0.35):
    n   = int(_RATE * dur)
    buf = bytearray()
    for i in range(n):
        t    = i / _RATE
        fade = 1.0 if i < n * 0.88 else (n - i) / (n * 0.12)
        s    = sum(math.sin(2 * math.pi * f * t) for f in freqs) / len(freqs)
        buf += struct.pack("<h", max(-32767, min(32767, int(s * vol * 32767 * fade))))
    return bytes(buf)

def _play(*notes):
    """Play notes async. Each note: (freq_or_[freqs], duration_sec)."""
    from .utils import SETTINGS
    if not SETTINGS.get("sounds"):
        return

    def run():
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        name = tmp.name
        try:
            frames = b"".join(
                _tone(f if isinstance(f, list) else [f], d) for f, d in notes
            )
            with wave.open(name, "w") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(_RATE)
                wf.writeframes(frames)
            tmp.close()
            for player in (["aplay", "-q", name], ["afplay", name]):
                if subprocess.run(["which", player[0]], capture_output=True).returncode == 0:
                    subprocess.run(player, stderr=subprocess.DEVNULL)
                    break
        except Exception:
            pass
        finally:
            try:
                os.unlink(name)
            except Exception:
                pass

    threading.Thread(target=run, daemon=True).start()

def correct():
    _play((880, 0.1))

def wrong():
    _play(([220, 233], 0.18))   # detuned pair = beating/buzz effect

def milestone(n):
    if   n == 5:  _play((523, 0.09), (659, 0.09), (784, 0.18))
    elif n == 10: _play((523, 0.08), (659, 0.08), (784, 0.08), (1047, 0.22))
    elif n >= 25: _play((523, 0.07), (659, 0.07), (784, 0.07), (1047, 0.07), (1319, 0.28))

def game_over():
    _play((440, 0.14), (370, 0.14), (294, 0.28))   # descending A-F#-D

def navigate():
    _play((523, 0.06))          # clean middle-C click for menu selection

def back():
    _play((370, 0.07))          # lower note, feels like stepping back

def toggle_on():
    _play((440, 0.05), (660, 0.08))   # ascending chirp — switched ON

def toggle_off():
    _play((660, 0.05), (440, 0.08))   # descending chirp — switched OFF
