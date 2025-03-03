import json
import subprocess

CONANFILE_PATH = "conanfile.py"

def get_conan_dependencies():
    """Retrieves current dependencies using `conan graph info`."""
    try:
        result = subprocess.run(
            ["conan", "graph", "info", CONANFILE_PATH, "--format", "json"],
            capture_output=True, text=True, check=True
        )
        graph_data = json.loads(result.stdout)

        requires = []
        build_requires = []

        for node in graph_data["nodes"].values():
            if "ref" in node:
                ref = node["ref"]
                if "build_requires" in node.get("context", ""):
                    build_requires.append(ref)
                else:
                    requires.append(ref)

        return requires, build_requires
    except subprocess.CalledProcessError:
        print("Failed to retrieve Conan dependencies.")
        return [], []

def get_latest_version(package_name):
    """Returns the latest version of a package from Conan."""
    try:
        result = subprocess.run(
            ["conan", "search", f"{package_name}/*", "--remote", "conancenter", "--raw"],
            capture_output=True, text=True, check=True
        )
        versions = [line.split("/")[1] for line in result.stdout.splitlines() if package_name in line]
        return sorted(versions, key=lambda v: [int(x) for x in v.split(".")])[-1] if versions else None
    except subprocess.CalledProcessError:
        print(f"Failed to fetch latest version for {package_name}")
        return None

def update_conanfile():
    """Updates dependencies in conanfile.py to the latest versions and returns True if modified."""
    requires, build_requires = get_conan_dependencies()
    
    if not requires and not build_requires:
        print("No dependencies found to update.")
        return False

    with open(CONANFILE_PATH, "r") as file:
        lines = file.readlines()

    modified = False

    for i, line in enumerate(lines):
        for dep_list in [requires, build_requires]:
            for dep in dep_list:
                package, current_version = dep.split("/")[0], dep.split("/")[1]
                latest_version = get_latest_version(package)
                if latest_version and latest_version != current_version:
                    print(f"Updating {package} from {current_version} to {latest_version}")
                    lines[i] = line.replace(f'"{package}/{current_version}"', f'"{package}/{latest_version}"')
                    modified = True

    if modified:
        with open(CONANFILE_PATH, "w") as file:
            file.writelines(lines)

    return modified

if __name__ == "__main__":
    modified = update_conanfile()
    exit(0 if modified else 1)  # Exit with 0 if updates were made, 1 if not
