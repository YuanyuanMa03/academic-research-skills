# Workflow 3: MeSH Search Strategy

**Purpose:** Build precise PubMed queries from MeSH terms.

## Procedure

1. Use `lookup_mesh(term="...")` to explore terms related to the topic.
2. Show term hierarchy (broader / narrower / related).
3. Construct Boolean query: MeSH terms + keywords.
   See [Query Construction](../search-strategy.md#query-construction) for templates.
4. Execute via `search_papers(query=..., sources=["pubmed"])`.

## Output

Final PubMed query string, result count, and top results.
