import os
import datetime
import json
import shutil
import glob
from tkinter import filedialog
import fileinput

def prompt_directory() -> str | None:
    directory = filedialog.askdirectory(title="Select the folder root")
    if directory:
        return directory
    else:
        return None

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

def remove_line_from_file(file: str, text_to_remove: str, encoding="utf-8"):
    for line in fileinput.input(file, inplace=True, encoding=encoding):
        if line != text_to_remove:
            print(line, end="")

def remove_property_value(file: str, property: str, value_to_remove: str, encoding="utf-8"):
    property_line = property + ':\n'
    value_line = '  - ' + value_to_remove + '\n'
    property_found = False

    for line in fileinput.input(file, inplace=True, encoding=encoding):
        if line == property_line:
            property_found = True
        if property_found == True and line == value_line: # Guarantees we're skipping the first value right after finding the property
            property_found = False # Prevents removing the value if it's found again
            continue
        print(line, end="")


def insert_line_after(
    file: str,
    insert_after: str,
    inserted_line: str,
    only_once: bool = True,
    encoding: str = "utf-8",
):
    inserted = False

    for line in fileinput.input(file, inplace=True, encoding=encoding):
        print(line, end="")
        if not inserted and line == insert_after:
            print(inserted_line)
            if only_once:
                inserted = True

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

if __name__ == '__main__':
    root_folder = prompt_directory()
    file_list = get_all_files_with_extension(root_folder, extension='.md')

    for file in file_list:
        try:
            header = get_note_header(file)
            parsed_header = parse_header(header)
        except Exception as err:
            print(f"Couldn't get header from {file}")
            continue
        try:
            note_tags = parsed_header['tags']
        except Exception as err:
            print(f"Couldn't get tags from {file}")
            continue

        remove_property_value(file, 'tags', 'Confi')