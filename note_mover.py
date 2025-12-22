import os
import datetime
import json
import shutil
import glob
from tkinter import filedialog

# Used to add timestampts to log messages saved to files
def create_log_file_with_headers(vault_root: str, vault_structure: str) -> str:
    if vault_structure == 'single_vault':
        log_folder = os.path.join(vault_root, 'zc_script_logs')
    else:
        log_folder = os.path.join(vault_root, 'obs_0','zc_script_logs')
    datetime_now = datetime.datetime.now()
    current_timestamp = datetime_now.strftime("%Y%m%d_%H%M")
    current_date = datetime_now.strftime("%Y-%m-%d")
    execution_log_file_path = os.path.join(log_folder, current_timestamp + '_python_file_mover.md' )
    with open(execution_log_file_path, 'w') as log_file:
        log_file.write(f"""---
date: {current_date}
note_type:
  - script_logs
cssclasses:
  - script_logs
---
Execution log:
```log
""")
    return execution_log_file_path
        
def write_to_log_file(message: str, filepath: str, add_timestamp: bool = False) -> None:
    if add_timestamp:
        treated_message = create_log_message(message)
    else:
        treated_message = message
    with open(filepath, 'a') as log_file:
        log_file.write(treated_message)

def create_log_message(message) -> str:
    curr_time = datetime.datetime.now()
    curr_time = curr_time.strftime("%Y-%m-%d %H:%M")
    return curr_time + ' - ' + message

def read_file_as_json(file) -> json:
    data = open(file, encoding='utf-8').read()
    data_as_json = json.loads(data)
    return(data_as_json)

def get_files_in_specific_folders(root_dir, target_folder_name: str) -> list[str]:
    """
    Walk through all subdirectories of root_dir and collect files
    inside folders whose name exactly matches target_folder_name.
    """
    matching_files = []

    for current_path, dirnames, filenames in os.walk(root_dir):
        # Check if the current folder name matches exactly
        if os.path.basename(current_path) == target_folder_name:
            for file in filenames:
                full_path = os.path.join(current_path, file)
                matching_files.append(full_path)

    return matching_files

def prompt_directory() -> str | None:
    directory = filedialog.askdirectory(title="Selet the vault root path")
    if directory:
        return directory
    else:
        return None
    
def check_vault_structure(vault_path: str) -> str:
    if '0_inbox' in os.listdir(vault_path):
        return 'single_vault'
    else:
        return 'multi_vault'
    
def get_note_header(file: str) -> list[str]:
    header_content = []
    with open(file, mode='r', encoding='utf-8') as f:
        file_content = f.read().splitlines()
    for line_num, line_content in enumerate(file_content):
        if line_num == 0:
            continue
        elif line_content == '---':
            break
        else:
            header_content.append(line_content)
    return header_content

def parse_header(header_content: list[str]) -> dict:
    result = {}
    current_key = None
    for line in header_content:
        line = line.rstrip()
        if not line.strip(): # Catches edge cases of empty lines
            continue
        if not line.startswith("  -"): # Catches new field
            current_key = line.replace(":", "")
            result[current_key] = []
        else:
            value = line.replace("  -", "").strip()
            result[current_key].append(value)
    return result

def move_file(file: str, vault_root: str, target_folder: str, file_name: str, log_file: str) -> str:
    try:
        shutil.move(file, os.path.join(vault_root, target_folder, file_name))
        write_to_log_file(f"Sucessfully moved to '{target_folder}'\n", log_file)
        return 'success'
    except FileExistsError:
        write_to_log_file(f"Could not move file. It already exists in '{target_folder}'\n", log_file)
        return 'file_already_exists'
    except Exception as err:
        write_to_log_file(str(type(err).__name__) + " | " + str(err) + "\n", log_file)
        return 'other error'

# Creation of the log file
vault_root = prompt_directory()
vault_structure = check_vault_structure(vault_root)
log_file = create_log_file_with_headers(vault_root, vault_structure)


