# OnePlus 6T (*fajita*) ztOS Installation Guide

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
   *What you see:* Package installation progress.  
   *Wait:* ~1 minute.

## Stage 2: Get Repositories

1. **Clone the repositories**  
   ```sh
   git clone https://github.com/flaherxd/ztconflo.git -b port/oneplus-fajita
   ```
   ```sh
   git clone https://github.com/flaherxd/ztOS.git -b port/oneplus-fajita
   ```
   *What you see:* Git checkout progress.  
   *Wait:* ~1 minute.

2. **Open the builder directory**  
   ```sh
   cd ztconflo
   ```

## Stage 3: Build Images

1. **Run the builder script**  
   ```sh
   python3 build_fajita.py
   ```
   *What you see:* Build steps 1–8 completing and `SUCCESS! Images ready in out/oneplus-fajita`.  
   *Wait:* ~2–3 minutes.

## Stage 4: Enter Fastboot Mode

1. **Boot phone to fastboot**  
   Power off the phone, then hold **Volume Down + Power** until the fastboot screen appears.  
   *(Or run: `adb reboot bootloader`)*

2. **Check USB connection**  
   ```sh
   fastboot devices
   ```
   *What you see:* Device serial followed by `fastboot`.  
   *Wait:* 5 seconds.

## Stage 5: Flash Device

1. **Flash boot and rootfs partitions**  
   ```sh
   cd out/oneplus-fajita
   ```
   ```sh
   fastboot flash boot boot.img
   ```
   ```sh
   fastboot flash userdata rootfs.img
   ```
   ```sh
   fastboot reboot
   ```
   *What you see:* `OKAY` confirmations for each partition.  
   *Wait:* ~1 minute.

## Stage 6: First Boot

1. **Wait for ztMETRO to load**  
   The phone boots to the ztMETRO live tile screen.  
   *Wait:* ~15–20 seconds.

2. **Log in over USB Ethernet**  
   ```sh
   ssh alarm@172.16.42.1
   ```
   Type password `alarm` when prompted.

## Problem Resolution

| Problem | Cause | Solution |
|---|---|---|
| `fastboot devices` is empty | Bad cable or missing permissions | Use a USB data cable or run `sudo fastboot devices`. |
| Speaker volume is quiet | Safe gain limit without upstream DSP curve | Normal behavior. Volume is capped to protect hardware. |
| SSH connection times out | Host network manager didn't configure USB link | Run `sudo ip addr add 172.16.42.2/24 dev <usb-interface>`. |
| Boots back to stock or recovery | Fastboot flashed inactive slot | Run `fastboot getvar current-slot`, then flash: `fastboot flash boot_a boot.img` (or `_b`). |
