from src.config.db import get_db

COLLECTION = "visual_elements"

async def insert_visual_elements(elements: list[dict]):
    db = get_db()
    if elements:
        await db[COLLECTION].insert_many(elements)

async def delete_by_pdf(pdf_name: str):
    db = get_db()
    await db[COLLECTION].delete_many({"pdf_name": pdf_name})

async def get_visuals_by_pdfs(pdf_names: list[str]):
    db = get_db()
    cursor = db[COLLECTION].find({"pdf_name": {"$in": pdf_names}})
    return await cursor.to_list(length=2000)