if vault_structure == 'multi_vault':
    if os.path.exists(os.path.join(vault_root, 'obs_0', 'za_vault_assets', 'script_configs', 'vaults_list.md')):
        vaults_list_file = os.path.join(vault_root, 'obs_0', 'za_vault_assets', 'script_configs', 'vaults_list.md')
    else:
        matches = glob.glob(vault_root + '/**/za_vault_assets/script_configs/vaults_list.md', recursive=True)
        vaults_list_file = matches[0]
    with open(vaults_list_file, mode='r', encoding='utf-8') as f:
        vaults_list = f.read().splitlines()
else:
    vaults_list = None


total_notes_moved = 0
notes_not_moved = []

write_to_log_file(
    """Starting note mover

Moves notes in '0_inbox' to their respective vault if directory is a multi-vault instance
Moves notes in '1_to_organize' based on note_type property
Config files can be found in /za_vault_assets/script_configs of your vault

""",
    log_file)

write_to_log_file("Checking notes in 0_inbox\n", log_file, True)

if vault_structure == 'multi_vault':
    note_list = get_files_in_specific_folders(vault_root, '0_inbox')
    for file in note_list:
        if not file.endswith('.md'):
            continue
        file_name = os.path.basename(file)
        write_to_log_file(f"'{file_name}' | ".replace("\n", ''), log_file, True)
        note_header = get_note_header(file)
        parsed_header = parse_header(note_header)

        folder_prefix = ''
        if vaults_list:
            for vault in vaults_list:
                if vault in parsed_header['tags']:
                    folder_prefix = 'obs_' + vault
                else:
                    folder_prefix = 'obs_0'
        target_folder = os.path.join(folder_prefix, '0_inbox')
        result = move_file(file, vault_root, target_folder, file_name, log_file)
        if result == 'success':
            total_notes_moved += 1
        else:
            notes_not_moved.append(f"'{file_name}' | Targeted folder: '{target_folder}'")
else:
    write_to_log_file("No notes to move between inboxes\n\ns", log_file)

write_to_log_file("Checking notes in 1_to_organize\n", log_file, True)

note_list = get_files_in_specific_folders(vault_root, '1_to_organize')

for file in note_list:
    file_name = os.path.basename(file)


    write_to_log_file(f"'{file_name}' | ".replace("\n", ''), log_file, True)
    note_header = get_note_header(file)
    parsed_header = parse_header(note_header)

# Checks if note should go into gitignored folder before moving it elsewhere
    if 'gitignored' in parsed_header['tags']:
        folder = "zb_gitignored"
        folder_prefix = 'obs_1_Priv'
        target_folder = os.path.join(folder_prefix, folder)
        result = move_file(file, vault_root, target_folder, file_name, log_file)
        if result == 'success':
            total_notes_moved += 1
        else:
            notes_not_moved.append(f"'{file_name}' | Targeted folder: '{target_folder}'")
    else:
        if vault_structure == 'multi_vault':
            folder_prefix = 'obs_0'
        else:
            folder_prefix = ''

        if vaults_list:
            for vault in vaults_list:
                if vault in parsed_header['tags']:
                    folder_prefix = 'obs_' + vault
        
        note_type = parsed_header['note_type'][0]
        target_folder = os.path.join(folder_prefix, note_type)

        result = move_file(file, vault_root, target_folder, file_name, log_file)
        if result == 'success':
            total_notes_moved += 1
        else:
            notes_not_moved.append(f"'{file_name}' | Targeted folder: '{target_folder}'")
write_to_log_file('\n', log_file)
write_to_log_file('End of notes\n', log_file, True)

write_to_log_file(f"Total notes moved: {total_notes_moved}\n", log_file, True)
write_to_log_file(f"Total notes not moved: {len(notes_not_moved)}\n\n", log_file, True)

## Loop that moves attached files in folder 'za_vault_assets' to their subfolders based on file extensions
#write_to_log_file(f"Starting file mover", log_file)

