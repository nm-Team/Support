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
                # Check if we should add contributing note
                if not should_hide_contributing_note(metadata, doc_path, doc):
                    # Read original file content
                    with open(f"{path}/{doc}", 'r', encoding='UTF-8', errors='ignore') as f:
                        original_content = f.read()

                    # Split content into metadata and body
                    if original_content.startswith("---"):
                        parts = original_content.split("---", 2)
                        if len(parts) >= 3:
                            metadata_part = f"---{parts[1]}---"
                            body_part = parts[2]
                        else:
                            metadata_part = ""
                            body_part = original_content
                    else:
                        metadata_part = ""
                        body_part = original_content

                    # Find the first heading and insert contributing note after it
                    lines = body_part.split('\n')
                    heading_found = False
                    insert_index = 0

                    for i, line in enumerate(lines):
                        if line.strip().startswith('#'):
                            heading_found = True
                            insert_index = i + 1
                            break

                    if heading_found:
                        # Insert contributing note after the heading
                        contributing_note = generate_contributing_note(
                            doc_path)
                        lines.insert(insert_index, contributing_note)
                        modified_body = '\n'.join(lines)
                    else:
                        # If no heading found, insert at the beginning
                        contributing_note = generate_contributing_note(
                            doc_path)
                        modified_body = contributing_note + body_part

                    # Write modified content to cache
                    modified_content = metadata_part + modified_body
                    with open(f"cache/{path_relative}/{doc}", 'w', encoding='UTF-8', errors='ignore') as f:
                        f.write(modified_content)
                else:
                    # Just copy the file as is
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
            sub_parent_index = sub[3]
            if sub_folder:
                # add yaml tab
                space_count = len(path.split("/"))
                space = ""
                for i in range(space_count):
                    space += "  "
                sub_folder = space + sub_folder.replace("\n", f"\n{space}")
                # remove the last space
                sub_folder = sub_folder[:-len(space)]
                sub_yaml = f"  - {sub_index_title}:\n{sub_folder}"
                # Read the
                # Add to index list
                index_dir_list.append({"title": sub_index_title,
                                       "description": sub_index_description,
                                       "path": f"{path}/{doc}",
                                       "metadata": "",
                                       "doc": doc,
                                       "index": sub_parent_index,
                                       "type": "folder",
                                       "yaml": sub_yaml})

        else:
            # Copy the file to cache
            shutil.copyfile(f"{path}/{doc}",
                            f"cache/{path_relative}/{doc}")

    # Sort index_dir_list, folders first
    index_dir_list.sort(key=lambda x: x["type"], reverse=True)
    # Sort index_dir_list by index, keep original order if index is the same
    index_dir_list_index_sorted = sorted(
        index_dir_list, key=lambda x: (x["index"], index_dir_list.index(x)))
    print(f"index_dir_list: {index_dir_list_index_sorted}")

    index_dir_list = index_dir_list_index_sorted

    # Generate yaml
    for i in index_dir_list:
        if i["type"] == 'folder':
            yaml += i["yaml"]
            continue
        elif i["doc"] == "index.md":
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
    index_content_default = f"# {index_title}\n\
{index_description}\n"
    index_content = ""

    # If has index.md, copy its content
    hide_navigation = False
    parent_index = 0
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
                metadata = "".join(lines[1:i])

                # If has navigation hide
                if re.search(r"- navigation", metadata):
                    hide_navigation = True

                # If has parent index
                if re.search(r"index: (.*)", metadata):
                    parent_index = int(re.search(
                        r"index: (.*)", metadata).group(1))

            else:
                index_content = all

    index_metadata = f"---\n\
automatically_generated: Don't edit this file directly, it's auto generated.\n\
title: {index_title}\n"
    index_metadata += """
hide:
  - toc\n"""
    # If page set hide navigation
    if hide_navigation:
        index_metadata += "  - navigation\n"
    index_metadata += "---\n\n"

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

    return (yaml, index_title, index_description, parent_index)


def generate_contributing_note(doc_path):
    """Generate contributing note HTML for a document"""
    github_edit_url = f"https://github.com/nm-Team/Support/edit/main/docs/{doc_path}"

    contributing_note = f'''
!!! tip "帮助我们改进此文档"
    发现文档有错误或需要改进的地方？您可以：

    - [在 GitHub 上直接编辑此页面]({github_edit_url})
    - [提交 Issue 报告问题](https://github.com/nm-Team/Support/issues/new)
    - [加入我们的讨论](https://github.com/nm-Team/Support/discussions)

    您的贡献将帮助更多用户获得更好的体验！

'''
    return contributing_note


def should_hide_contributing_note(metadata, doc_path, doc_name):
    """Check if contributing note should be hidden for this document"""
    # Check if metadata contains Hide Contributing Note
    if metadata and re.search(r"hideContributingNote", metadata, re.IGNORECASE):
        return True

    # Check if it's an index.md file
    if doc_name == "index.md":
        return True

    # Define excluded path patterns (regex patterns)
    excluded_patterns = [
        r"^legal/",      # Files directly in legal folder
        r"/legal/",      # Files in any legal subfolder
        r"/update-log/",  # Files in update-log folder
        # Add more patterns here as needed
    ]

    # Check if the document path matches any excluded pattern
    for pattern in excluded_patterns:
        if re.search(pattern, doc_path):
            return True

    return False


if __name__ == "__main__":
    generate()
