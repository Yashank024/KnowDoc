import json
import logging
import re
from app.db.chroma import chroma_wrapper
from app.services.ai.embeddings_service import embeddings_service
from app.services.ai.gemini_service import gemini_service
from app.utils.chunking import chunk_document_lines
from app.utils.query_classifier import needs_rag, get_local_response

logger = logging.getLogger("rag_pipeline")

class RAGPipeline:
    def __init__(self):
        self.collection = chroma_wrapper.get_collection()

    def index_document(self, doc_id: str, filename: str, text_lines: list) -> bool:
        """
        Splits visual OCR lines into overlapping chunks, generates embedding vectors,
        and saves chunks into ChromaDB persistent storage.
        """
        if not text_lines:
            logger.warning(f"No OCR lines available to index for document {filename}")
            return False

        logger.info(f"RAG Indexer: Splitting and embedding document '{filename}'...")
        
        # Generate overlapping layout-aware chunks optimized to 500 words with 100 word overlap
        chunks = chunk_document_lines(text_lines, chunk_word_size=500, overlap_word_size=100)
        
        ids = []
        documents = []
        embeddings = []
        metadatas = []

        # Extract only text parts for bulk embeddings call
        chunk_texts = [c["text"] for c in chunks]
        
        import time
        try:
            # Generate bulk embedding vectors using standard EmbeddingsService
            start_embed = time.time()
            chunk_vectors = embeddings_service.get_embeddings(chunk_texts)
            embed_time = time.time() - start_embed
            logger.info(f"METRIC: Embedding generation time for {filename} ({len(chunks)} chunks): {embed_time:.3f} seconds")
        except Exception as e:
            logger.error(f"Failed to generate embeddings in bulk: {e}. Falling back to page-by-page mapping.")
            chunk_vectors = []
            start_embed = time.time()
            for text in chunk_texts:
                chunk_vectors.append(embeddings_service.get_embedding(text))
            embed_time = time.time() - start_embed
            logger.info(f"METRIC: Embedding fallback generation time for {filename} ({len(chunks)} chunks): {embed_time:.3f} seconds")

        for idx, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{idx}"
            pages_str = ",".join([str(p) for p in chunk["pages"]])
            
            ids.append(chunk_id)
            documents.append(chunk["text"])
            embeddings.append(chunk_vectors[idx])
            
            # ChromaDB metadata values must be simple types (str, int, float, bool)
            metadatas.append({
                "doc_id": doc_id,
                "filename": filename,
                "pages": pages_str,
                "box_coords": json.dumps(chunk["box"])
            })

        try:
            # Upsert into persistent vector store
            self.collection.upsert(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            logger.info(f"Successfully indexed {len(chunks)} chunks for {filename} inside ChromaDB.")
            return True
        except Exception as e:
            logger.error(f"Error upserting chunks into ChromaDB: {e}", exc_info=True)
            return False

    def search_relevant_chunks(self, query: str, doc_ids: list = None, n_results: int = 3) -> list:
        """
        Computes search vector, queries ChromaDB persistent store, filters by similarity L2 threshold, and returns matches.
        """
        if not query.strip():
            return []

        logger.info(f"RAG search query: '{query}'")
        try:
            # Get search query embedding vector
            query_vector = embeddings_service.get_embedding(query)
            
            # Setup optional metadata filters (e.g. scoped document searches)
            where_filter = None
            if doc_ids and len(doc_ids) > 0:
                if len(doc_ids) == 1:
                    where_filter = {"doc_id": doc_ids[0]}
                else:
                    where_filter = {"doc_id": {"$in": doc_ids}}

            # Run query (Retrieving only top 3 most relevant chunks)
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=n_results,
                where=where_filter
            )

            formatted_chunks = []
            if results and results.get("documents"):
                docs = results["documents"][0]
                metas = results["metadatas"][0]
                distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

                for doc_text, metadata, dist in zip(docs, metas, distances):
                    score = float(dist)
                    # Apply rigid similarity filter: L2 distance > 1.25 is ignored to reduce retrieval noise
                    if score > 1.25:
                        logger.info(f"Retrieval Precision Filter: Skipping irrelevant chunk with distance {score:.3f} (> 1.25)")
                        continue

                    pages_list = []
                    if metadata.get("pages"):
                        try:
                            pages_list = [int(p) for p in metadata["pages"].split(",")]
                        except Exception:
                            pages_list = [1]
                            
                    formatted_chunks.append({
                        "text": doc_text,
                        "doc_id": metadata.get("doc_id"),
                        "filename": metadata.get("filename"),
                        "pages": pages_list,
                        "box_coords": json.loads(metadata.get("box_coords", "[]")),
                        "score": score
                    })

            return formatted_chunks
        except Exception as e:
            logger.error(f"Error querying ChromaDB vector store: {e}", exc_info=True)
            return []

    def answer_user_query(self, query: str, doc_ids: list = None, history: list = None) -> dict:
        """
        Orchestrates full local RAG pipeline flow: semantic search, context building,
        Gemini instruction mapping, response generation, and structured citations.
        Supports Two-Layer Query Classification, a sliding Memory Window of 6 messages,
        and high-precision retrieval-controlled citation mappings.
        """
        # Step 1: Query Classification Check (Bypass Gemini/RAG for generic greetings)
        if not needs_rag(query):
            logger.info(f"Query Classifier: Bypassing LLM/RAG for conversational prompt: '{query[:40]}'")
            return get_local_response(query)

        # Step 2: Build chat memory context limited to the last 6 messages
        memory_context = ""
        if history:
            recent_messages = history[-6:]
            history_parts = []
            for msg in recent_messages:
                # msg can be a Pydantic object or dict
                sender = getattr(msg, "sender", None) or msg.get("sender")
                text = getattr(msg, "text", None) or msg.get("text")
                sender_name = "User" if sender == "user" else "Assistant"
                history_parts.append(f"{sender_name}: {text}")
            memory_context = "\n".join(history_parts)
            logger.info(f"RAG Pipeline Memory: Formatted {len(recent_messages)} turns into memory context.")

        # Step 3: Retrieve context from vector store (top 3 filtered chunks)
        chunks = self.search_relevant_chunks(query, doc_ids=doc_ids, n_results=3)
        
        # If no chunks survive the threshold filtering, bypass LLM entirely
        if not chunks:
            logger.info("Retrieval Control: Zero relevant chunks survived threshold filtering. Returning fallback.")
            return {
                "reply": "No relevant information was found in uploaded documents.",
                "citations": [],
                "chunks_searched": 0
            }

        # Build layout-aware RAG context block
        context_parts = []
        unique_docs_map = {}
        doc_counter = 1

        for idx, chunk in enumerate(chunks):
            filename = chunk["filename"]
            pages_str = ", ".join([str(p) for p in chunk["pages"]])
            
            # Give documents unique index numbers starting at 1
            if filename not in unique_docs_map:
                unique_docs_map[filename] = doc_counter
                doc_counter += 1
                
            doc_idx = unique_docs_map[filename]
            context_parts.append(
                f"[Doc {doc_idx}] {filename} (Page {pages_str}):\n{chunk['text']}\n"
            )

        context_block = "\n".join(context_parts)

        # Rigid System Prompt Contract forcing markdown and citation constraints
        system_instruction = (
            "You are KnowDoc AI, a premium conversational document auditing assistant.\n"
            "Your task is to answer user queries using ONLY the provided Context Blocks from uploaded files.\n\n"
            "CRITICAL INSTRUCTIONS FOR CITATIONS & RESPONSE FORMAT:\n"
            "1. Answer ONLY using the facts from the Context Blocks. If you cannot find the answer, reply: \"No relevant information was found in uploaded documents.\"\n"
            "2. For every statement of fact, append an inline citation exactly in this format: '[Doc X, Page Y]' "
            "where 'X' is the document index number (e.g. 1 for [Doc 1]) and 'Y' is the exact page number (e.g., Page 3).\n"
            "3. Place this inline reference superscript immediately after the sentence or statement that extracts that fact.\n"
            "4. NEVER reference document indices or page numbers that do not appear in the context. Never hallucinate citations.\n"
            "5. Respond in elegant, highly professional, and clean markdown formats. Use headings (###), bullet points for list elements, and bold formatting where appropriate.\n"
            "6. Keep answers highly concise, informative, and organized. Avoid dense paragraphs."
        )
        
        if memory_context:
            system_instruction += f"\nRecent Conversational History:\n{memory_context}\n"

        prompt = (
            f"User Query:\n{query}\n\n"
            f"Context Blocks from Global AI Memory:\n"
            f"=========================================\n"
            f"{context_block}\n"
            f"=========================================\n\n"
            f"Based solely on the Context Blocks above, provide a comprehensive, structured response referencing the sources."
        )

        logger.info("Invoking Gemini Generative model with RAG context...")
        reply_text = gemini_service.generate_response(prompt, system_instruction=system_instruction)

        # Step 4: Backend-controlled Retrieval Citation Mapping
        # Search the generated text for citations to see which sources were actually cited by the assistant
        cited_indices = set()
        citation_pattern = re.compile(r'\[Doc\s*(\d+)(?:,\s*Page\s*(\d+))?\]')
        for match in citation_pattern.finditer(reply_text):
            doc_idx = int(match.group(1))
            cited_indices.add(doc_idx)
            
        logger.info(f"Retrieval Control: Document indices actually cited by Gemini: {cited_indices}")

        # Map document reference names and pages to citations in a list for front-end,
        # filtering out retrieved chunks that were not actually cited in the text
        citations_output = []
        for filename, doc_idx in unique_docs_map.items():
            if doc_idx in cited_indices:
                # Gather which pages were queried for this doc
                pages_queried = []
                for c in chunks:
                    if c["filename"] == filename:
                        pages_queried.extend(c["pages"])
                pages_queried = sorted(list(set(pages_queried)))
                
                citations_output.append({
                    "source_index": doc_idx,
                    "filename": filename,
                    "pages": pages_queried
                })

        return {
            "reply": reply_text,
            "citations": citations_output,
            "chunks_searched": len(chunks)
        }

# Initialize singleton pipeline
rag_pipeline = RAGPipeline()
