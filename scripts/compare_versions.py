import subprocess
import sys
import json

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

def main():
    develop_version = get_version("main")
    integration_version = get_version("integration")

    if develop_version != integration_version:
        print(f"❌ Package versions do not match! (Develop: {develop_version}, Integration: {integration_version})")
        sys.exit(1)
    else:
        print(f"✅ Package versions match: {develop_version}")

if __name__ == "__main__":
    main()
