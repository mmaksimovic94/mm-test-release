import subprocess
import sys
import json
import re

CONANFILE_PATH = "conanfile.py"

def get_version(branch):
    """Checkout the given branch and retrieve the package version using conan inspect."""
    try:
        subprocess.run(["git", "fetch", "origin", branch, "--depth=1"], check=True)
        subprocess.run(["git", "checkout", branch], check=True)
        result = subprocess.run(["conan", "inspect", "conanfile.py", "--format=json"], 
                                capture_output=True, text=True, check=True)
        version = json.loads(result.stdout)["version"]
        print(f"✅ Version on {branch}: {version}")
        return version
    except subprocess.CalledProcessError as e:
        print(f"❌ Error while processing {branch}: {e}")
        sys.exit(1)

def update_version():
    integration_version = get_version("integration")
    develop_version = get_version("main")

    if develop_version != integration_version:
        print("Version on main and integration branch already different.")
        return False

    major, minor, patch = map(int, develop_version.split("."))
    new_version = f"{major}.{minor + 1}.0"

    with open(CONANFILE_PATH, "r") as file:
        content = file.read()

    def replace_version(match):
        return f'{match.group(1)}"{new_version}"'

    updated_content = re.sub(r'(version\s*=\s*)"\d+\.\d+\.\d+"', replace_version, content)

    if updated_content != content:
        with open(CONANFILE_PATH, "w") as file:
            file.write(updated_content)
        print("Updated conanfile.py with new version.")
        return True
    
    print("No changes were made to conanfile.")
    return False

def main():
    modified = update_version()
    exit(0 if modified else 1)  # Exit with 0 if updates were made, 1 if not

if __name__ == "__main__":
    main()
