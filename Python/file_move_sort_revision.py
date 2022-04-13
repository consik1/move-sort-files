import os
import pathlib
import re
import shutil
import stat


def has_hidden_attribute(filepath):
    """Returns True if a given file is recognized as hidden"""
    return bool(os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)


def input_directory_names():
    """Collects Path of source and destination directories from user"""
    src = input(r"Please enter absolute path of source folder: ")
    dst = input(r"Please enter absolute path of destination folder: ")
    while not os.path.isdir(src) or not os.path.isdir(dst):
        print(f"Source: {src}, Destination: {dst} are not valid directory paths.")
        src = input(r'Please enter a valid source path: ')
        dst = input(r'Please enter a valid destination path: ')
    return src, dst


def create_file_ext_dir(directory):
    """Generates dictionary which defines occurrences of extensions in a given directory"""
    src_files = os.listdir(directory)
    ext_dict = {}
    for file in src_files:
        if not has_hidden_attribute(os.path.join(directory, file)):
            file_ext = pathlib.Path(file).suffix
            ext_dict[file_ext] = ext_dict.get(file_ext, 0) + 1
    return ext_dict


def create_dst_dir_and_list(ext_dict, dst):
    """Make a new directory for each extension in a directory, and return their absolute paths"""
    new_dir_abs_paths = []
    for key in ext_dict.keys():
        if key == "":
            continue
        # sorted folder naming conventions defined here
        # note: changes here require an update to move_file regex expression
        folder_name = f"{key[1:]} Files"
        dir_path = os.path.join(dst, folder_name)
        new_dir_abs_paths.append(dir_path)
        try:
            os.mkdir(dir_path)
        except FileExistsError:
            continue
    return new_dir_abs_paths


def create_abs_path_list(directory):
    """Given a directory, return a list with the absolute path of each file"""
    abs_paths = []
    for f in os.listdir(directory):
        f = os.path.join(directory, f)
        abs_paths.append(f)
    return abs_paths


def move_file(filepath, dst, dst_dirs, dst_files):
    """Move a given file to its destination, accounting for duplicates"""
    was_moved = False
    # separate filepath into name and extension for later use
    split_filename = os.path.splitext(filepath)
    file_ext = split_filename[1]
    # take file's basename for quick comparison to existing files in destination directory
    file_name = os.path.basename(filepath)
    # handle folders separately first
    if file_ext == "":
        if file_name not in dst_files:
            folder_dst = os.path.join(dst, file_name)
            was_moved = True
            shutil.move(filepath, folder_dst)
    # compare file extension to newly created directories so we can insert into them
    for dst_folder in dst_dirs:
        find_ext = re.search(r"([\w-]*) [\w]*$", dst_folder)
        ext_to_match = find_ext[1]
        if file_ext[1:] == ext_to_match:
            try:
                shutil.move(filepath, dst_folder)
                was_moved = True
            except shutil.Error:
                pass
    return file_name, was_moved


def main():
    # define directories
    src_dir, dst_dir = input_directory_names()
    # create a dictionary of file extensions for directories
    src_dir_ext_dict = create_file_ext_dir(src_dir)
    # create lists of absolute paths for source folder files
    src_dir_file_list = create_abs_path_list(src_dir)
    # create directories to place sorted files into and store their absolute paths
    dst_dir_trim_file_list = create_dst_dir_and_list(src_dir_ext_dict, dst_dir)
    # iterate through files in source folder, moving to destination directory
    files_moved = []
    files_unmoved = []
    for file in src_dir_file_list:
        filename, move_successful = move_file(file, dst_dir, dst_dir_trim_file_list, os.listdir(dst_dir))
        files_moved.append(filename) if move_successful else files_unmoved.append(filename)
    print(f"{len(files_moved)} files/directories were transferred to '{dst_dir}' and sorted.\n{files_moved}")
    print(f"{len(files_unmoved)} files/directories were left unaffected, remaining at '{src_dir}'.\n{files_unmoved}")


main()
