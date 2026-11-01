# OnePlus 6T (*fajita*) ztOS Installation Guide

A quick guide to build and flash **ztOS** onto the OnePlus 6T.

---

## Stage 1: Host Preparation

1. **Install required packages**  
   On Arch Linux / Manjaro:
   ```sh
   sudo pacman -S --needed android-tools python util-linux e2fsprogs libarchive mkbootimg git
   ```
   On Ubuntu / Debian:
   ```sh
   sudo apt update && sudo apt install -y android-tools-adb android-tools-fastboot python3 util-linux e2fsprogs libarchive-tools mkbootimg git
   ```
   *Wait:* ~1 minute.

---

## Stage 2: Get the Repositories

1. **Clone the port repositories**  
   ```sh
   git clone https://github.com/flaherxd/ztconflo.git -b port/oneplus-fajita
   git clone https://github.com/flaherxd/ztOS.git -b port/oneplus-fajita
   ```
   *What you see:* Git cloning progress.  
   *Wait:* ~1–2 minutes.

2. **Enter the builder folder**  
   ```sh
   cd ztconflo
   ```

---

## Stage 3: Build Flashable Images

1. **Run the build script**  
   ```sh
   python3 build_fajita.py
   ```
   *What you see:* Steps 1 through 8 completing, ending with `SUCCESS! Images ready in out/oneplus-fajita`.  
   *Wait:* ~2–3 minutes.

---

## Stage 4: Enter Fastboot Mode

1. **Put the phone into Fastboot**  
   Turn off the OnePlus 6T, then hold **Volume Down + Power** until the fastboot menu appears.
   *(Or run `adb reboot bootloader`)*

2. **Verify connection**  
   ```sh
   fastboot devices
   ```
   *What you see:* Your phone's serial number followed by `fastboot`.  
   *Wait:* ~5 seconds.

---

## Stage 5: Flash Device

1. **Flash boot and userdata partitions**  
   ```sh
   cd out/oneplus-fajita
   fastboot flash boot boot.img
   fastboot flash userdata rootfs.img
   fastboot reboot
   ```
   *What you see:* `Sending... OKAY` and `Writing... OKAY` for both images.  
   *Wait:* ~1 minute.

---

## Stage 6: First Boot & Login

1. **Boot into ztOS**  
   The screen will light up with the OnePlus logo, then display the **ztMETRO** live tile dashboard.  
   *Wait:* ~15–20 seconds.

2. **Connect over USB Ethernet**  
   Connect the phone to your computer via USB cable, then SSH in:
   ```sh
   ssh alarm@172.16.42.1
   ```
   *Login credentials:* user `alarm`, password `alarm` (root password is `root`).

---

## Problem Resolution

| Problem | Cause | Solution |
|---|---|---|
| `fastboot devices` is empty | Faulty USB cable or missing permissions | Use a USB data cable, a rear USB port, or run `sudo fastboot devices`. |
| Speaker volume is quiet | Safe gain limit without upstream DSP curve | **Normal.** Volume is intentionally capped to protect hardware. Do not boost gain. |
| SSH connection times out | Host network manager didn't configure USB interface | On host, assign an IP manually: `sudo ip addr add 172.16.42.2/24 dev <usb-interface>`. |
| Boots back to stock or recovery | Fastboot flashed the inactive slot | Run `fastboot getvar current-slot`, then flash to that slot: `fastboot flash boot_a boot.img` (or `_b`). |
