from src.index.semantic_searcher import SemanticSearcher

searcher = SemanticSearcher()
results = searcher.search("employee compensation policy")

for r in results:
    print(f"[{r['rank']}] {r['path']} (score={r['score']:.3f})")
