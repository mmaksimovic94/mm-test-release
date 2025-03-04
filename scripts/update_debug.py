import json
import subprocess
import packaging.version
import re

CONANFILE_PATH = "conanfile.py"

def get_latest_version(package_name):
    """Returns the latest version of a package from Conan with the integration channel."""
    try:
        print(f"Fetching latest version for package: {package_name}")
        # result = subprocess.run(
        #     ["conan", "list", f"{package_name}/*@*/integration", "-f=json"],  # Fetch only @*/integration versions
        #     capture_output=True, text=True, check=True
        # )
        result = subprocess.run(
            ["conan", "search", f"{package_name}/*", "--remote", "conancenter", "-f=json"],
            capture_output=True, text=True, check=True
        )
        versions = []

        search_data = list(json.loads(result.stdout)["conancenter"].keys())
        for key in search_data:
            match = re.match(rf"{package_name}/([\d\.]+)", key)
            # match = re.match(rf"{package_name}/([\d\.]+)@(.+)/integration", key)  # Match only @*/integration versions
            if match:
                versions.append(match.group(1))
            else:
                print(f"No match for key: {key}")

        if versions:
            latest_version = max(versions, key=packaging.version.parse)
            return latest_version

    except subprocess.CalledProcessError:
        print(f"Failed to fetch latest version for {package_name}")
        return None

def update_conanfile():
    """Updates dependencies in conanfile.py to the latest versions and returns True if modified."""

    with open(CONANFILE_PATH, "r") as file:
        content = file.read()

    def replace_version(match):
        full_match = match.group(0)
        package = match.group(1)  # Extract package name
        old_version = match.group(2)  # Extract version (e.g., "1.1.0", "[~1.1.0]", "[^1.1.0]")
        new_version = get_latest_version(package)

        if new_version:
            print(f"Package: {package} - Current version: {old_version} - New version: {new_version}")

            # Preserve caret (^) or tilde (~) if present inside square brackets
            if old_version.startswith("[") and old_version.endswith("]"):
                constraint_symbol = re.match(r"\[(\^|~)?", old_version).group(1) or ""
                return full_match.replace(old_version, f"[{constraint_symbol}{new_version}]")
            else:
                return full_match.replace(old_version, new_version)

        return full_match  # Keep original if no new version is found

    # Updated regex to match conanfile.py format correctly
    updated_content = re.sub(r'self\.(?:build_)?requires\("([^/]+)/(\S+?)(?:@\S+)?"\)', replace_version, content)

    if updated_content != content:
        with open(CONANFILE_PATH, "w") as file:
            file.write(updated_content)
        print("Updated conanfile.py with new dependency versions.")
        return True
    
    print("No changes were made to conanfile.")
    return False

# Test function
if __name__ == "__main__":
    modified = update_conanfile()
    exit(0 if modified else 1)  # Exit with 0 if updates were made, 1 if not
