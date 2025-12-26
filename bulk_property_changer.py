import os
import datetime
import json
import shutil
import glob
from tkinter import filedialog, messagebox
import fileinput
import difflib

def prompt_directory() -> str | None:
    directory = filedialog.askdirectory(title="Select the folder root")
    if directory:
        return directory
    else:
        return None
    
def ask_confirmation(message: str, title: str = "Confirm changes"):
    result = messagebox.askyesno(title, message)
    return result

def get_all_files_with_extension(directory: str, extension: str = '.md') -> list[str]:
    matches = []

    for root, dirs, files in os.walk(directory):
        for name in files:
            if name.endswith(extension):
                matches.append(os.path.join(root, name))
    return matches

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

def remove_line_from_file(file_path: str, text_to_remove: str, encoding="utf-8"):
    for line in fileinput.input(file_path, inplace=True, encoding=encoding):
        if line != text_to_remove:
            print(line, end="")

def remove_property_value(file_path: str, property: str, value_to_remove: str, encoding="utf-8"):
    property_line = property + ':\n'
    value_line = '  - ' + value_to_remove + '\n'
    property_found = False

    for line in fileinput.input(file_path, inplace=True, encoding=encoding):
        if line == property_line:
            property_found = True
        if property_found == True and line == value_line: # Guarantees we're skipping the first value right after finding the property
            property_found = False # Prevents removing the value if it's found again
            continue
        print(line, end="")


def insert_line_after(
    file_path: str,
    insert_after: str,
    inserted_line: str,
    only_once: bool = True,
    encoding: str = "utf-8",
):
    inserted = False

    for line in fileinput.input(file_path, inplace=True, encoding=encoding):
        print(line, end="")
        if not inserted and line == insert_after:
            print(inserted_line)
            if only_once:
                inserted = True

def create_temp_file_with_changes(file_path: str, old_text: str, new_text: str) -> str:
    with open(file_path, "r", encoding="utf-8") as src, \
         open(file_path + ".tmp", "w", encoding="utf-8") as dst:

        for line in src:
            dst.write(line.replace(old_text, new_text))
    return file_path


def diff_files(file_path: str):
    src_path = file_path
    dst_path = file_path + ".tmp"
    with open(src_path, "r", encoding="utf-8") as original_file, \
         open(dst_path, "r", encoding="utf-8") as new_file:

        src_lines = original_file.readlines()
        new_lines = new_file.readlines()

    diff = difflib.unified_diff(
        src_lines,
        new_lines,
        fromfile=os.path.basename(src_path),
        tofile=os.path.basename(dst_path)
    )
    return "".join(diff)

def push_file_changes_to_original(file_path: str) -> None:
    os.replace(file_path + ".tmp", file_path)

def replace_text_in_files(file_path: str, old_text: str, new_text: str, require_confirmation: bool = True) -> None:
    create_temp_file_with_changes(file_path, old_text, new_text)
    tmp_filepath = file_path + ".tmp"
    diff_result = diff_files(file_path)
    if diff_result:
        if require_confirmation:
            user_response = messagebox.askyesno('Confirm file changes', diff_result)
            if user_response:
                push_file_changes_to_original(file_path)
            else:
                if os.path.exists(tmp_filepath):
                    os.remove(tmp_filepath)
        else:
            push_file_changes_to_original(file_path)
    else:
        if os.path.exists(tmp_filepath):
            os.remove(tmp_filepath)
       

def get_note_header(file_path: str) -> list[str]:
    header_content = []
    with open(file_path, mode='r', encoding='utf-8') as f:
        file_content = f.read().splitlines()
    for line_num, line_content in enumerate(file_content):
        if line_num == 0:
            continue
        elif line_content == '---':
            break
        else:
            header_content.append(line_content)
    return header_content

if __name__ == '__main__':
    root_folder = prompt_directory()
    file_list = get_all_files_with_extension(root_folder, extension='.md')

    for f in file_list:
        replace_text_in_files(f, '\"meeting_note\"', '\"meeting_notes\"', require_confirmation=True)
        replace_text_in_files(f, '\"task\"', '\"tasks\"', require_confirmation=True)
        replace_text_in_files(f, '\"documentation_note\"', '\"documentation_notes\"', require_confirmation=True)
        replace_text_in_files(f, '\"general_note\"', '\"general_notes\"', require_confirmation=True)