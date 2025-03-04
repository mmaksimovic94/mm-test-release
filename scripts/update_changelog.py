import subprocess
import re
from datetime import date

CHANGELOG_FILE = "changelog.md"

def get_version():
    """Retrieve the package version using conan inspect."""
    try:
        result = subprocess.run(["conan", "inspect", "conanfile.py", "--format=json"], 
                                capture_output=True, text=True, check=True)
        version = json.loads(result.stdout)["version"]
        print(f"✅ Version: {version}")
        return version
    except subprocess.CalledProcessError as e:
        print(f"❌ Error while processing: {e}")
        sys.exit(1)

def update_changelog(version):
    """Replace 'Unreleased' with formatted version string in changelog."""
    with open(CHANGELOG_FILE, "r") as file:
        content = file.read()
    
    # Match '## Unreleased' and replace it with the new version and today's date
    today = date.today().strftime("%Y-%m-%d")
    new_header = f"## [{version}] - {today}"
    updated_content = re.sub(r"##\s+Unreleased", new_header, content, count=1)

    with open(CHANGELOG_FILE, "w") as file:
        file.write(updated_content)

if __name__ == "__main__":
    version = get_version()
    update_changelog(version)
    print(f"Updated changelog with version {version}.")
