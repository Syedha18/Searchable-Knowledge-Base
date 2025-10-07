import sys
from src.index.searcher import search_query
from src.index.semantic_searcher import SemanticSearcher
from src.index.semantic_indexer import SemanticIndexer

BANNER = """
==========================================
 🔍  Enterprise PDF Search CLI
==========================================
Commands:
  [1] Keyword Search
  [2] Semantic Search
  [3] Add new PDFs to semantic index
Type 'exit' or 'quit' to leave.
------------------------------------------
"""

def run_cli(keyword_index_dir="indexdir", semantic_index_dir="semantic_index"):
    print(BANNER)

    semantic_searcher = None
    indexer = SemanticIndexer(index_dir=semantic_index_dir)

    while True:
        try:
            cmd = input("Select mode/command (1,2,3) > ").strip()
            if cmd.lower() in {"exit", "quit"}:
                print("\n👋 Exiting CLI...")
                break

            # Add new PDFs
            if cmd == "3":
                folder = input("Folder path with new PDFs > ").strip()
                if not folder:
                    folder = "data"
                indexer.add_documents_batch(folder)
                semantic_searcher = SemanticSearcher(index_dir=semantic_index_dir)
                continue

            # Keyword search
            if cmd == "1":
                query = input("🔎  Keyword Query > ").strip()
                if not query:
                    continue
                results = search_query(query, index_dir=keyword_index_dir, limit=5)
                if not results:
                    print("⚠️  No results found.\n")
                    continue
                print(f"\n✅ Found {len(results)} result(s) [Keyword Search]:")
                for i, r in enumerate(results, 1):
                    print(f"\n[{i}] {r['path']}")
                    print(f"Snippet: {r['snippet'][:300]}...\n")
                continue

            # Semantic search
            if cmd == "2":
                if semantic_searcher is None:
                    try:
                        semantic_searcher = SemanticSearcher(index_dir=semantic_index_dir)
                    except FileNotFoundError as e:
                        print(f"[ERROR] {e}\nRun option 3 to add PDFs first.")
                        continue
                query = input("🔎  Semantic Query > ").strip()
                if not query:
                    continue
                results = semantic_searcher.search(query, top_k=5)
                if not results:
                    print("⚠️  No results found.\n")
                    continue
                print(f"\n✅ Found {len(results)} result(s) [Semantic Search]:")
                for r in results:
                    print(f"[{r['rank']}] {r['path']} (score={r['score']:.3f})")
                continue

            print("[WARN] Invalid option. Choose 1,2,3, or type 'exit'.\n")

        except KeyboardInterrupt:
            print("\n👋 Exiting CLI...")
            break
        except Exception as e:
            print(f"[ERROR] {e}\n")


if __name__ == "__main__":
    keyword_dir = sys.argv[1] if len(sys.argv) > 1 else "indexdir"
    semantic_dir = sys.argv[2] if len(sys.argv) > 2 else "semantic_index"
    run_cli(keyword_dir, semantic_dir)
