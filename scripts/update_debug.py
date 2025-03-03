import json
import subprocess
import packaging.version

CONANFILE_PATH = "conanfile.py"

def get_conan_dependencies():
    """Retrieves current dependencies using `conan graph info`."""
    try:
        result = subprocess.run(
            ["conan", "graph", "info", CONANFILE_PATH, "-f=json"],
            capture_output=True, text=True, check=True
        )
        print("Raw Conan output:", result.stdout)  # Debugging line
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

        # versions = [line.split("/")[1] for line in result.stdout.splitlines() if package_name in line]
        # return sorted(versions, key=lambda v: [int(x) for x in v.split(".")])[-1] if versions else None
    except subprocess.CalledProcessError:
        print(f"Failed to fetch latest version for {package_name}")
        return None

def update_conanfile():
    """Updates dependencies in conanfile.py to the latest versions and returns True if modified."""
    dependencies = get_conan_dependencies()
    print("Deps list:", dependencies)
    
    if not dependencies:
        print("No dependencies found to update.")
        return False

    with open(CONANFILE_PATH, "r") as file:
        lines = file.readlines()

    modified = False

    for i, line in enumerate(lines):
        for dep in dependencies:
            package, current_version = dep.split("/")[0], dep.split("/")[1]
            latest_version = get_latest_version(package)
            print(f"Package: {package} - Current version: {current_version} - Latest version: {latest_version}")
            if latest_version and latest_version != current_version:
                print(f"Updating {package} from {current_version} to {latest_version}")
                lines[i] = line.replace(f'"{package}/{current_version}"', f'"{package}/{latest_version}"')
                modified = True

    if modified:
        with open(CONANFILE_PATH, "w") as file:
            file.writelines(lines)

    return modified

# Test function
if __name__ == "__main__":
    modified = update_conanfile()
    exit(0 if modified else 1)  # Exit with 0 if updates were made, 1 if not


