# Technical implementation plan

## Prove the integration first

1. Record the test Mac, macOS version, Mixxx version, and physical Launchpad MK2 identity. Consult the official Novation programmer reference and Mixxx documentation for the exact versions. Record the references with the findings.
2. Capture a press and release from a grid pad and from User 1 and User 2. Identify which device mode exposes those events and allows the app to set dim and bright LEDs. Verify that the physical User buttons remain available when the app owns the LEDs.
3. Send one transport action and one continuous value from the app to live Mixxx. Check whether Mixxx needs its own mapping and how the app can read or reconcile current values before the first step. Test that one physical press yields one Mixxx action.
4. Choose the smallest working transport. A macOS MIDI bridge using Core MIDI and a Mixxx mapping is a candidate. Compare it with an alternative only if the spike exposes a constraint. Record the choice, evidence, setup, and versions under D05 before committing to the stack.

## Proposed boundaries

| Component | Responsibility |
| --- | --- |
| Launchpad endpoint | Discover hardware, decode pad events, and write LED changes. Keep device-specific MIDI values here. |
| Profile router | Turn physical pad events into logical actions for the active profile. Map deck A and B explicitly. Invalidate holds on profile changes. |
| Control engine | Maintain held inputs, apply bounded knob increments using a monotonic clock, and emit one action per binary press. |
| Mixxx endpoint | Map logical actions to verified Mixxx groups and controls. Translate normalized values into each control's supported range and reconcile live state where the chosen integration supports it. |
| LED renderer | Convert profile and press state into color and brightness. Redraw on profile entry and when the device reconnects. |

Route raw input through the profile router before emitting actions. Keep LED output separate from Mixxx input so feedback cannot be routed back as a user action. If live Mixxx values can change outside the controller, prove feedback synchronization or document a bounded policy that prevents an unexpected parameter jump.

## Mapping contract

Maintain a single mapping for profile, pad address, logical control, deck or mixer target, input action, and LED color. Validate that pad addresses are unique within each profile, that both profile selectors stay available, and that logical controls have the required pad counts. Confirm physical capacity before finalizing D02.

## Recovery and delivery

Cancel holds when input ownership changes or a device is lost. On reconnect, rebuild LED state and require fresh presses. Document launch and shutdown order, any required Mixxx mapping installation, how to identify connection problems, and supported versions. Deliver the agreed app format and test it from a clean setup.
