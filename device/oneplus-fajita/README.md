# OnePlus 6T (*fajita*) Device Support for ztOS

This directory contains device-specific configurations, patched device tree, drivers, and services for running **ztOS** on the OnePlus 6T (Qualcomm Snapdragon 845 / SDM845).

---

## Hardware Support Overview

* **Display**: Native resolution on AMOLED panel at 60 FPS via Freedreno KMS.
* **Touchscreen**: Synaptics `s6sy761` multi-touch driver.
* **Connectivity**: Wi-Fi (`ath10k_snoc` / `wcn3990`), Bluetooth (`hci0`), and LTE cellular data via `ModemManager`.
* **Power & Battery**: TI `bq27411` fuel gauge and `pmi8998` charger monitoring.
* **Sensors & Haptics**: Accelerometer/gyroscope IIO sensors and SPMI haptic vibration motor.
* **Flashlight**: PM8998 dual-LED torch controlled from Action Center.
* **3D Acceleration**: Vulkan 1.3 via Mesa Turnip (`vulkan-freedreno`).

---

## Installation & Flashing

### Stage 1: Build Image
```sh
cd /home/artur/ztconflo
python3 build_fajita.py
```

### Stage 2: Enter Fastboot Mode
```sh
adb reboot bootloader
# Verify connection
fastboot devices
```

### Stage 3: Flash Partitions
```sh
cd /home/artur/ztconflo/out/oneplus-fajita
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
