# OnePlus 6T (*fajita*) Device Support for ztOS

This directory contains device-specific configurations, patched device tree, drivers, and services for running **ztOS** on the OnePlus 6T (Qualcomm Snapdragon 845 / SDM845).

---

## Hardware Support Overview

* **Display**: Native resolution on AMOLED panel at 60 FPS via Freedreno KMS.
* **3D Acceleration**: Vulkan 1.3 via Mesa Turnip (`vulkan-freedreno`) and OpenGL ES 3.1 via Freedreno.
* **Audio**: PipeWire & WirePlumber with full ALSA UCM2 profiles and TFA9894 smart speaker amplifier (`MMITest_48000` profile, mastered system sounds; volume is currently conservative/quiet to prevent distortion and protect the speaker without vendor DSP protection).
* **Touchscreen**: Synaptics multi-touch driver (`s6sy761`).
* **Connectivity**: Wi-Fi (`ath10k_snoc` / `wcn3990`), Bluetooth (`hci0`), and LTE cellular data via `ModemManager`.
* **Power & Battery**: TI `bq27411` fuel gauge and `pmi8998` charger monitoring.
* **Sensors & Haptics**: Accelerometer/gyroscope IIO sensors and SPMI haptic vibration motor.
* **Flashlight**: PM8998 dual-LED torch controlled from Action Center.

---

## Installation & Flashing

> For a complete step-by-step walkthrough covering host setup, cloning, and first boot, see the **[Full Installation Guide (INSTALL.md)](INSTALL.md)**.

### Stage 1: Build Image
From the root of the repository:
```sh
python3 build_fajita.py
```
This builds `out/oneplus-fajita/boot.img` and `out/oneplus-fajita/rootfs.img` completely unprivileged using `fakeroot` and `proot`.

### Stage 2: Enter Fastboot Mode
Reboot your OnePlus 6T into the bootloader (hold Volume Down + Power, or use adb):
```sh
adb reboot bootloader
# Verify connection
fastboot devices
```

### Stage 3: Flash Partitions
```sh
cd out/oneplus-fajita
fastboot flash boot boot.img
fastboot flash userdata rootfs.img
fastboot reboot
```

### Stage 4: Access Device
After ~15 seconds, the phone boots into the `ztmetro` live tile dashboard. Connect via USB Ethernet:
```sh
ssh alarm@172.16.42.1
# Default credentials: user 'alarm', password 'alarm'
```

---

## Known Notes & Quirks

* **Audio Output Level**: Speaker audio is clear and distortion-free, but remains quiet. Software volumes in PipeWire and ztMETRO are strictly capped to 0 dBFS and the TFA9894 amplifier profile uses safe gain to avoid hardware damage until dynamic speaker protection algorithms are implemented.
