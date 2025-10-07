import os

from whoosh import index
from whoosh.fields import Schema, TEXT, ID

def create_or_open_index(index_dir="indexdir"):
    """
    Create or open a Whoosh index directory.
    """
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)

    schema = Schema(
        path=ID(stored=True, unique=True),
        content=TEXT(stored=True)
    )

    if not index.exists_in(index_dir):
        idx = index.create_in(index_dir, schema)
    else:
        idx = index.open_dir(index_dir)
    return idx


def add_to_index(pdf_path: str, text: str, index_dir="indexdir"):
    """
    Add a PDF's text content to the Whoosh index.
    """
    idx = create_or_open_index(index_dir)
    writer = idx.writer()
    writer.update_document(path=pdf_path, content=text)
    writer.commit()
    print(f"[INDEXED] {os.path.basename(pdf_path)}")
