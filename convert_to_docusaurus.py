import os
import re

path = os.getcwd()

files = []
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        if '.md' in file:
            files.append(os.path.join(r, file))

for f in files:
    print(f)
    # Read contents from file
    with open(f, 'r') as original: contents = original.read()
    
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
    
    # Derive relative path and create id
    # Deprecated with Docusaurus v2
    #
    # splitat = len(path) + 1
    # relative_path = f[splitat:]
    # id = re.sub(r'\\', '-', relative_path) # replace '\\' with '/' on Mac or Linux

    # With Docusaurus v2, the id is just the filename minus the filetype.
    derive_id_from_filename = re.findall(r'(.*\\)(.*)(.md)', f)
    id = str(derive_id_from_filename[0][1])

    # Generate Prepend string
    prependString = "---\n" + "id: " + id + "\ntitle: " + doc_title + "\n---\n\n"
    print(prependString)
    
    # write to file
    with open(f, 'w') as modified: modified.write(prependString + contents)

