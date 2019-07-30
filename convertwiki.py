import os
import re
import json
import copy

path = os.getcwd()

#### Add Docusaurus headers to Docsify documents ####

files = []
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        if '.md' in file:
            files.append(os.path.join(r, file))

for f in files:
    print(f)
    # Read contents from file
    with open(f, 'r', encoding="utf8", errors="ignore") as original: contents = original.read()
    
    # Find first heading and discard Markdown syntax
    titles = re.findall(r'(#+ )(.*)(\n$)', contents, re.M)

    if len(titles) > 0:
        doc_title = str(titles[0][1])

        # Delete markdown title from contents
        markdown_title = str(titles[0][0]) + str(titles[0][1]) + str(titles[0][2])
        print(markdown_title)
        contents = re.sub(markdown_title, '', contents)

    else:
        # Use file name as title if there's no heading
        derive_title_from_filename = re.findall(r'(.*\\)(.*)(.md)', f)  
        doc_title = str(derive_title_from_filename[0][1])
    
    # With Docusaurus v2, the id is just the filename minus the filetype.
    derive_id_from_filename = re.findall(r'(.*\\)(.*)(.md)', f)
    id = str(derive_id_from_filename[0][1])

    # Generate Prepend string
    prependString = "---\n" + "id: " + id + "\ntitle: " + doc_title + "\n---\n\n"
    print(prependString)
    
    # write to file
    with open(f, 'w', encoding="utf8", errors="ignore") as modified: modified.write(prependString + contents)


#### Convert sidenav.md to sidebar.json ####

sidenav_location = os.path.join(path, 'sidenav.md')

## Read name and location from sidenav.md
# with open(f, 'sidenav.md') as source_sidenav: sidenav_dump = source_sidenav.read()
# sidenav_items = sidenav_dump.splitlines()

sidenav_items = [line.rstrip('\n') for line in open('sidenav.md')]

sidebars_json = { "wiki": { 'Wiki' : [ ] } }

category_dict = { 
        "type":"subcategory",
        "label":"",
        "ids":[ ]
        }

for sidenav_item in sidenav_items:
    
    # is the sidenav item a title? If so, add title to the category_dict label field
    if re.search(r'(#+ )(.*)', sidenav_item):  
        title = re.match(r'(#+ )(.*)', sidenav_item)
        print('\n')
        print(title.group(2))

        # if category_dict['ids'] has contents, copy to sidebars_json and flush contents 
        if len(category_dict['ids']) > 0:
            sidebars_json['wiki']['Wiki'].append(copy.deepcopy(category_dict))
            category_dict['ids'] = [ ]

        ## add title to the category_dict label field
        category_dict['label'] = title.group(2)
        print(json.dumps(category_dict))
        continue

    # If not, extract doc name and doc path if item is a Markdown link 
    elif re.search(r'.*\[(.*)\]\((.*)\)', sidenav_item):  
        content_link = re.match(r'.*\[(.*)\]\((.*)\)', sidenav_item)
        print(content_link.group(1))
        relative_path = content_link.group(2)
        print(relative_path)

        # create relative_path_to_id (remove filename from relative path)
        relative_path_to_id = ""
        
        if '/' in relative_path: # re.search(r'/', relative_path):
            slash_iter = re.finditer(r"/", relative_path)
            slash_positions = [m.start(0) for m in slash_iter]
            location_of_last_slash = slash_positions[len(slash_positions) - 1] + 1
            print('location of last slash: ', location_of_last_slash)
            relative_path_to_id = relative_path[:location_of_last_slash]
            print('relative path to id: ', relative_path_to_id)
        
        # convert relative path to absolute
        current_working_dir = os.getcwd()
        absolute_path = os.path.join(current_working_dir, relative_path)

        # convert URL slash to Windows backslash
        absolute_path = re.sub('/', r'\\', absolute_path)

        print(absolute_path)
        
        # clean up paths
        if 'http' in absolute_path: continue
        if '?' in absolute_path:
            path_with_anchor = re.match(r'(.*)(\?.*)', absolute_path)
            absolute_path = path_with_anchor.group(1)

        with open(absolute_path, 'r', encoding='utf8') as document: contents = document.read()
        
        # if re.search(r'(---.*id:\W*)(.*)(title:\W)(.*)(---)', contents):
        docusaurus_header = re.match(r'(\W*---\W*\n)(\W*id:\W*)(.*)(\W*\n)(\W*title:\W*)(.*)(\n)', contents)
        document_id = relative_path_to_id + docusaurus_header.group(3)
        document_title = docusaurus_header.group(6)

        print('Document id: ', document_id)
        print('Document title: ', document_title)
        print('\n')

        # Append Document id to category_dict['ids']
        category_dict['ids'].append(document_id)
        print(json.dumps(category_dict))
        print('\n')


# print resulting sidebars_json

print(json.dumps(sidebars_json, indent=4))

