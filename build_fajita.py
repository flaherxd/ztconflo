#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Unprivileged ztOS builder for OnePlus 6T (oneplus-fajita) using user namespaces."""
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out" / "oneplus-fajita"
CACHE_DIR = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "ztconflo"
WORK = CACHE_DIR / "work" / "oneplus-fajita"
APKS = CACHE_DIR / "apks"
DEVICE = ROOT / "device" / "oneplus-fajita"

# Locate ztOS GSI tarball
GSI_ENV = os.environ.get("ZTOS_GSI")
if GSI_ENV and Path(GSI_ENV).is_file():
    GSI = Path(GSI_ENV)
else:
    candidates = [
        Path.home() / "ztOS" / "build" / "ztos" / "gsi" / "ztos-gsi-0.2.0-aarch64.tar.zst",
        ROOT.parent / "ztOS" / "build" / "ztos" / "gsi" / "ztos-gsi-0.2.0-aarch64.tar.zst",
        CACHE_DIR / "gsi" / "0.2.0" / "ztos-gsi-0.2.0-aarch64.tar.zst",
        ROOT / "ztos-gsi-0.2.0-aarch64.tar.zst",
    ]
    GSI = next((c for c in candidates if c.is_file()), candidates[0])

def say(*args):
    print("==>", *args, flush=True)

def ensure_file(path: Path, url: str):
    if path.exists() and path.stat().st_size > 0:
        return
    say(f"Downloading {path.name}...")
    path.parent.mkdir(parents=True, exist_ok=True)
    import urllib.request
    urllib.request.urlretrieve(url, path)

def run_unshare(cmd, cwd=None):
    unshare_cmd = ["unshare", "--map-auto", "--map-root-user", "--mount", "--fork", "--pid", *cmd]
    res = subprocess.run(unshare_cmd, cwd=cwd, check=True)
    return res

def unpack_apk(apk: Path, dest: Path):
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(apk, "r:gz") as tar:
        members = [m for m in tar.getmembers() if not m.name.startswith(".") or m.name.startswith("./")]
        members = [m for m in members if not Path(m.name).name.startswith(".SIGN.") and m.name not in (".PKGINFO",)]
        tar.extractall(dest, members=members, filter="tar")

