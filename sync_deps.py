import json
import toml

def sync_dependencies():
    # Load dependencies from Pipfile.lock
    with open("Pipfile.lock", "r") as pipfile:
        pipfile_content = json.load(pipfile)
        default_deps = {name: detail['version'] for name, detail in pipfile_content.get('default', {}).items()}
        dev_deps = {name: detail['version'] for name, detail in pipfile_content.get('develop', {}).items()}

    # Load current pyproject.toml content
    with open("pyproject.toml", "r") as pyproject:
        pyproject_content = toml.load(pyproject)

    # Update dependencies in pyproject.toml
    pyproject_content["dependencies"] = default_deps
    pyproject_content["dev-dependencies"] = dev_deps

    # Save updated pyproject.toml content
    with open("pyproject.toml", "w") as pyproject:
        toml.dump(pyproject_content, pyproject)

if __name__ == "__main__":
    sync_dependencies()
    print("Dependencies synced from Pipfile.lock to pyproject.toml!")