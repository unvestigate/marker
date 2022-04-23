import subprocess
from zipfile import ZipFile
import glob


def download():
    # https://raw.githubusercontent.com/tldr-pages/tldr-pages.github.io/master/assets/tldr.zip
    subprocess.run(["curl", "-sO", "https://tldr.sh/assets/tldr.zip"])
    with ZipFile("tldr.zip", "r") as zipObj:
       files = zipObj.namelist()
       for file in files:
           if file.startswith("pages/common/") or file.startswith("pages/linux/") or file.startswith("pages/osx/"):
               zipObj.extract(file)


def process(path: str):
    lines = []
    txt = ""
    cmd = ""
    for file in glob.glob(f"pages/{path}/*.md"):
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
                    print(temp)
                    lines.append(temp)
        with open(f"../{path}.txt", "w+") as file:
            file.writelines(lines)
    subprocess.run(["cp", f"{path}.txt", "tldr/"])
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
