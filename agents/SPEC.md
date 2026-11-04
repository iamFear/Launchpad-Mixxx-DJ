# Product specification

## Goal

A DJ can play a full set in Mixxx on macOS using a single Novation Launchpad MK2 as two CDJ-style decks, a mixer, and effects controls. A custom macOS application handles Launchpad input and LED feedback. The implementation language is open.

## Confirmed requirements

| ID | Requirement |
| --- | --- |
| R01 | Deliver a macOS application that connects the Launchpad MK2 to Mixxx and controls the Launchpad LED patterns. |
| R02 | The physical **User 1** button activates the mixer and effects profile. |
| R03 | The physical **User 2** button activates a single profile containing both decks. |
| R04 | Green means increase and red means decrease for knobs and faders. Yellow means start, stop, or mute where a binary action applies. The documented fader allocation conflicts with this legend. See D01. |
| R05 | A held pad appears bright. After it has been pressed and released, it appears dim in its assigned color. See D03 for initial and re-entry appearance. |
| R06 | A knob occupies three pads (yellow, red, green). A fader occupies two pads (specified as yellow and red, pending D01). A standalone button occupies one yellow pad. |
| R07 | Increasing a knob applies one percentage point per 20 ms. A continuous hold moves from 0% to 100% in 2 seconds. |
| R08 | A DJ can complete a set using both decks, the mixer, and effects through the two profiles. D02 defines the exact controls and how to verify the set. |

## Proposed implementation behavior

- P01. Represent knob values on a normalized 0–100% scale. Start repeat ticks at 20 ms and clamp at 0% and 100%. Apply a symmetric decrease unless D04 specifies otherwise. Cancel pending repeats on release, profile exit, or device loss. Require a fresh press after a profile switch or reconnect.
- P02. Process a yellow pad's mapped binary action once per press. A held yellow pad stays bright and does not repeat the action.
- P03. Use one active input profile at a time. Switching profiles redraws LEDs and preserves Mixxx values. Invalidate outstanding hold events before routing input through the new profile.

## Decisions

| ID | Open question | Resolve before |
| --- | --- | --- |
| D01 | Which color and direction should the two fader pads use? Confirm whether yellow or green means increase and specify the fader's step, hold behavior, and bounds. | Fader mapping and verification |
| D02 | Which exact deck, mixer, and FX controls are required, and which pads own them? Use track selection/loading, play/pause, cue, channel level, crossfade, and FX enable/amount as candidates for a two-track transition. Confirm any required headphone, EQ, sync, or tempo controls. | Layout freeze and release test |
| D03 | What profile is active at launch? What should never-pressed, unused, re-entered, and reconnected pads show? Should binary control state change the LEDs independently of pad press state? | Final LED behavior |
| D04 | Confirm symmetric knob decrease, the behavior of a tap shorter than 20 ms, and which direction wins when both pads are held. | Final knob behavior |
| D05 | Which macOS and Mixxx versions will be supported, how will the app be installed, and which integration route passes the hardware spike? | Packaging and physical acceptance |

The first delivery targets the named hardware, operating system, and DJ software. Other platforms, controller models, standalone audio processing, and visual CDJ replicas are outside the proposed first-delivery scope.

## Project sources

- [Launchpad-Mixxx-DJ project brief](https://app.notion.com/p/40a908a97b328055a242f8cd240aa642)
- [Prepare Knob Functionality Logic](https://app.notion.com/p/40a908a97b328061bef7f5f46b08e975), an in-progress task with no additional specification in its body.
- [GitHub repository](https://github.com/iamFear/Launchpad-Mixxx-DJ)
