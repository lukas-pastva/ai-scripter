import os
import datetime
import stat
from fnmatch import fnmatch

# ────────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ────────────────────────────────────────────────────────────────────────────────
# Hidden files or folders you explicitly WANT to include.
ALLOWED_HIDDEN = {
    '.github',          # directory
    '.gitlab-ci.yml',  # single file
}

# Directory names or glob‐patterns to ignore entirely.
IGNORE_DIR_PATTERNS = {
    'tmp',              # our temporary output folder
    'js'
    # add other dirs you never want to scan, e.g. 'node_modules', '*.egg-info'
}

# File extensions (lowercase) to skip entirely.
SKIP_IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
    '.tif', '.tiff', '.jar', '.scss', '.eot',
    '.ttf', '.woff', '.otf', '.woff2', '.less',
}

# Base filenames (no extension) to skip entirely.
SKIP_FILENAMES = {
    'license',  # also covers 'LICENSE', etc.
}

# Wildcard file patterns to skip.
SKIP_FILE_PATTERNS = [
    'jquery*.js',
    'bootstrap*css',
]

# ────────────────────────────────────────────────────────────────────────────────
# HIDDEN / IGNORE HELPERS
# ────────────────────────────────────────────────────────────────────────────────
def is_hidden(filepath):
    """
    Determine if a file or directory is hidden *and* not explicitly allowed.
    """
    name = os.path.basename(os.path.abspath(filepath))

    # 1. Whitelist first
    if name in ALLOWED_HIDDEN:
        return False

    # 2. Standard Unix hidden detection
    if name.startswith('.'):
        return True

    # 3. Windows FILE_ATTRIBUTE_HIDDEN flag
    try:
        attrs = os.stat(filepath).st_file_attributes
        return bool(attrs & stat.FILE_ATTRIBUTE_HIDDEN)
    except AttributeError:
        # Non-Windows systems may not have st_file_attributes
        return False


def load_gitignore_patterns(base_path):
    """
    Load patterns from a .gitignore file if present.
    """
    patterns = []
    gitignore_path = os.path.join(base_path, '.gitignore')
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8', errors='ignore') as g:
            for line in g:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    return patterns


def should_ignore(name, ignore_patterns):
    """
    Check whether *name* matches any .gitignore pattern.
    """
    for pattern in ignore_patterns:
        if fnmatch(name, pattern):
            return True
    return False


# ────────────────────────────────────────────────────────────────────────────────
# FILE‐SKIP HELPER
# ────────────────────────────────────────────────────────────────────────────────
def should_skip_file(file_name):
    """
    Decide whether to exclude *file_name* from the output bundle.
    """
    base = os.path.basename(file_name).lower()
    _, ext = os.path.splitext(base)

    # skip by extension
    if ext in SKIP_IMAGE_EXTENSIONS:
        return True

    # skip known base names
    if base in SKIP_FILENAMES or any(base.startswith(name + '.') for name in SKIP_FILENAMES):
        return True

    # skip by wildcard patterns
    return any(fnmatch(base, patt) for patt in SKIP_FILE_PATTERNS)


# ────────────────────────────────────────────────────────────────────────────────
# TREE & CONTENT GENERATION
# ────────────────────────────────────────────────────────────────────────────────
def generate_ascii_tree(startpath, ignore_patterns):
    """
    Produce an ASCII tree of *startpath*, applying all exclusion rules.
    """
    tree_str = ''
    for root, dirs, files in os.walk(startpath):
        # Relative path depth controls indentation
        relpath = os.path.relpath(root, startpath)
        if relpath == '.':
            relpath = ''
        level = relpath.count(os.sep)
        indent = ' ' * 4 * level
        dirname = os.path.basename(root) if root != startpath else (os.path.basename(startpath) or '.')

        # --- filter directories -------------------------------------------------
        filtered_dirs = []
        for d in dirs:
            full_d = os.path.join(root, d)
            if is_hidden(full_d):
                continue
            if any(fnmatch(d, patt) for patt in IGNORE_DIR_PATTERNS):
                continue
            if should_ignore(d, ignore_patterns):
                continue
            filtered_dirs.append(d)
        dirs[:] = filtered_dirs

        # --- filter files -------------------------------------------------------
        filtered_files = []
        for f in files:
            full_f = os.path.join(root, f)
            if is_hidden(full_f):
                continue
            if should_ignore(f, ignore_patterns):
                continue
            filtered_files.append(f)
        files = filtered_files

        # add this directory to the tree
        tree_str += f'{indent}{dirname}/\n'
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            tree_str += f'{subindent}{f}\n'
    return tree_str


# ────────────────────────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────────────────────────
def main():
    cwd = os.getcwd()
    ignore_patterns = load_gitignore_patterns(cwd)

    # Ensure tmp directory exists (but is never scanned)
    tmp_dir = os.path.join(cwd, 'tmp')
    os.makedirs(tmp_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime('state-%Y-%m-%d-%H-%M-%S.txt')
    output_file = os.path.join(tmp_dir, timestamp)

    with open(output_file, 'w', encoding='utf-8') as out:
        out.write('Hello dear AI, please for below request, give me whole contents of files that changed (not the ones that did not change).\n')
        out.write('........................\n\n')

        # 1) Directory tree
        out.write(generate_ascii_tree(cwd, ignore_patterns))

        # 2) File contents
        for root, dirs, files in os.walk(cwd):
            # directory filtering
            filtered_dirs = []
            for d in dirs:
                full_d = os.path.join(root, d)
                if is_hidden(full_d):
                    continue
                if any(fnmatch(d, patt) for patt in IGNORE_DIR_PATTERNS):
                    continue
                if should_ignore(d, ignore_patterns):
                    continue
                filtered_dirs.append(d)
            dirs[:] = filtered_dirs

            # file filtering
            filtered_files = []
            for fn in files:
                full_f = os.path.join(root, fn)
                if os.path.abspath(full_f) == os.path.abspath(output_file):
                    continue
                if is_hidden(full_f):
                    continue
                if should_ignore(fn, ignore_patterns):
                    continue
                if should_skip_file(full_f):
                    continue
                filtered_files.append(fn)
            files = filtered_files

            for filename in files:
                full_path = os.path.join(root, filename)
                rel = os.path.relpath(full_path, cwd)
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as src:
                        out.write(f'\n\n------------------ Start of {rel} ------------------\n\n')
                        out.write(src.read())
                        out.write(f'\n\n------------------ End of {rel} ------------------\n\n')
                except Exception as exc:
                    out.write(f'\n\n------------------ Could not read {rel}: {exc} ------------------\n\n')

    print(f"State file generated at: {output_file}")


if __name__ == '__main__':
    main()
