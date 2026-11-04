# Launchpad × Mixxx — Meta hackathon demo

A narrated 1920×1080, 30 fps animated walkthrough. The pad layouts are extracted from `src/launchpad_mixxx/mapping.py` in the parent project. Waveforms and deck panels are explanatory animation, not recorded Mixxx footage. The video does not claim physical hardware testing.

## Preview

```sh
cd demo-video
npm install
npm run dev -- --no-open
```

Choose **Launchpad-Demo** in Remotion Studio. Each scene also has its own editable composition.

## Voice

Narration uses macOS's built-in **Samantha** voice, generated locally. This is synthetic speech, not OpenAI or ElevenLabs. There is no direct OpenAI speech tool in this chat, and no API key was configured. To regenerate on macOS:

```sh
python3 scripts/make-narration.py
```

Scene lengths are derived from the WAV files, plus a short pause. The text is saved in `src/narration.json`.

## Export when needed

```sh
npx remotion render src/index.ts Launchpad-Demo out/launchpad-mixxx-demo.mp4
```
