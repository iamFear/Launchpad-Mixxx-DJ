# Acceptance and verification

Record the tested commit, app build, macOS and Mixxx versions, Launchpad model and device mode, mapping revision, date, result, and evidence. Run deterministic checks with fakes first. Run each case's physical portion using the Launchpad MK2 and live Mixxx on macOS.

| Case | Covers | Procedure and expected result |
| --- | --- | --- |
| A01 | R01 | Install and launch from a clean setup using the documented steps. Confirm that the app receives a physical pad event, lights its LED, and sends one intended command to Mixxx. |
| A02 | R02, R03, R08 | Press User 1 and exercise a mixer and an FX control. Press User 2 and exercise one control per deck. Verify that each input changes its intended Mixxx target once and leaves the corresponding inactive-profile targets alone. |
| A03 | R04–R06 | Inspect the mapped grid for knob, fader, and button pad counts. Exercise each control type and compare the color and action to the resolved layout. Verify bright while held and dim after release. Verify initial and profile re-entry states against D03. |
| A04 | R07, P01 | With a fake clock and the knob at 0%, hold increase. Under the proposed tick contract, expect 1% at 20 ms, 50% at 1 s, and 100% at 2 s. Keep holding and check that the value stays at 100%. Verify release cancels future ticks. Verify decrease, brief taps, and opposing pads against D04. Repeat the full sweep with the physical controller and record actual timing and any scheduling variation. |
| A05 | R04, R06, P02 | Verify fader direction, increments, and bounds against D01. Hold each assigned binary action and check for exactly one Mixxx action per press. Release and press again to confirm the action rearms. |
| A06 | R02, R03, P01, P03 | While a knob is repeating, switch profiles or unplug the device. Verify that repeat events stop, delayed releases cannot affect the new profile, Mixxx retains its current values, and reconnect restores LEDs without sending control changes. Verify that a fresh press works afterward. |
| A07 | R01–R03, R08 | Use the final pad map to load and start track A, prepare track B, mix into B, engage and adjust an effect, and continue playback. Demonstrate both profiles and repeat the transition. Use the app setup controls and observe Mixxx for verification. Perform the DJ actions with the Launchpad alone. Include any additional workflows agreed in D02. |

A release requires the applicable physical cases to pass. Report an unavailable device or unresolved product decision as Blocked and identify the affected cases. A fake-clock pass verifies the repeat logic. The hardware run measures the end-to-end response.
