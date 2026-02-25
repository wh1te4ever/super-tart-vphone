import os, glob, subprocess

target_dir = "./iosbinpack64"

for p in glob.glob(f"{target_dir}/**/*", recursive=True):
    if os.path.isfile(p) and not os.path.islink(p) and "Mach-O" in subprocess.getoutput(f'file "{p}"'):
        os.system(f'tools/ldid_macosx_arm64 -S -M -Ksigncert.p12 "{p}"')