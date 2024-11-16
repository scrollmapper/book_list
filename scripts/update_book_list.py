import os
import json


"""
Updates the book list from the scrollmapper repos.

This function fetches the latest book list from the scrollmapper repositories
and updates the local database with the new entries. It ensures that the local
book list is synchronized with the remote repositories, adding any new books and
removing any that are no longer present in the repository.

To run this, you must have the scrollmapper repositories cloned to your local machine,
with the two repos in the same directory as the book_list repo.

The two main source examples:

../bible_databases/sources/en/KJV/KJV.json
../bible_databases_deuterocanonical/sources/en/1-enoch/1-enoch.json

Every book follows the same location format:

../bible_databases/sources/<language>/<book>/<book>.json
../bible_databases_deuterocanonical/sources/<language>/<book>/<book>.json

These are the same as:

https://github.com/scrollmapper/bible_databases/sources/<language>/<book>/<book>.json
https://github.com/scrollmapper/bible_databases_deuterocanonical/sources/<language>/<book>/<book>.json

The book_list.json contains the following information recorded like so:

    [
        {
            "language": "en",
            "book": "KJV",
            "title": "King James Version",
            "source": "KJV.json"
        },
        {
            "language": "en",
            "book": "1-enoch",
            "title": "1 Enoch",
            "source": "1-enoch.json"
        }
    ]

This should allow your software to easily access the bibles and deuterocanonical books with necessary meta information.    

Please note that the bibles in the bible databases consist of many books: Genesis, Exodus, Leviticus, etc.
The deuterocanonical books consist of books like 1-enoch, 2-esdras, etc.

What this script does:

This script iterates recursively through the bible_databases and bible_databases_deuterocanonical source directories to 
find each <book>.json file. It reads the language abbreviation from the <language> part of the path, the book from the <book> 
part of the path, and the title from the actual <book>.json file. The source is the link to the <book>.json file
itself online. It then updates the book_list.json file with this information.

Returns:
    None
"""

def update_book_list():
    base_dirs = [
        "../../bible_databases/sources",
        "../../bible_databases_deuterocanonical/sources"
    ]
    book_list = []

    for base_dir in base_dirs:
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith(".json"):
                    language = os.path.basename(os.path.dirname(root))
                    book = os.path.basename(root)
                    if file == f"{book}.json":
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            title = data.get("name", book)
                            repo_name = "bible_databases_deuterocanonical" if "bible_databases_deuterocanonical" in base_dir else "bible_databases"
                            source = f"https://raw.githubusercontent.com/scrollmapper/{repo_name}/refs/heads/master/sources/{language}/{book}/{file}"
                            
                            if "README.md" in files:
                                with open(os.path.join(root, "README.md"), 'r', encoding='utf-8') as readme_file:
                                    for line in readme_file:
                                        if line.startswith("# "):
                                            title = line[2:].strip()
                                            break
                            
                            book_list.append({
                                "language": language,
                                "book": book,
                                "title": title,
                                "source": source
                            })
                
    with open("../book_list.json", 'w', encoding='utf-8') as f:
        json.dump(book_list, f, ensure_ascii=False, indent=4)

def build_markdown_link_list():
    with open("../book_list.json", 'r', encoding='utf-8') as f:
        book_list = json.load(f)

    biblical_books = []
    deuterocanonical_books = []

    for book in book_list:
        entry = f"[{book['book']}: {book['title']} ({book['language']})]({book['source']})"
        if "deuterocanonical" in book['source']:
            deuterocanonical_books.append(entry)
        else:
            biblical_books.append(entry)

    with open("../readme/0_Intro.md", 'r', encoding='utf-8') as f:
        intro_content = f.read()

    with open("../readme/1_Other.md", 'r', encoding='utf-8') as f:
        other_content = f.read()

    with open("../README.md", 'w', encoding='utf-8') as f:
        f.write(intro_content + "\n\n")
        f.write("## Deuterocanonical Books\n")
        f.write("\n".join(deuterocanonical_books) + "\n\n")
        f.write("## Biblical Books\n")
        f.write("\n".join(biblical_books) + "\n\n")
        f.write(other_content)



if __name__ == "__main__":
    update_book_list()
    build_markdown_link_list()