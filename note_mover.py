import os
import datetime
import json

# Used to add timestampts to log messages saved to files
def log_message(message):
	curr_time = datetime.datetime.now()
	curr_time = curr_time.strftime("%Y-%m-%d %H:%M")
	return curr_time + ' - ' + message + '\n'

def read_file_as_json(file):
	data = open(file, encoding='utf-8').read()
	data_as_json = json.loads(data)
	return(data_as_json)

READ_LINE_LIMIT = 20

# Creation of the log file
vault_root = input("Input vault root path: ")
os.chdir(vault_root)
source_folder = os.path.join(vault_root, '1_to_organize')
log_folder = os.path.join(vault_root, 'zc_script_logs')

datetime_now = datetime.datetime.now()
current_timestamp = datetime_now.strftime("%Y%m%d_%H%M")
current_date = datetime_now.strftime("%Y-%m-%d")
execution_log_file_path = os.path.join(log_folder, current_timestamp + '_python_file_mover.md' )
with open(execution_log_file_path, 'w') as execution_log:
	# Property header for log file
	execution_log.write(f"""---
	date: {current_date}
	note_type:
	  - script_log
	cssclasses:
	  - script_log
	---
	Execution log:
	```log
	""")

# Loop that moves notes in '1_to_move' based on note_type property
config_file_path = os.path.join(vault_root, "za_vault_assets", "script_configs", "note_types.md")
NOTE_TYPE_FOLDERS = read_file_as_json(config_file_path)

file_list = [os.path.join(source_folder, file) for file in os.listdir(os.path.join(source_folder)) if os.path.isfile(os.path.join(source_folder, file))]

total_notes_moved = 0
notes_not_moved = []

with open(execution_log_file_path, 'w') as execution_log:
	execution_log.write(log_message(f"Starting note mover"))
	execution_log.write(f"Moves notes in '1_to_move' based on note_type property\n")
	execution_log.write(f"Config file can be found in /za_vault_assets/script_configs\n\n")


for file in file_list:
	file_name = os.path.basename(file)
	with open(file, encoding='utf-8') as opened_file:
		content = opened_file.read().splitlines()
	execution_log.write(log_message(f"'{file_name}' | ").replace("\n", ''))

	gitignored = False
# Checks if note should go into gitignored folder before moving it elsewhere
	for line_num, line_content in enumerate(content):
		if line_content == "---" and line_num > 2:
			# Reached the end of the properties block 
			break
		if line_content == "tags:":
			if content[line_num + 1] == "  - \"#gitignored\"":
				gitignored = True
				try:
					folder = "zb_gitignored"
					os.rename(file, os.path.join(vault_root, folder, file_name))
					execution_log.write(f"Sucessfully moved to '{folder}'\n")
					total_notes_moved += 1
					break
				except FileExistsError:
					execution_log.write(f"Could not move note. Note already exists in '{folder}'\n")
				except Exception as err:
					execution_log.write(str(type(err).__name__) + " | " + str(err) + "\n")
				notes_not_moved.append(f"'{file_name}' | Targeted folder: '{folder}'")
				break

# Moves notes if they're not gitignored
	if not gitignored:
		for line_num, line_content in enumerate(content):
			if line_content == "---" and line_num > 2:
				execution_log.write(f"Reached end of property block without finding property 'note_type'\n")
				notes_not_moved.append(f"'{file_name}' | Property note_type not found")
				break
			if line_num > READ_LINE_LIMIT:
				execution_log.write(f"Reached line {line_num} without finding property 'note_type'\n")
				notes_not_moved.append(f"'{file_name}' | Property note_type not found")
				break

			if line_content == 'note_type:':
				try: folder = NOTE_TYPE_FOLDERS[content[line_num + 1]]
				except:
					execution_log.write("Note type did not match any criteria\n")
					notes_not_moved.append(f"'{file_name}' | Note type found: '{content[line_num + 1]}'")
					break

				try:
					os.rename(file, os.path.join(vault_root, folder, file_name))
					execution_log.write(f"Sucessfully moved to '{folder}'\n")
					total_notes_moved += 1
					break
				except FileExistsError:
					execution_log.write(f"Could not move note. Note already exists in '{folder}'\n")
				except Exception as err:
					execution_log.write(str(type(err).__name__) + " | " + str(err) + "\n")
				notes_not_moved.append(f"'{file_name}' | Targeted folder: '{folder}'")
				break