def main():
    if not GSI or not GSI.exists():
        print(f"Error: ztOS GSI tarball not found at: {GSI}")
        print("Please build it in ztOS or specify ZTOS_GSI=/path/to/ztos-gsi-0.2.0-aarch64.tar.zst")
        sys.exit(1)

    OUT.mkdir(parents=True, exist_ok=True)
    rootfs = WORK / "root"
    if rootfs.exists():
        say("Removing previous work rootfs...")
        run_unshare(["rm", "-rf", str(rootfs)])
    rootfs.mkdir(parents=True, exist_ok=True)

    say("1. Extracting GSI into rootfs...")
    # Extract GSI as root inside user namespace
    tar_script = f"bsdtar --numeric-owner -xpf '{GSI}' -C '{rootfs}'"
    run_unshare(["sh", "-c", tar_script])

    say("2. Extracting kernel modules and firmware...")
    tmp_kernel = WORK / "pkg_kernel"
    tmp_firmware = WORK / "pkg_firmware"
    shutil.rmtree(tmp_kernel, ignore_errors=True)
    shutil.rmtree(tmp_firmware, ignore_errors=True)
    
    kernel_apk = APKS / "linux-postmarketos-qcom-sdm845-7.1_rc1-r4.apk"
    firmware_apk = APKS / "firmware-oneplus-sdm845-19-r0.apk"
    ensure_file(kernel_apk, "http://mirror.postmarketos.org/postmarketos/master/aarch64/linux-postmarketos-qcom-sdm845-7.1_rc1-r4.apk")
    ensure_file(firmware_apk, "http://mirror.postmarketos.org/postmarketos/master/aarch64/firmware-oneplus-sdm845-19-r0.apk")
    
    unpack_apk(kernel_apk, tmp_kernel)
    unpack_apk(firmware_apk, tmp_firmware)

    # Copy modules into root/usr/lib/modules
    mod_src = tmp_kernel / "lib" / "modules"
    if not mod_src.exists():
        mod_src = tmp_kernel / "usr" / "lib" / "modules"
    dest_mod = rootfs / "usr" / "lib" / "modules"
    dest_mod.mkdir(parents=True, exist_ok=True)
    run_unshare(["cp", "-a", f"{mod_src}/.", str(dest_mod)])

    # Copy firmware into root/usr/lib/firmware
    fw_src = tmp_firmware / "lib" / "firmware"
    if not fw_src.exists():
        fw_src = tmp_firmware / "usr" / "lib" / "firmware"
    dest_fw = rootfs / "usr" / "lib" / "firmware"
    dest_fw.mkdir(parents=True, exist_ok=True)
    run_unshare(["cp", "-a", f"{fw_src}/.", str(dest_fw)])
    run_unshare(["ln", "-sf", "postmarketos/tfa98xx.cnt", str(dest_fw / "tfa98xx.cnt")])

    say("2b. Integrating device-specific hardware files (UCM2, WirePlumber, Qualcomm daemons, services)...")
    dest_ucm = rootfs / "usr" / "share" / "alsa" / "ucm2"
    dest_ucm.mkdir(parents=True, exist_ok=True)
    run_unshare(["cp", "-a", f"{DEVICE / 'ucm2'}/.", str(dest_ucm)])

    dest_wp = rootfs / "etc" / "wireplumber" / "wireplumber.conf.d"
    dest_wp.mkdir(parents=True, exist_ok=True)
    run_unshare(["cp", "-a", f"{DEVICE / 'wireplumber'}/.", str(dest_wp)])

    if (DEVICE / "sounds").exists():
        dest_sounds = rootfs / "usr" / "local" / "share" / "sounds" / "ztos"
        dest_sounds.mkdir(parents=True, exist_ok=True)
        run_unshare(["cp", "-a", f"{DEVICE / 'sounds'}/.", str(dest_sounds)])

    if (DEVICE / "asound.state").exists():
        dest_alsa = rootfs / "var" / "lib" / "alsa"
        dest_alsa.mkdir(parents=True, exist_ok=True)
        run_unshare(["cp", "-a", str(DEVICE / "asound.state"), str(dest_alsa / "asound.state")])

    dest_bin = rootfs / "usr" / "bin"
    dest_lib = rootfs / "usr" / "lib"
    dest_systemd = rootfs / "etc" / "systemd" / "system"
    dest_bin.mkdir(parents=True, exist_ok=True)
    dest_systemd.mkdir(parents=True, exist_ok=True)

    run_unshare(["cp", "-a", str(DEVICE / "bin" / "libqrtr.so.1"), str(dest_lib)])
    run_unshare(["ln", "-sf", "libqrtr.so.1", str(dest_lib / "libqrtr.so")])
    for b in ("pd-mapper", "qrtr-cfg", "qrtr-lookup", "rmtfs", "tqftpserv"):
        run_unshare(["cp", "-a", str(DEVICE / "bin" / b), str(dest_bin / b)])
        run_unshare(["chmod", "0755", str(dest_bin / b)])

    dest_local_bin = rootfs / "usr" / "local" / "bin"
    dest_local_bin.mkdir(parents=True, exist_ok=True)
    for b in ("ztsettings", "ztpower", "ztdevices", "ztmetro", "ztos-sounds"):
        if (DEVICE / "bin" / b).exists():
            run_unshare(["cp", "-a", str(DEVICE / "bin" / b), str(dest_local_bin / b)])
            run_unshare(["chmod", "0755", str(dest_local_bin / b)])

    dest_local_sbin = rootfs / "usr" / "local" / "sbin"
    dest_local_sbin.mkdir(parents=True, exist_ok=True)
    for b in ("ztoscsf", "ztos-bluetooth-init"):
        if (DEVICE / "bin" / b).exists():
            run_unshare(["cp", "-a", str(DEVICE / "bin" / b), str(dest_local_sbin / b)])
            run_unshare(["chmod", "0755", str(dest_local_sbin / b)])

    if (DEVICE / "components").exists():
        dest_csf = rootfs / "etc" / "ztoscoresensorframework"
        dest_csf.mkdir(parents=True, exist_ok=True)
        run_unshare(["cp", "-a", str(DEVICE / "components"), str(dest_csf / "components")])

    if (DEVICE / "udev").exists():
        dest_udev = rootfs / "etc" / "udev" / "rules.d"
        dest_udev.mkdir(parents=True, exist_ok=True)
        run_unshare(["cp", "-a", f"{DEVICE / 'udev'}/.", str(dest_udev)])

    run_unshare(["cp", "-a", f"{DEVICE / 'systemd'}/.", str(dest_systemd)])

    say("3. Writing vendor device layer (ztOSIAL manifest)...")
    vendor_dir = rootfs / "vendor" / "ztos"
    (vendor_dir / "systemd").mkdir(parents=True, exist_ok=True)
    
    manifest_content = """# generated by ztconflo; the device layer's ztOSIAL manifest

[device]
codename = "oneplus-fajita"
name = "OnePlus 6T"
form_factor = "phone"
scale = 2.5

[gsi]
min = "0.2.0"

[ial.Device1]
backend = "generic"
version = 1

[ial.Power1]
backend = "generic"
version = 1

[ial.Perf1]
backend = "generic"
version = 1

[ial.Display1]
backend = "generic"
version = 1
node = "/sys/class/backlight/ae94000.dsi.0"
curve = "linear"

[ial.Sleep1]
backend = "generic"
version = 1
method = "s2idle"

[ial.Sensors1]
backend = "generic"
version = 1

[ial.Haptics1]
backend = "generic"
version = 1
device = "spmi_haptics"

[ial.Lights1]
backend = "generic"
version = 1

[ial.Modem1]
backend = "generic"
version = 1

[android]
binder = "binderfs"
gralloc = "gbm"

[units]
enable = ["rmtfs.service", "pd-mapper.service", "tqftpserv.service"]

[kernel]
contract_checked = false
soft_gaps = []
"""
    (vendor_dir / "manifest.toml").write_text(manifest_content)
    (vendor_dir / "systemd" / "90-ztos-vendor.preset").write_text(
        "enable rmtfs.service pd-mapper.service tqftpserv.service\n"
    )

    say("4. Configuring rootfs inside chroot...")
    chroot_script = f"""set -eu
R='{rootfs}'
mount --bind "$R" "$R"
mount --rbind /dev "$R/dev"
mount -t proc proc "$R/proc"
mount -t tmpfs tmpfs "$R/tmp"
[ -f /etc/resolv.conf ] && rm -f "$R/etc/resolv.conf" && cp -L /etc/resolv.conf "$R/etc/resolv.conf"

chroot "$R" /usr/bin/env -i PATH=/usr/local/sbin:/usr/local/bin:/usr/bin HOME=/root LANG=C.UTF-8 /bin/bash -euc '
echo ztos-oneplus-fajita > /etc/hostname
sed -i "s/#DisableSandbox/DisableSandbox/g" /etc/pacman.conf
pacman-key --init >/dev/null 2>&1 && pacman-key --populate archlinuxarm >/dev/null 2>&1 || true
pacman -S --noconfirm --needed modemmanager libqmi libmbim bluez bluez-utils vulkan-freedreno >/dev/null 2>&1 || true
rm -rf /var/cache/pacman/pkg/*
id alarm >/dev/null 2>&1 || useradd -m -u 1000 -G wheel,video,input,audio -s /bin/bash alarm
usermod -aG wheel,video,input,audio alarm >/dev/null 2>&1 || true
echo "alarm:alarm" | chpasswd
install -d /etc/ztos
printf "ZTOS_USER=%s\\nZTOS_UID=%s\\nZTOS_GID=%s\\nZTOS_HOME=%s\\n" alarm "$(id -u alarm)" "$(id -g alarm)" "$(getent passwd alarm | cut -d: -f6)" > /etc/ztos/user.conf
[ -x /usr/local/sbin/ztos-user-dropins ] && /usr/local/sbin/ztos-user-dropins >/dev/null || true
install -d -m 755 /etc/ztmetro
printf "scale = 2.5\\nvibrator = auto\\nrotation = 0\\n" > /etc/ztmetro/config
[ -f /etc/ztos/session.env ] && sed -i "/ZTMETRO_SCALE/d" /etc/ztos/session.env
systemctl enable greetd NetworkManager sshd systemd-networkd >/dev/null 2>&1 || true
systemctl enable bluetooth ztos-bluetooth-init >/dev/null 2>&1 || true
for k in /usr/lib/modules/*/; do depmod -a "$(basename "$k")" >/dev/null 2>&1 || true; done
systemctl enable ModemManager >/dev/null 2>&1 || true
systemctl enable zboot-usb-gadget >/dev/null 2>&1 || true
systemctl enable zrnperfd >/dev/null 2>&1 || true
systemctl mask alsa-restore.service alsa-state.service ztoscorenetworking-modem.service ztoscirrusaudio.service ztoscsf-sensorhub.service ztoscsf-sensord.service >/dev/null 2>&1 || true
systemctl enable rmtfs pd-mapper tqftpserv modem-boot >/dev/null 2>&1 || true
if [ -x /usr/local/sbin/zboot-session ]; then
    sed -i "s|^command = .*|command = \\"/usr/local/bin/ztmetro-session\\"|" /etc/greetd/config.toml
fi
/usr/bin/ztos-ial check --root / || echo "IAL check finished"
'

umount -l "$R/tmp" "$R/proc" 2>/dev/null || true
umount -lR "$R/dev" 2>/dev/null || true
umount -l "$R" 2>/dev/null || true
"""
    run_unshare(["sh", "-c", chroot_script])

    say("5. Writing ext4 rootfs image (7168M)...")
    raw_img = OUT / "rootfs.raw.img"
    if raw_img.exists():
        raw_img.unlink()
    run_unshare([
        "/usr/bin/mke2fs", "-q", "-t", "ext4", "-L", "pmOS_root",
        "-d", str(rootfs), "-E", "root_owner=0:0", str(raw_img), "7168M"
    ])

    say("6. Converting to sparse fastboot image...")
    sparse_img = OUT / "rootfs.img"
    if sparse_img.exists():
        sparse_img.unlink()
    subprocess.run(["img2simg", str(raw_img), str(sparse_img)], check=True)
    raw_img.unlink(missing_ok=True)

    say("7. Building boot.img with patched device tree...")
    boot_img = OUT / "boot.img"
    kernel_bin = DEVICE / "boot" / "kernel"
    ramdisk_bin = DEVICE / "boot" / "ramdisk"
    dtb_bin = DEVICE / "dtb" / "sdm845-oneplus-fajita.dtb"
    cmd = [
        "mkbootimg",
        "--header_version", "0",
        "--base", "0x00000000",
        "--pagesize", "4096",
        "--kernel_offset", "0x00008000",
        "--ramdisk_offset", "0x01000000",
        "--tags_offset", "0x00000100",
        "--os_version", "11.0.0",
        "--os_patch_level", "2021-08",
        "--kernel", str(kernel_bin),
        "--ramdisk", str(ramdisk_bin),
        "--second", str(dtb_bin),
        "-o", str(boot_img),
    ]
    subprocess.run(cmd, check=True)

    say("8. Writing flash.sh...")
    flash_sh = OUT / "flash.sh"
    flash_sh.write_text("""#!/bin/sh
# Generated by ztConflo for oneplus-fajita (OnePlus 6T). Overwrites: boot, userdata.
set -eu
cd "$(dirname "$0")"
echo "Flashing boot partition..."
fastboot flash boot boot.img
echo "Flashing userdata (rootfs) partition..."
fastboot flash userdata rootfs.img
echo "Rebooting into ztOS..."
fastboot reboot
""")
    flash_sh.chmod(0o755)

    say(f"SUCCESS! Images ready in {OUT}")
    for item in ("boot.img", "rootfs.img", "flash.sh"):
        p = OUT / item
        if p.exists():
            say(f"  {p.name}: {p.stat().st_size / (1024*1024):.1f} MB")

if __name__ == "__main__":
    main()
