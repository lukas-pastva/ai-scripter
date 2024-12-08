import os
import datetime
import stat

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

def generate_ascii_tree(startpath):
    """
    Generate an ASCII tree representation of the current directory.
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
        dirname = os.path.basename(root) if relpath else os.path.basename(startpath)
        dirname = dirname if dirname else os.path.basename(startpath)
        tree_str += '{}{}/\n'.format(indent, dirname)
        subindent = ' ' * 4 * (level + 1)
        
        # Exclude hidden files and directories
        dirs[:] = [d for d in dirs if not is_hidden(os.path.join(root, d))]
        files = [f for f in files if not is_hidden(os.path.join(root, f))]
        
        for f in files:
            tree_str += '{}{}\n'.format(subindent, f)
    return tree_str

def main():
    # Current working directory
    current_dir = os.getcwd()
    
    # Create 'ai' directory if it doesn't exist
    ai_dir = os.path.join(current_dir, 'ai')
    if not os.path.exists(ai_dir):
        os.makedirs(ai_dir)
    
    # Get current datetime for filename
    now = datetime.datetime.now()
    filename = now.strftime('state-%Y-%m-%d-%H-%M-%S.txt')
    output_file_path = os.path.join(ai_dir, filename)
    
    with open(output_file_path, 'w', encoding='utf-8') as f:
        # Write the initial text
        f.write('Hello dear AI, please upgrade the application I have described in the below files and enhance it for\n')
        f.write('........................\n\n')
        
        # Generate the ASCII tree for current directory and write to file
        tree = generate_ascii_tree(current_dir)
        f.write(tree)
        
        # Then write the contents of all files within the current directory
        for root, dirs, files in os.walk(current_dir):
            dirs[:] = [d for d in dirs if not is_hidden(os.path.join(root, d))]
            files = [f_name for f_name in files if not is_hidden(os.path.join(root, f_name))]
            for file in files:
                full_file_path = os.path.join(root, file)
                # Skip the output file itself if it's inside the current directory
                if os.path.abspath(full_file_path) == os.path.abspath(output_file_path):
                    continue
                try:
                    with open(full_file_path, 'r', encoding='utf-8', errors='ignore') as content_file:
                        relative_path = os.path.relpath(full_file_path, current_dir)
                        f.write(f'\n\n--- Start of {relative_path} ---\n\n')
                        f.write(content_file.read())
                        f.write(f'\n\n--- End of {relative_path} ---\n\n')
                except Exception as e:
                    relative_path = os.path.relpath(full_file_path, current_dir)
                    f.write(f'\n\n--- Could not read {relative_path}: {e} ---\n\n')

    print(f"State file generated at: {output_file_path}")

if __name__ == '__main__':
    main()
    