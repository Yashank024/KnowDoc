import logging

logger = logging.getLogger("citation_service")

class CitationService:
    def format_citations(self, unique_docs: dict, retrieved_chunks: list) -> list:
        """
        Maps standard citation JSON envelopes for response mapping.
        """
        citations_output = []
        for filename, doc_idx in unique_docs.items():
            # Filter pages searched for this source
            pages_queried = []
            for c in retrieved_chunks:
                if c.get("filename") == filename:
                    pages_queried.extend(c.get("pages", []))
            pages_queried = sorted(list(set(pages_queried)))
            
            citations_output.append({
                "source_index": doc_idx,
                "filename": filename,
                "pages": pages_queried
            })
        return citations_output

citation_service = CitationService()
