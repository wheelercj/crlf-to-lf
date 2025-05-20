import os
import subprocess

# Folders listed here will be ignored by this script.
folders_to_exclude = [
    "__pycache__",
    "__pypackages__",
    "_build",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "build",
    "dist",
    "lib",
    "logs",
    "node_modules",
    "site-packages",
    "venv",
]

# Only files that end with one of these will be changed.
file_suffixes_to_include = [
    ".bat",
    ".bru",
    ".cs",
    ".css",
    ".dockerignore",
    ".env",
    ".gitignore",
    ".gitmodules",
    ".go",
    ".html",
    ".js",
    ".json",
    ".md",
    ".mod",
    ".py",
    ".rst",
    ".sql",
    ".tmpl",
    ".toml",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
    "Dockerfile",
    "INSTALLER",
    "LICENSE",
    "Makefile",
    "METADATA",
    "WHEEL",
]

ignored_suffixes = set()


def main():
    has_gitignore: bool = os.path.exists(".gitignore")
    crlf_to_lf(has_gitignore)
    print(
        f"File suffixes ignored by this script but not by Git: {sorted(ignored_suffixes) or '(none)'}"
    )


def crlf_to_lf(has_gitignore: bool, path: str = "."):
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_dir():
                if entry.name in folders_to_exclude:
                    continue
                crlf_to_lf(has_gitignore, entry.path)
            elif entry.is_file():
                if has_accepted_suffix(entry.name):
                    with open(entry.path, "r+", encoding="utf8") as file:
                        content = file.read()
                        content = content.replace("\r\n", "\n")
                        file.seek(0)
                        file.truncate()
                        file.write(content)
                elif has_gitignore and not in_gitignore(entry.path):
                    last_token = entry.name.split(".")[-1]
                    if "." in entry.name:
                        last_token = "." + last_token
                    ignored_suffixes.add(last_token)


def has_accepted_suffix(file_name: str) -> bool:
    for suffix in file_suffixes_to_include:
        if file_name.endswith(suffix):
            return True
    return False


def in_gitignore(filepath: str) -> bool:
    try:
        subprocess.run(
            ["git", "check-ignore", filepath],
            capture_output=True,
            text=True,
            check=True,  # raise an exception for non-zero exit codes
        )
        # the file is in the .gitignore
        return True
    except subprocess.CalledProcessError as err:
        if err.returncode == 1:
            # the file is not in the .gitignore
            return False
        else:
            raise RuntimeError(f"Error checking .gitignore status: {err}")
    except Exception as err:
        raise RuntimeError(f"Unexpected error: {err}")


main()
