# OnePlus 6T (*fajita*) ztOS Installation Guide

This guide details how to build and flash **ztOS** onto a OnePlus 6T (Qualcomm Snapdragon 845 / SDM845) using the community port repositories.

---

## Repositories

* **Builder & Device Layer**: [flaherxd/ztconflo (branch `port/oneplus-fajita`)](https://github.com/flaherxd/ztconflo/tree/port/oneplus-fajita)
* **Shell & Core Framework**: [flaherxd/ztOS (branch `port/oneplus-fajita`)](https://github.com/flaherxd/ztOS/tree/port/oneplus-fajita)

---

## Prerequisites

### Hardware
* **OnePlus 6T** (`oneplus-fajita` / A6010 / A6013) with an unlocked bootloader.
* USB-C to USB-A/C data cable.

### Host System (Build Machine)
* Linux PC (Arch Linux, Fedora, Ubuntu/Debian, etc.).
* Standard build and flashing utilities:
  * `android-tools` (`fastboot`, `adb`, `img2simg`)
  * `python` (3.10+)
  * `util-linux` (`unshare` with user namespace support)
  * `e2fsprogs` (`mke2fs`)
  * `libarchive` (`bsdtar`)
  * `mkbootimg`
  * `git`

On Arch Linux / CachyOS / Manjaro:
```sh
sudo pacman -S --needed android-tools python util-linux e2fsprogs libarchive mkbootimg git
```

On Ubuntu / Debian:
```sh
sudo apt update
sudo apt install -y android-tools-adb android-tools-fastboot python3 util-linux e2fsprogs libarchive-tools mkbootimg git
```

---

## Step 1: Clone Repositories

Clone both repositories into the same parent directory, checking out the `port/oneplus-fajita` branch:

```sh
git clone https://github.com/flaherxd/ztconflo.git -b port/oneplus-fajita
git clone https://github.com/flaherxd/ztOS.git -b port/oneplus-fajita
```

---

## Step 2: Build the Flashable Images

Run the automated unprivileged builder inside the `ztconflo` repository:

```sh
cd ztconflo
python3 build_fajita.py
```

### What the builder does:
1. Extracts the generic ztOS GSI rootfs (Arch Linux ARM + ztMETRO shell).
2. Downloads and unpacks Qualcomm SDM845 kernel modules and OnePlus firmware.
3. Injects OnePlus 6T audio configurations (ALSA UCM2, WirePlumber safe volume limits, TFA9894 smart amp profile).
4. Installs the SPMI flashlight udev rules, QRTR services, and modem daemons.
5. Generates the ext4 rootfs sparse image (`rootfs.img`) and fastboot boot image (`boot.img`) with the patched device tree (`sdm845-oneplus-fajita.dtb`).

Output files will be written to `out/oneplus-fajita/`:
* `boot.img` (~28 MB)
* `rootfs.img` (~4.7 GB sparse)
* `flash.sh`

---

## Step 3: Enter Fastboot Mode

1. Power off the OnePlus 6T completely.
2. Hold **Volume Down + Power** until the Fastboot logo appears.
   *(Alternatively, if running Android/recovery: `adb reboot bootloader`)*
3. Connect the phone to your computer via USB.
4. Verify the fastboot connection:
   ```sh
   fastboot devices
   ```

---

## Step 4: Flash Partitions

Flash the boot and userdata partitions:

```sh
cd out/oneplus-fajita
fastboot flash boot boot.img
fastboot flash userdata rootfs.img
fastboot reboot
```

Or execute the generated flash script:
```sh
sh flash.sh
```

---

## Step 5: First Boot & Access

1. The device will reboot and display the boot splash.
2. Within ~15–20 seconds, the device will start **ztMETRO** on the AMOLED display (Windows Phone 8.1 inspired UI running on Wayland at 60 FPS).
3. Connect your computer to the phone via USB. The phone acts as a USB Ethernet gadget (`172.16.42.1`).
4. Log into the device via SSH:
   ```sh
   ssh alarm@172.16.42.1
   ```
   * **Default user**: `alarm`
   * **Default password**: `alarm`
   * **Root password**: `root` (sudo is preconfigured for `alarm`)

---

## Hardware Notes & Tips

* **3D Acceleration**: Hardware accelerated via Turnip Vulkan 1.3 (`vulkan-freedreno`) and Freedreno OpenGL ES 3.1. Test with:
  ```sh
  WAYLAND_DISPLAY=wayland-0 XDG_RUNTIME_DIR=/run/user/1000 vkcube
  ```
* **Audio**: PipeWire and ALSA UCM2 are active with TFA9894 smart speaker amplifier. Sound output is clear and distortion-free, but volume levels are kept conservative/quiet to prevent damage to the speaker hardware until full dynamic DSP protection is implemented.
* **Flashlight / Torch**: Controlled from the Action Center quick toggles via PM8998 dual-LED sysfs bindings.
* **Wi-Fi**: Connect using the Settings tile on the phone, or via terminal:
  ```sh
  nmcli dev wifi connect "Your_SSID" password "Your_Password"
  ```
* **Haptics**: SPMI haptic vibration motor is driven on touch, navigation, and tile taps.
