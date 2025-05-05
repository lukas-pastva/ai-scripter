import os
import datetime
import stat
from fnmatch import fnmatch

# ────────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ────────────────────────────────────────────────────────────────────────────────
ALLOWED_HIDDEN = {
    '.github',
    '.gitlab-ci.yml',
}

IGNORE_DIR_PATTERNS = {
    'tmp',
    'js'
    # e.g. 'node_modules', '*.egg-info'
}

SKIP_IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
    '.tif', '.tiff', '.jar', '.scss', '.eot',
    '.ttf', '.woff', '.otf', '.woff2', '.less'
}

SKIP_FILENAMES = {
    'license',
}

SKIP_FILE_PATTERNS = [
    'jquery*.js',
    'bootstrap*css',
]

# ────────────────────────────────────────────────────────────────────────────────
# HIDDEN / IGNORE HELPERS
# ────────────────────────────────────────────────────────────────────────────────
def is_hidden(filepath):
    name = os.path.basename(os.path.abspath(filepath))
    if name in ALLOWED_HIDDEN:
        return False
    if name.startswith('.'):
        return True
    try:
        attrs = os.stat(filepath).st_file_attributes
        return bool(attrs & stat.FILE_ATTRIBUTE_HIDDEN)
    except AttributeError:
        return False

def load_gitignore_patterns(base_path):
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
    return any(fnmatch(name, patt) for patt in ignore_patterns)

# ────────────────────────────────────────────────────────────────────────────────
# FILE‐SKIP HELPER
# ────────────────────────────────────────────────────────────────────────────────
def should_skip_file(file_path):
    base = os.path.basename(file_path).lower()
    _, ext = os.path.splitext(base)
    if ext in SKIP_IMAGE_EXTENSIONS:
        return True
    if base in SKIP_FILENAMES or any(base.startswith(name + '.') for name in SKIP_FILENAMES):
        return True
    return any(fnmatch(base, patt) for patt in SKIP_FILE_PATTERNS)

# ────────────────────────────────────────────────────────────────────────────────
# TREE GENERATION
# ────────────────────────────────────────────────────────────────────────────────
def generate_ascii_tree(startpath, ignore_patterns):
    tree_str = ''
    for root, dirs, files in os.walk(startpath):
        rel = os.path.relpath(root, startpath)
        level = 0 if rel == '.' else rel.count(os.sep)
        indent = ' ' * 4 * level
        dirname = os.path.basename(root) if rel else (os.path.basename(startpath) or '.')

        # filter directories
        dirs[:] = [
            d for d in dirs
            if not is_hidden(os.path.join(root, d))
            and not any(fnmatch(d, patt) for patt in IGNORE_DIR_PATTERNS)
            and not should_ignore(d, ignore_patterns)
        ]

        # filter files (now also skip the SKIP_* ones)
        files = [
            f for f in files
            if not is_hidden(os.path.join(root, f))
            and not should_ignore(f, ignore_patterns)
            and not should_skip_file(os.path.join(root, f))
        ]

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

    tmp_dir = os.path.join(cwd, 'tmp')
    os.makedirs(tmp_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime('state-%Y-%m-%d-%H-%M-%S.txt')
    output_file = os.path.join(tmp_dir, timestamp)

    with open(output_file, 'w', encoding='utf-8') as out:
        out.write('Hello dear AI, please for below request, give me whole contents of files that changed (not the ones that did not change).\n')
        out.write('........................\n\n')

        # 1) Directory tree (skipping the SKIP_* files)
        out.write(generate_ascii_tree(cwd, ignore_patterns))

        # 2) File contents (only for the same filtered set)
        for root, dirs, files in os.walk(cwd):
            # dir filters
            dirs[:] = [
                d for d in dirs
                if not is_hidden(os.path.join(root, d))
                and not any(fnmatch(d, patt) for patt in IGNORE_DIR_PATTERNS)
                and not should_ignore(d, ignore_patterns)
            ]

            # file filters
            files = [
                f for f in files
                if not is_hidden(os.path.join(root, f))
                and not should_ignore(f, ignore_patterns)
                and not should_skip_file(os.path.join(root, f))
            ]

            for filename in files:
                full_path = os.path.join(root, filename)
                # never dump our own state file
                if os.path.abspath(full_path) == os.path.abspath(output_file):
                    continue

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