#write_to_log_file(f"Moves attached files in folder 'za_vault_assets' to their subfolders based on file extensions\n", log_file)
#write_to_log_file(f"Config file can be found in /za_vault_assets/script_configs\n\n", log_file)
#
#config_file_path = os.path.join(vault_root, "za_vault_assets", "script_configs", "file_types.md")
#FILE_TYPE_FOLDERS = read_file_as_json(config_file_path)
#
#source_folder = os.path.join(vault_root, 'za_vault_assets')
#file_list = [os.path.join(source_folder, file) for file in os.listdir(os.path.join(source_folder)) if os.path.isfile(os.path.join(source_folder, file))]
#
#total_files_moved = 0
#files_not_moved = []
#for file in file_list:
#    filename = os.path.basename(file) # Gets name of the file and discard
#    file_extension = os.path.splitext(file)[1] # Splits file path into the file path and the extension with point, example: .pdf
#    lowercase_file_extension = file_extension.lower()
#
#    execution_log.write(create_log_message(f"'{filename}' | ").replace("\n", ''))
#
#    try: folder = FILE_TYPE_FOLDERS[lowercase_file_extension]
#    except:
#        execution_log.write("File extension not in config file\n")
#        files_not_moved.append(f"'{filename}' | File extension not found in config file")
#
#    if folder == "ignore_file":
#        continue
#
#    try:
#        shutil.move(file, os.path.join(source_folder, folder, filename))
#        execution_log.write(f"Sucessfully moved to '{folder}'\n")
#        total_files_moved += 1
#    except FileExistsError:
#        execution_log.write(f"Could not move file. File already exists in '{folder}'\n")
#    except Exception as err:
#        execution_log.write(str(type(err).__name__) + " | " + str(err) + "\n")
#        files_not_moved.append(f"'{filename}' | Targeted folder: '{folder}'")
# Cria task caso hajam notas que nao foram movidas
#if len(notes_not_moved) >= 1 or len(files_not_moved) >= 1:

if len(notes_not_moved) >= 1:
    write_to_log_file(f"Creating task to check notes and files that were not moved\n", log_file, True)
    datetime_now = datetime.datetime.now()
    current_timestamp = datetime_now.strftime("%Y%m%d_%H%M")
    current_date = datetime_now.strftime("%Y-%m-%d")
    if vault_structure == 'multi_vault':
        task_note_path = os.path.join(vault_root, 'obs_0', '0_inbox', current_timestamp + ' Verificar arquivos nao movidos.md')
    else:
        task_note_path = os.path.join(vault_root, '0_inbox', current_timestamp + ' Verificar arquivos nao movidos.md')
    with open(task_note_path, 'w') as task_note:
        task_note.write(f"""---
date: {current_date}
status: false
projects:
  - "[[This vault]]"
topics:
meetings:
tasks:
scope:
  - personal
tags:
  - "generated_by_script"
aliases:
note_type:
  - tasks
cssclasses:
  - tasks
---
""")

        if len(notes_not_moved) >= 1:
            write_to_log_file(f"List of notes not moved\n", log_file, True)

            note_list_string = '\n'.join(notes_not_moved)
            write_to_log_file(note_list_string, log_file)
            write_to_log_file('\n\n', log_file)
            task_note.write(f"### Lista de notas que nao foram movidas:\n- [ ] ")
            note_list_checklist = '\n- [ ] '.join(notes_not_moved)
            task_note.write(note_list_checklist)
#    if len(files_not_moved) >= 1:
#        write_to_log_file(f"List of files not moved", log_file, True)

#        file_list_string = '\n'.join(files_not_moved)
#        write_to_log_file(file_list_string)
#        write_to_log_file('\n\n')
#        task_note.write(f"""### Lista de arquivos que nao foram movidos:
#- [ ] """)
#        file_list_checklist = '\n- [ ] '.join(files_not_moved)
#        task_note.write(file_list_checklist)
else:
    write_to_log_file(f"All notes and files moved successfully\n", log_file, True)

write_to_log_file(f"End of script\n", log_file, True)
write_to_log_file(r"```", log_file)