# OnePlus 6T (*fajita*) ztOS Installation Guide

## Stage 1: Host Preparation

1. Install build and flash utilities on Arch Linux or Manjaro:

    ```sh
    sudo pacman -S --needed android-tools python util-linux e2fsprogs libarchive mkbootimg git
    ```

2. Install build and flash utilities on Ubuntu or Debian:

    ```sh
    sudo apt update && sudo apt install -y android-tools-adb android-tools-fastboot python3 util-linux e2fsprogs libarchive-tools mkbootimg git
    ```

## Stage 2: Getting the Repositories

1. Clone the ztConflo builder repository:

    ```sh
    git clone https://github.com/flaherxd/ztconflo.git -b port/oneplus-fajita
    ```

2. Clone the ztOS mobile shell repository:

    ```sh
    git clone https://github.com/flaherxd/ztOS.git -b port/oneplus-fajita
    ```

3. Enter the builder directory:

    ```sh
    cd ztconflo
    ```

## Stage 3: Building the Images

1. Run the builder script:

    ```sh
    python3 build_fajita.py
    ```

## Stage 4: Entering Fastboot Mode

1. Reboot the phone into bootloader over ADB:

    ```sh
    adb reboot bootloader
    ```

2. Verify that fastboot detects the device:

    ```sh
    fastboot devices
    ```

## Stage 5: Flashing the Device

1. Navigate to the output directory:

    ```sh
    cd out/oneplus-fajita
    ```

2. Flash the boot partition:

    ```sh
    fastboot flash boot boot.img
    ```

3. Flash the root filesystem partition:

    ```sh
    fastboot flash userdata rootfs.img
    ```

4. Reboot the phone into ztOS:

    ```sh
    fastboot reboot
    ```

## Stage 6: First Boot and Access

1. Connect the phone to your computer with a USB cable.

2. Connect to the device via SSH:

    ```sh
    ssh alarm@172.16.42.1
    ```

    Password: `alarm` (root password: `root`).

## Problems

| Problem | Cause | Solution |
| --- | --- | --- |
| Fastboot device not detected | Faulty USB cable or missing permissions | Use a USB data cable, plug into a rear motherboard port, or run `sudo fastboot devices`. |
| Speaker volume is quiet | Safe gain limit without upstream DSP curve | Expected behavior. Volume is capped to protect hardware. |
| SSH connection times out | USB network interface not configured by host | Assign an IP to the host interface: `sudo ip addr add 172.16.42.2/24 dev <interface>`. |
| Device boots into stock OS or recovery | Fastboot flashed the inactive slot | Run `fastboot getvar current-slot`, then flash directly to that slot: `fastboot flash boot_a boot.img` (or `_b`). |
