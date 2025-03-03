import json
import subprocess

CONANFILE_PATH = "conanfile.py"

def get_conan_dependencies():
    """Retrieves current dependencies using `conan graph info`."""
    try:
        result = subprocess.run(
            ["conan", "graph", "info", CONANFILE_PATH, "--format=json"],
            capture_output=True, text=True, check=True
        )
        print("Raw Conan output:", result.stdout)  # Debugging line
        graph_data = list(json.loads(result.stdout)["graph"]["nodes"].values())
        
        requires = []
        build_requires = []

        for node in graph_data:
            if "ref" in node:
                ref = node["ref"]
                if "build_requires" in node.get("context", ""):
                    build_requires.append(ref)
                else:
                    requires.append(ref)

        return requires, build_requires
    except subprocess.CalledProcessError as e:
        print("Failed to retrieve Conan dependencies.")
        print("Error message:", e.stderr)
        return [], []

# Test function
if __name__ == "__main__":
    print("Checking Conan dependencies...")
    reqs, build_reqs = get_conan_dependencies()
    print("Requires:", reqs)
    print("Build requires:", build_reqs)