execution_log.write('\n')
execution_log.write(log_message(f"End of notes\n"))
execution_log.write(log_message(f"Total notes moved: {total_notes_moved}"))
execution_log.write(log_message(f"Total notes not moved: {len(notes_not_moved)}\n\n"))


# Loop that moves attached files in folder 'za_vault_assets' to their subfolders based on file extensions
execution_log.write(log_message(f"Starting file mover"))
execution_log.write(f"Moves attached files in folder 'za_vault_assets' to their subfolders based on file extensions\n")
execution_log.write(f"Config file can be found in /za_vault_assets/script_configs\n\n")

config_file_path = os.path.join(vault_root, "za_vault_assets", "script_configs", "file_types.md")
FILE_TYPE_FOLDERS = read_file_as_json(config_file_path)

source_folder = os.path.join(vault_root, 'za_vault_assets')
file_list = [os.path.join(source_folder, file) for file in os.listdir(os.path.join(source_folder)) if os.path.isfile(os.path.join(source_folder, file))]

total_files_moved = 0
files_not_moved = []
for file in file_list:
	filename = os.path.basename(file) # Gets name of the file and discard
	file_extension = os.path.splitext(file)[1] # Splits file path into the file path and the extension with point, example: .pdf
	lowercase_file_extension = file_extension.lower()

	execution_log.write(log_message(f"'{filename}' | ").replace("\n", ''))

	try: folder = FILE_TYPE_FOLDERS[lowercase_file_extension]
	except:
		execution_log.write("File extension not in config file\n")
		files_not_moved.append(f"'{filename}' | File extension not found in config file")

	if folder == "ignore_file":
		continue

	try:
		os.rename(file, os.path.join(source_folder, folder, filename))
		execution_log.write(f"Sucessfully moved to '{folder}'\n")
		total_files_moved += 1
	except FileExistsError:
		execution_log.write(f"Could not move file. File already exists in '{folder}'\n")
	except Exception as err:
		execution_log.write(str(type(err).__name__) + " | " + str(err) + "\n")
		files_not_moved.append(f"'{filename}' | Targeted folder: '{folder}'")

# Cria task caso hajam notas que nao foram movidas
if len(notes_not_moved) >= 1 or len(files_not_moved) >= 1:

	execution_log.write(log_message(f"Creating task to check notes and files that were not moved"))
	task_note_path = os.path.join(vault_root, '0_inbox', current_timestamp + ' Verificar arquivos nao movidos.md')
	task_note = open(task_note_path, 'w')
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
  - "#generated_by_script"
aliases:
note_type:
  - task
cssclasses:
  - task
---

""")

	if len(notes_not_moved) >= 1:
		execution_log.write(log_message(f"List of notes not moved"))
		note_list_string = '\n'.join(notes_not_moved)
		execution_log.write(note_list_string)
		execution_log.write('\n\n')
		task_note.write(f"""### Lista de notas que nao foram movidas:
- [ ] """)
		note_list_checklist = '\n- [ ] '.join(notes_not_moved)
		task_note.write(note_list_checklist)

	if len(files_not_moved) >= 1:
		execution_log.write(log_message(f"List of files not moved"))
		file_list_string = '\n'.join(files_not_moved)
		execution_log.write(file_list_string)
		execution_log.write('\n\n')
		task_note.write(f"""### Lista de arquivos que nao foram movidos:
- [ ] """)
		file_list_checklist = '\n- [ ] '.join(files_not_moved)
		task_note.write(file_list_checklist)

	task_note.close()

else:
	execution_log.write(log_message(f"All notes and files moved successfully"))

execution_log.write(log_message(f"End of script"))
execution_log.write(r"```")
execution_log.close()