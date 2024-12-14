import subprocess
from pathlib import Path

def get_git_root():
    try:
        # Run the git command to find the root directory
        git_root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).strip().decode("utf-8")
        return Path(git_root)
    except subprocess.CalledProcessError:
        raise RuntimeError("This directory is not inside a Git repository")

# Change the current working directory to the Git root
git_root = get_git_root()
print("Git root is at:", git_root)

# Change the working directory to the Git root
import os
os.chdir(git_root)

print("Current working directory:", os.getcwd())