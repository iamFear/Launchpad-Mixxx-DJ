"""Generate local, generic female narration with macOS Samantha (no cloud service)."""
import json, subprocess
from pathlib import Path
root = Path(__file__).resolve().parents[1]
segments = [
('intro', 'Turn one Launchpad into a complete DJ setup. Launchpad Mixxx DJ brings two decks, mixing, and effects to a single pad grid.'),
('decks', 'Start in User Two. Deck A is on the left, Deck B on the right. Load and play the first track. Then load, cue, sync, and play the second.'),
('controls', 'The colors explain the controls. Hold green to increase, red to decrease. Yellow triggers one action, or resets a knob to center. Release a pad to stop the change.'),
('transition', 'Ready to mix? Hold the crossfader increase pad to move from Deck A toward Deck B. A full sweep takes about two seconds.'),
('mixer', 'Switch to User One for the mixer and effects. Adjust channel levels, enable an effect, and raise the effects mix. Switching profiles preserves your control values.'),
('outro', 'No Launchpad? Use the on-screen emulator with Mixxx. The bridge sends MIDI commands while Mixxx handles the audio. Your full DJ workflow, on one grid.'),
]
for name, text in segments:
    wav = root / 'public' / f'{name}.wav'
    subprocess.run(['say', '-v', 'Samantha', '-r', '168', '-o', str(wav), '--file-format=WAVE', '--data-format=LEI16@24000', text], check=True)
import wave, math
items = []
for name, text in segments:
    with wave.open(str(root/'public'/f'{name}.wav')) as audio:
        seconds = audio.getnframes()/audio.getframerate()
    items.append({'id': name, 'text': text, 'seconds': seconds, 'frames': math.ceil((seconds + 1.1)*30)})
(root/'src'/'narration.json').write_text(json.dumps(items, indent=2)+'\n')
print(json.dumps(items, indent=2))
