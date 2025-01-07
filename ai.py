import os
import datetime
import stat
from fnmatch import fnmatch

def is_hidden(filepath):
    """
    Determine if a file or directory is hidden.
    """
    name = os.path.basename(os.path.abspath(filepath))
    if name.startswith('.'):
        return True
    try:
        attrs = os.stat(filepath).st_file_attributes
        return bool(attrs & stat.FILE_ATTRIBUTE_HIDDEN)
    except AttributeError:
        # Non-Windows systems may not have st_file_attributes
        return False

def load_gitignore_patterns(base_path):
    """
    Load .gitignore patterns from the .gitignore file if it exists.
    Returns a list of patterns.
    """
    gitignore_path = os.path.join(base_path, '.gitignore')
    patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8', errors='ignore') as g:
            for line in g:
                line = line.strip()
                # Exclude comments and blank lines
                if line and not line.startswith('#'):
                    patterns.append(line)
    return patterns

def should_ignore(name, ignore_patterns):
    """
    Check if a file or directory name should be ignored based on .gitignore patterns.
    """
    for pattern in ignore_patterns:
        # If pattern doesn't start with '/', we treat it as matching anywhere.
        # Simple approach: just fnmatch the filename.
        if fnmatch(name, pattern):
            return True
    return False

def generate_ascii_tree(startpath, ignore_patterns):
    """
    Generate an ASCII tree representation of the current directory,
    excluding hidden files, directories, the ai directory, and files/directories specified in .gitignore.
    """
    tree_str = ''
    for root, dirs, files in os.walk(startpath):
        # Calculate the relative path from startpath
        relpath = os.path.relpath(root, startpath)
        if relpath == '.':
            relpath = ''
        # Determine the depth level
        level = relpath.count(os.sep)
        indent = ' ' * 4 * level
        dirname = os.path.basename(root) if root != startpath else os.path.basename(startpath) or '.'

        # Exclude hidden directories, 'ai' directory, and gitignored directories
        dirs[:] = [d for d in dirs 
                   if not is_hidden(os.path.join(root, d)) 
                   and d != 'ai' 
                   and not should_ignore(d, ignore_patterns)]

        # Exclude hidden files and gitignored files
        files = [f for f in files 
                 if not is_hidden(os.path.join(root, f)) 
                 and not should_ignore(f, ignore_patterns)]

        tree_str += '{}{}/\n'.format(indent, dirname)
        subindent = ' ' * 4 * (level + 1)
        
        for f in files:
            tree_str += '{}{}\n'.format(subindent, f)
    return tree_str

def should_skip_file(file_name):
    """
    Determine if a file should be skipped from being read and included in the state file.
    We skip image files and LICENSE files.
    """
    # Common image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg', '.tif', '.tiff'}
    base_name = os.path.basename(file_name).lower()
    _, ext = os.path.splitext(base_name)
    
    # Check for images
    if ext in image_extensions:
        return True
    
    # Check for license files
    if base_name == 'license' or base_name.startswith('license.'):
        return True
    
    return False

def main():
    current_dir = os.getcwd()
    
    # Load .gitignore patterns
    ignore_patterns = load_gitignore_patterns(current_dir)

    # Create 'ai' directory if it doesn't exist (excluded from scanning but we still need it as output target)
    ai_dir = os.path.join(current_dir, 'ai')
    if not os.path.exists(ai_dir):
        os.makedirs(ai_dir)
    
    # Get current datetime for filename
    now = datetime.datetime.now()
    filename = now.strftime('state-%Y-%m-%d-%H-%M-%S.txt')
    output_file_path = os.path.join(ai_dir, filename)
    
    with open(output_file_path, 'w', encoding='utf-8') as f:
        # Write the initial text
        f.write('Hello dear AI, please for below request, guve me whoel contents of files that you hve gladly changed. Because you are just super cool!\n')
        f.write('........................\n\n')
        
        # Generate the ASCII tree for the current directory and write to file
        tree = generate_ascii_tree(current_dir, ignore_patterns)
        f.write(tree)
        
        # Then write the contents of all files within the current directory
        for root, dirs, files in os.walk(current_dir):
            # Exclude hidden directories, 'ai', and gitignored directories
            dirs[:] = [d for d in dirs 
                       if not is_hidden(os.path.join(root, d)) 
                       and d != 'ai' 
                       and not should_ignore(d, ignore_patterns)]

            # Exclude hidden and gitignored files
            files = [f_name for f_name in files 
                     if not is_hidden(os.path.join(root, f_name)) 
                     and not should_ignore(f_name, ignore_patterns)]

            for file in files:
                full_file_path = os.path.join(root, file)
                
                # Skip if it's the output file itself
                if os.path.abspath(full_file_path) == os.path.abspath(output_file_path):
                    continue
                
                # Skip files we don't want to include (images, license)
                if should_skip_file(full_file_path):
                    continue
                
                try:
                    with open(full_file_path, 'r', encoding='utf-8', errors='ignore') as content_file:
                        relative_path = os.path.relpath(full_file_path, current_dir)
                        f.write(f'\n\n------------------ Start of {relative_path} ------------------\n\n')
                        f.write(content_file.read())
                        f.write(f'\n\n------------------ End of {relative_path} ------------------\n\n')
                except Exception as e:
                    relative_path = os.path.relpath(full_file_path, current_dir)
                    f.write(f'\n\n------------------ Could not read {relative_path}: {e} ------------------\n\n')

    print(f"State file generated at: {output_file_path}")

if __name__ == '__main__':
    main()
