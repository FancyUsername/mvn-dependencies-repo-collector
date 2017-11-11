import os
from pathlib import Path
import subprocess
import re
from shutil import copyfile
import sys


def get_folder_size(p):
   """
   https://stackoverflow.com/a/18763675
   :param p: path
   :return: size in bytes
   """
   if not os.path.isdir(p): return 0
   from functools import partial
   prepend = partial(os.path.join, p)
   return sum([(os.path.getsize(f) if os.path.isfile(f) else get_folder_size(f)) for f in map(prepend, os.listdir(p))])

def run(target_repo = "repo"):
    print("mvn dependency:tree ...")
    deps = subprocess.Popen(["mvn", "dependency:tree"], stdout=subprocess.PIPE).communicate()[0].decode('unicode_escape')
    deps = set([match.group(1) for match in re.finditer(r"\[INFO\][ |+-\\]+(.*):compile", deps)])
    for i, dep in enumerate(deps):
        groupId, artifact, packaging, version = dep.split(':')
        rel_path = os.path.join(groupId.replace('.', '/'), artifact, version)
        target_path = os.path.join(target_repo, rel_path)
        os.makedirs(target_path, exist_ok=True)
        src_path = os.path.join(Path.home(), ".m2", "repository", rel_path )
        files = os.listdir(src_path)
        for file in files:
            copyfile(os.path.join(src_path, file), os.path.join(target_path, file))
    print('{} dependencies ({:.2f} MB) copied to "{}"'.format(len(deps), get_folder_size(target_repo) / 1024 ** 2, target_repo))


if __name__ == "__main__":
    if len(sys.argv) > 1: run(sys.argv[1])
    else: run()
