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
        
        dependencies = []
        for node in graph_data["nodes"].values():
            if "ref" in node:
                ref = node["ref"]
                if "@mili/integration" in ref:
                    dependencies.append(ref)
        
        return dependencies
    except subprocess.CalledProcessError:
        print("Failed to retrieve Conan dependencies.")
        return []

def get_latest_version(package_name):
    """Returns the latest version of a package from Conan."""
    try:
        result = subprocess.run(
            ["conan", "search", f"{package_name}/*@mili/integration", "--raw"],
            capture_output=True, text=True, check=True
        )
        versions = [line.split("/")[1].split("@")[0] for line in result.stdout.splitlines() if package_name in line]
        return sorted(versions, key=lambda v: [int(x) for x in v.split(".")])[-1] if versions else None
    except subprocess.CalledProcessError:
        print(f"Failed to fetch latest version for {package_name}")
        return None

def update_conanfile():
    """Updates dependencies in conanfile.py to the latest versions."""
    dependencies = get_conan_dependencies()
    
    if not dependencies:
        print("No dependencies found to update.")
        return
    
    with open(CONANFILE_PATH, "r") as file:
        lines = file.readlines()
    
    for i, line in enumerate(lines):
        for dep in dependencies:
            package, current_version = dep.split("/")[0], dep.split("/")[1].split("@")[0]
            latest_version = get_latest_version(package)
            if latest_version and latest_version != current_version:
                print(f"Updating {package} from {current_version} to {latest_version}")
                lines[i] = line.replace(f"{package}/{current_version}@mili/integration", 
                                        f"{package}/{latest_version}@mili/integration")

    with open(CONANFILE_PATH, "w") as file:
        file.writelines(lines)

if __name__ == "__main__":
    update_conanfile()
