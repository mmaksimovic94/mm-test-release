import json
import subprocess
import packaging.version
import re

CONANFILE_PATH = "conanfile.py"

def get_conan_dependencies():
    """Retrieves current dependencies using `conan graph info`."""
    try:
        result = subprocess.run(
            ["conan", "graph", "info", CONANFILE_PATH, "-f=json"],
            capture_output=True, text=True, check=True
        )
        # print("Raw Conan output:", result.stdout)  # Debugging line
        graph_data = list(json.loads(result.stdout)["graph"]["nodes"].values())
        
        dependencies = []

        for node in graph_data:
            if "ref" in node and node["name"] != "hello_world":
                ref_value = node["ref"].split("#")[0]
                dependencies.append(ref_value)

        return dependencies
    except subprocess.CalledProcessError as e:
        print("Failed to retrieve Conan dependencies.")
        print("Error message:", e.stderr)
        return []

def get_latest_version(package_name):
    """Returns the latest version of a package from Conan."""
    try:
        result = subprocess.run(
            ["conan", "search", f"{package_name}/*", "--remote", "conancenter", "-f=json"],
            capture_output=True, text=True, check=True
        )
        versions = []
        search_data = list(json.loads(result.stdout)["conancenter"].keys())
        for key in search_data:
            version = key.split("/")[-1]
            if version.replace(".", "").isdigit():
                versions.append(version)

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
        package = match.group(2)
        old_version = match.group(3)  # Can be "1.11.0", "[~1.11.0]", "[^9.0.0]"
        new_version = get_latest_version(package)

        if new_version:
            print(f"Package: {package} - Current version: {old_version} - New version: {new_version}")

            # Preserve caret (^) or tilde (~) if present inside square brackets
            if old_version.startswith("[") and old_version.endswith("]"):
                constraint_symbol = re.match(r"\[(\^|~)?", old_version).group(1) or ""
                return f'{match.group(1)}[{constraint_symbol}{new_version}]{match.group(4)}'
            else:
                return f'{match.group(1)}{new_version}{match.group(4)}'

        return match.group(0)  # Keep original if no new version is found

    updated_content = re.sub(r'(self\.(?:requires|build_requires)\("([^"]+)/)([^"]+)("\))', replace_version, content)

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


