# Generate nmTeam documentation.
# This script should be run before building the documentation.

import html
import os
import re
import shutil


def generate():
    # Generate the documentation.
    print("Generating documentation...")

    # Create cache folder. If exists delete it first
    if os.path.exists('cache'):
        shutil.rmtree('cache')
    os.mkdir('cache')

    yaml = ""

    # Read all the folders/files in /docs
    yaml += read('docs')[0]

    # Update mkdocs.yml, replacing content between "# NAV_ARIA_START" and "# NAV_ARIA_END"
    with open('mkdocs-template.yml', encoding='UTF-8', errors='ignore') as f:
        mkdocs = f.read()
        mkdocs = re.sub(r"# NAV_ARIA_START.*# NAV_ARIA_END",
                        f"# NAV_ARIA_START\n{yaml}# NAV_ARIA_END", mkdocs, flags=re.S)
    # Write the mkdocs.yml in cache
    with open('mkdocs.yml', 'w', encoding='UTF-8', errors='ignore') as f:
        f.write(mkdocs)

    # Copy cache to generated
    if os.path.exists('generated'):
        shutil.rmtree('generated')

    shutil.copytree('cache', 'generated')

    print("Documentation generated. ")


def read(path):
    path_relative = path.replace('docs/', '').replace('docs', '')
    yaml = ""
    index_dir_list = []
    docs = os.listdir(path)

    # Create path folder in cache
    if not os.path.exists(f"cache/{path_relative}"):
        os.makedirs(f"cache/{path_relative}")

    for doc in docs:
        # If the file is a markdown file
        if doc.endswith(".md"):
            # If is a normal markdown file
            # Try to read markdown metadata
            metadata = ""
            with open(f"{path}/{doc}", 'r', encoding='UTF-8', errors='ignore') as f:
                lines = f.readlines()
                # If the file is empty, skip
                if len(lines) == 0:
                    continue
                # If the file is not empty, read the metadata
                if lines[0].startswith("---"):
                    # If the file has metadata
                    i = 1
                    while not lines[i].startswith("---"):
                        i += 1
                    metadata = "".join(lines[1:i])
                else:
                    # If the file has no metadata
                    metadata = ""

            # Deal with data
            # Title
            if metadata and re.search(r"title: (.*)", metadata):
                title = re.search(r"title: (.*)", metadata).group(1)
            elif re.search(r"# (.*)", "".join(lines)):
                title = re.search(r"# (.*)", "".join(lines)).group(1)
            else:
                title = doc.replace(".md", "").replace("-", " ").title()

            # Description
            if metadata and re.search(r"description: (.*)", metadata):
                description = re.search(
                    r"description: (.*)", metadata).group(1)
            elif len(lines) > len(metadata) + 1:
                # else get 100 first characters after metadata
                description_lines = lines[len(metadata):]
                # Remove lines starting with #
                description_lines = [
                    line for line in description_lines if not line.startswith("#")]
                description = "".join(description_lines)
                # Remove special characters: []()#`>*_|
                description = re.sub(r"[\[\]\(\)#`>*_]|\|", "", description)
                i = 0
                while len(description) < 100 and len(metadata) < len(lines):
                    description += lines[len(metadata)]
                    i += 1
                description = description[:100]+'...'
            else:
                description = ""

            # Index
            if metadata and re.search(r"index: (.*)", metadata):
                index = int(re.search(r"index: (.*)", metadata).group(1))
            else:
                index = 0

            # For index.md
            hide_docs_list = False
            if doc == "index.md":
                hide_docs_list = re.search(r"hide_docs_list: (.*)", metadata) and re.search(
                    r"hide_docs_list: (.*)", metadata).group(1) == 'true'

            # Doc path, removing "docs/"
            doc_path = re.search(r"docs/(.*)", f"{path}/{doc}").group(1)

            # Add to index list
            index_dir_list.append({"title": title,
                                   "description": description,
                                   "path": doc_path,
                                   "metadata": metadata,
                                   "doc": doc,
                                   "index": index,
                                   "type": "doc",
                                   })

            # Copy the file to cache if is not index.md
            if doc != "index.md":
                shutil.copyfile(f"{path}/{doc}",
                                f"cache/{path_relative}/{doc}")
            else:
                print(f"index.md: {doc}")

        # If the file is a folder
        elif os.path.isdir(f"{path}/{doc}"):
            # If is the assets folder, skip
            if doc == "img":
                # Copy the folder to cache
                shutil.copytree(f"{path}/{doc}",
                                f"cache/{path_relative}/{doc}")
                continue
            # If is a normal folder
            sub = read(f"{path}/{doc}")
            sub_folder = sub[0]
            sub_index_title = sub[1]
            sub_index_description = sub[2]
            if sub_folder:
                # add yaml tab
                space_count = len(path.split("/"))
                space = ""
                for i in range(space_count):
                    space += "  "
                sub_folder = space + sub_folder.replace("\n", f"\n{space}")
                # remove the last space
                sub_folder = sub_folder[:-len(space)]
                yaml += f"  - {sub_index_title}:\n{sub_folder}"
                # Add to index list
                index_dir_list.append({"title": sub_index_title,
                                       "description": sub_index_description,
                                       "path": f"{path}/{doc}",
                                       "metadata": "",
                                       "doc": doc,
                                       "index": 0,
                                       "type": "folder"})

        else:
            # Copy the file to cache
            shutil.copyfile(f"{path}/{doc}",
                            f"cache/{path_relative}/{doc}")

    # Sort index_dir_list, folders first
    index_dir_list.sort(key=lambda x: x["type"], reverse=True)
    # Sort index_dir_list by index, keep original order if index is the same
    index_dir_list_index_sorted = []
    for i in range(len(index_dir_list)):
        # Append to matched index position of index_dir_list_index_sorted
        for j in range(len(index_dir_list_index_sorted)):
            if index_dir_list[j]["index"] > index_dir_list[i]["index"]:
                index_dir_list_index_sorted.insert(j, index_dir_list[i])
                break
        else:
            index_dir_list_index_sorted.append(index_dir_list[i])
    index_dir_list = index_dir_list_index_sorted

    # Generate yaml
    for i in index_dir_list:
        if i["type"] != 'doc' or i["doc"] == "index.md":
            continue
        yaml += f"  - {i['title']}: '{i['path']}'\n"

    # Generate index.md
    # Get index title from index.md if exists
    index_title = path.split("/")[-1]
    index_description = ""
    for i in index_dir_list:
        if i["doc"] == "index.md":
            index_title = i["title"]
            index_description = i["description"]
            break

    # Generate new index.md content
    index_metadata = f"---\n\
automatically_generated: Don't edit this file directly, it's auto generated.\n\
title: {index_title}\n"
    index_metadata += "---\n\n"
    index_content_default = f"# {index_title}\n\
{index_description}\n"
    index_content = ""

    # If has index.md, copy its content
    if os.path.exists(f"{path}/index.md"):
        with open(f"{path}/index.md", 'r', encoding='UTF-8', errors='ignore') as f:
            all = f.read()

            # Only copy content after metadata
            if all.startswith("---"):
                i = 1
                lines = all.split("\n")
                while not lines[i].startswith("---"):
                    i += 1
                # Only if has lines not empty
                for j in range(i+1, len(lines)):
                    if len(lines[j]) > 0:
                        index_content += "\n".join(lines[i+1:])
                        break

            else:
                index_content = all

    # If index.md has content, add to yaml
    if index_content:
        if path == 'docs':
            link = ''
        else:
            link = f"{path.replace('docs/', '')}/"
        yaml = f"  - {index_title}: '{link}index.md'\n" + yaml
    else:
        # If index.md has no content, use default content
        index_content = index_content_default.format(
            index_title=index_title, index_description=index_description)

    # Geneate index docs list
    docs_list_html = '\n\n\n<div class="docsList">'
    for i in index_dir_list:
        if i['doc'] == 'index.md':
            continue
        docs_list_html += '\n\
    <div class="docsItem">\n\
        <i class="icon {type}" aria-hidden="true"></i>\n\
        <div class="text">\n\
            <a class="link" href="{path}">{title}</a>\n\
            <p class="description">{description}</p>\n\
        </div>\n\
    </div>'.format(path=html.escape('/'+i['path'].replace('docs/', '').replace('.md', '')),
                   title=html.escape(i['title']),
                   description=html.escape(i['description']),
                   type=i['type'])
    docs_list_html += '\n</div>'

    if hide_docs_list != True:
        index_content += docs_list_html

    # Create index.md to cache
    with open(f"cache/{path_relative}/index.md", 'w', encoding='UTF-8', errors='ignore') as f:
        f.write(index_metadata + index_content)

    return (yaml, index_title, index_description)


if __name__ == "__main__":
    generate()
