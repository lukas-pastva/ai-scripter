import os
import datetime

def generate_ascii_tree(startpath):
    tree_str = ''
    for root, dirs, files in os.walk(startpath):
        # Determine the relative path from startpath
        relpath = os.path.relpath(root, startpath)
        if relpath == '.':
            relpath = ''
        # Determine the level (depth) in the directory tree
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * level
        dirname = os.path.basename(root)
        tree_str += '{}{}/\n'.format(indent, dirname)
        subindent = ' ' * 4 * (level + 1)
        
        # Determine if we are in 'Src' or under it
        path_parts = os.path.normpath(root).split(os.sep)
        if 'Src' in path_parts:
            # Include hidden files and dirs
            pass  # Do nothing
        else:
            # Exclude hidden files and dirs
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            files = [f for f in files if not f.startswith('.')]
        for f in files:
            tree_str += '{}{}\n'.format(subindent, f)
    return tree_str

def main():
    # Create 'ai' directory if it doesn't exist
    if not os.path.exists('ai'):
        os.makedirs('ai')
    
    # Get current datetime for filename
    now = datetime.datetime.now()
    filename = now.strftime('state-%Y-%m-%d-%H-%M-%S.txt')
    output_file_path = os.path.join('ai', filename)
    
    with open(output_file_path, 'w', encoding='utf-8') as f:
        # Write the initial text
        f.write('Hello dear AI, please upgrade the application I have described in below files and enhance it for\n')
        f.write('........................\n\n')
        
        # Generate the ascii tree and write to file
        tree = generate_ascii_tree('.')
        f.write(tree)
        
        # Then write the contents of all files
        for root, dirs, files in os.walk('.'):
            # Determine if we are in 'Src' or under it
            path_parts = os.path.normpath(root).split(os.sep)
            if 'Src' in path_parts:
                # Include hidden files and dirs
                pass  # Do nothing
            else:
                # Exclude hidden files and dirs
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                files = [f for f in files if not f.startswith('.')]
            for file in files:
                full_file_path = os.path.join(root, file)
                # Skip the output file itself
                if os.path.abspath(full_file_path) == os.path.abspath(output_file_path):
                    continue
                try:
                    with open(full_file_path, 'r', encoding='utf-8', errors='ignore') as content_file:
                        f.write(f'\n\n--- Start of {full_file_path} ---\n\n')
                        f.write(content_file.read())
                        f.write(f'\n\n--- End of {full_file_path} ---\n\n')
                except Exception as e:
                    f.write(f'\n\n--- Could not read {full_file_path}: {e} ---\n\n')
    
if __name__ == '__main__':
    main()
