import glob
import pathlib
import shutil
import os
import stat
import time


def has_hidden_attribute(filepath):
    return bool(os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)


def clean_hidden_files(file_list):
    cleaned_list = []
    # avoid hidden windows sys files
    for item in file_list:
        if not has_hidden_attribute(item):
            cleaned_list.append(item)
    return cleaned_list


def rmv_list_dupe(x):
    return list(dict.fromkeys(x))


def is_matching_dir(src, dst):
    if src == dst[:-2]:
        return True
    else:
        return False


def gen_ext_list(file_list, incl_folders_ans):
    extensions = []
    for item in file_list:
        file_name = os.path.basename(item)
        file_extension = pathlib.Path(file_name).suffixes
        extensions.append(''.join(file_extension))
    extensions = rmv_list_dupe(extensions)  # clean list before creating dir

    if incl_folders_ans:
        return extensions
    else:
        return extensions.remove('')


def incl_folders():
    ans = input("\nInclude folders ('y' or 'n'): ").lower()
    while ans != 'y' or ans != 'n':
        if ans == 'y':
            return True
        elif ans == 'n':
            return False
        ans = input("Please enter 'y' or 'n': ").lower()


def gen_ext_dir(dst, extensions):
    if len(extensions) > 0:
        new_dir_names = []
        curr_dir_names = []
        for ext in extensions:
            try:
                path = os.path.join(dst, ext)
                os.mkdir(path)
                new_dir_names.append(ext)
            except FileExistsError:
                curr_dir_names.append(ext)
        if len(new_dir_names) > 0:
            print(f'\tNewly created subfolders {new_dir_names}')
        elif len(curr_dir_names) > 0:
            if len(curr_dir_names) != 1 and curr_dir_names.count('') != 1:
                print(f'\tExisting subfolders {curr_dir_names}')
    else:
        print("\tDirectories remain unchanged due to lack of files.")


def move_files(src, dst, extensions):
    moved_files = []
    for ext in extensions:
        moved_files.clear()
        file_list = glob.glob(src + "\*" + ext)
        file_list = clean_hidden_files(file_list)
        for item in file_list:
            file_name = os.path.basename(item)
            # line below stops us from pre-emptively sorting longer extensions
            full_ext = ''.join(pathlib.Path(file_name).suffixes)
            if ext == full_ext:
                subdir_path = os.path.join(dst, ext)
                subdir_path += r'\\'
                file_path = os.path.join(subdir_path, file_name)
                shutil.move(item, file_path)
                moved_files.append(file_name)
        if ext != '':
            print(f'\t{ext} files moved: {moved_files}')
        elif ext == '' and is_matching_dir(src, dst):
            print(f'\n\tFolders remain as-is...')
        elif ext == '':
            print(f'\tFolders moved: {moved_files}')


def move_files_persistent(src, dst):
    scan_time = int(input("Scan Interval (sec): "))
    print(f"\nTransferring files from {src} to {dst} every {scan_time} seconds...")
    scan_count = 2
    incl_folders_ans = incl_folders()
    while True:
        file_list = glob.glob(src + '\*')
        file_list = clean_hidden_files(file_list)
        extensions = gen_ext_list(file_list, incl_folders_ans)

        gen_ext_dir(dst, extensions)
        move_files(src, dst, extensions)

        time.sleep(scan_time)
        print(f"\t\nInitiating Scan #{scan_count}...")
        scan_count += 1


def move_files_single(src, dst):
    file_list = glob.glob(src + '\*')
    file_list = clean_hidden_files(file_list)
    incl_folders_ans = incl_folders()
    extensions = gen_ext_list(file_list, incl_folders_ans)

    if is_matching_dir(src, dst):
        print(f'\nSorting {src}...')
    else:
        print(f"\nTransferring files from {src} to {dst}...")

    try:
        if len(extensions) > 0:
            gen_ext_dir(dst, extensions)
            move_files(src, dst, extensions)
        else:
            print("\nNo files found in directory.")
    except TypeError:
        print("\n\tNo files found in directory.")
    print("\nExiting program.")
    time.sleep(5)


print('''
Welcome to a basic tool which will move and/or sort files based on extension.
\n\tKey Notes: 
\t\tFolders are preserved, files in subfolders remain unaffected.
\t\tIf source and destination are set to the same location, that folder will be sorted.
\t\tHidden files are ignored in this script.
\t\tIf you hold any doubts that manipulating a folder may cause future problems, please express due caution.''')

print(r'''
Example Input: C:\Users\[user]\Downloads
''')

# path entry
src_dir = input(r'Enter Windows path of source folder: ')
dst_dir = input(r'Enter Windows path of destination folder: ')

while not os.path.exists(src_dir) and not os.path.exists(dst_dir):
    src_dir = input(r'Please enter a valid source path: ')
    dst_dir = input(r'Please enter a valid destination path: ')


# # OPTIONAL: insert values (e.g., c:\Users\[user]\Downloads)
# src_dir = r"[insert]"
# dst_dir = r"[insert]"

# easier implementation rather than asking user to append backslash to directory path
dst_dir += r"\\"

# define scan type
scan_type = input("\nPersistent ('p') or Single ('s') Scan: ").lower()
while scan_type != 'p' or scan_type != 's':
    if scan_type == 'p':
        move_files_persistent(src_dir, dst_dir)
        break
    elif scan_type == 's':
        move_files_single(src_dir, dst_dir)
        break
    scan_type = input("Please enter either 'p' or 's': ")
