import glob
import hashlib
import os
import subprocess
from tracemalloc import stop
from zipfile import ZipFile


def download():
    current_checksum = ""
    checksum = ""
    # https://tldr.sh/assets/tldr.zip
    subprocess.run(
        ["curl", "-sO", "https://raw.githubusercontent.com/tldr-pages/tldr-pages.github.io/master/assets/tldr.zip"])
    with open("tldr.zip", "rb") as file:
        data = file.read()
        checksum = hashlib.sha256(data).hexdigest()
    try:
        with open("checksum.txt", "r") as file:
            current_checksum = file.read()
    except:
        pass
    with open("checksum.txt", "w") as file:
        file.seek(0)
        file.write(checksum)
        file.truncate()
        if checksum != current_checksum:
            print("New checksum, updating")
            file.seek(0)
            file.write(checksum)
            file.truncate()
            with ZipFile("tldr.zip", "r") as zipObj:
                files = zipObj.namelist()
                for file in files:
                    if file.startswith("pages/common/") or file.startswith("pages/linux/") or file.startswith("pages/osx/"):
                        zipObj.extract(file)
        else:
            print("Same checksum, not updating")
            cleanup()
            exit(0)


def process(path: str):
    new_lines = []
    txt = ""
    cmd = ""
    old_lines = []
    aux = []
    tldr_path = os.path.join(os.getenv('MARKER_HOME'), 'tldr')

    with open(f"{tldr_path}/{path}.txt", "r") as file:
        old_lines = file.readlines()

    for file in sorted(glob.glob(f"pages/{path}/*.md")):
        with open(file, "r") as f:
            for line in f.readlines():
                if line == "\n" or line.startswith("#") or line.startswith(">"):
                    continue
                if line.startswith("-") and not line.startswith("--"):
                    txt = line.replace("\n", "").replace(":", "").replace("- ", "")
                elif line.startswith("`"):
                    cmd = line.replace("`", "").replace("\n", "")
                else:
                    continue
                if (cmd != "" and cmd != "\n") and (txt != "" and txt != "\n"):
                    temp = f"{cmd}##{txt}\n"
                    txt = ""
                    cmd = ""
                    new_lines.append(temp.lstrip())
    for nl in sorted(new_lines):
        if nl not in old_lines:
            aux.append(nl)
    old_lines += aux
    with open(f"{tldr_path}/{path}.txt", "w+") as file:
        file.writelines(sorted(old_lines))
    subprocess.run(["cp", f"{path}.txt", tldr_path])
    subprocess.run(["rm", f"{path}.txt"])


def cleanup():
    subprocess.run(["rm", "-rfd", "pages/"])
    subprocess.run(["rm", "tldr.zip"])


def update():
    download()
    process("common")
    process("linux")
    process("osx")
    cleanup()
    print("Update completed")
