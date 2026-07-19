import json
import logging
import re
from app.db.chroma import chroma_wrapper
from app.services.ai.embeddings_service import embeddings_service
from app.services.ai.openrouter_service import openrouter_service
from app.utils.chunking import chunk_document_lines

logger = logging.getLogger("rag_pipeline")

class RAGPipeline:
    def __init__(self):
        self.collection = chroma_wrapper.get_collection()
        self._query_cache = {}

    def index_document(self, doc_id: str, filename: str, text_lines: list) -> bool:
        """
        Splits visual OCR lines into overlapping chunks, generates embedding vectors,
        and saves chunks into ChromaDB persistent storage.
        """
        if not text_lines:
            logger.warning(f"No OCR lines available to index for document {filename}")
            return False

        logger.info(f"RAG Indexer: Splitting and embedding document '{filename}'...")
        
        # Generate overlapping layout-aware chunks optimized to 900 words with 150 word overlap
        chunks = chunk_document_lines(text_lines, chunk_word_size=900, overlap_word_size=150)
        
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
                "box_coords": json.dumps(chunk["box"]),
                "type": "document"
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

    def search_relevant_chunks(self, query: str, doc_ids: list = None, chat_id: str = None, n_results: int = 5) -> list:
        """
        Computes search vector, queries ChromaDB persistent store, filters by similarity L2 threshold, and returns matches.
        """
        if not query.strip():
            return []

        logger.info(f"RAG search query: '{query}', chat_id: '{chat_id}'")
        try:
            # Get search query embedding vector
            query_vector = embeddings_service.get_embedding(query)
            
            # Setup optional metadata filters (e.g. scoped document searches and chat memory)
            where_filter = None
            conditions = []
            
            if doc_ids and len(doc_ids) > 0:
                if len(doc_ids) == 1:
                    conditions.append({"doc_id": doc_ids[0]})
                else:
                    conditions.append({"doc_id": {"$in": doc_ids}})
            else:
                # Default: search standard user documents (type = "document")
                conditions.append({"type": "document"})
                
            if chat_id:
                # Include the active chat history turns
                conditions.append({"doc_id": f"chat_memory_{chat_id}"})
                
            if conditions:
                if len(conditions) == 1:
                    where_filter = conditions[0]
                else:
                    where_filter = {"$or": conditions}

            # Run query
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
                    # Apply relaxed similarity filter: L2 distance > 1.65 is ignored to reduce retrieval noise
                    if score > 1.65:
                        logger.info(f"Retrieval Precision Filter: Skipping irrelevant chunk with distance {score:.3f} (> 1.65)")
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

    def answer_user_query(self, query: str, doc_ids: list = None, history: list = None, chat_id: str = None) -> dict:
        """
        Orchestrates full local RAG pipeline flow: semantic search, context building,
        OpenRouter instruction mapping, response generation, and structured citations.
        Supports Vector Conversation Memory, sliding Memory Window of 6 messages,
        and high-precision retrieval-controlled citation mappings.
        """
        # Step 1: Check In-Memory Query Cache for instant repeat response
        doc_ids_key = ",".join(sorted(doc_ids)) if doc_ids else ""
        cache_key = f"{query.strip().lower()}:{doc_ids_key}"
        if cache_key in self._query_cache:
            logger.info(f"Query Cache Hit: Instant response for repeated prompt: '{query[:40]}'")
            return self._query_cache[cache_key]

        # Step 2: Build chat memory context limited to the last 6 messages
        memory_context = ""
        if history:
            recent_messages = history[-6:]
            history_parts = []
            for msg in recent_messages:
                sender = getattr(msg, "sender", None) or msg.get("sender")
                text = getattr(msg, "text", None) or msg.get("text")
                sender_name = "User" if sender == "user" else "Assistant"
                history_parts.append(f"{sender_name}: {text}")
            memory_context = "\n".join(history_parts)
            logger.info(f"RAG Pipeline Memory: Formatted {len(recent_messages)} turns into memory context.")

        # Step 3: Retrieve context from vector store (top 5 filtered chunks including conversation memory)
        chunks = self.search_relevant_chunks(query, doc_ids=doc_ids, chat_id=chat_id, n_results=5)
        
        # Build layout-aware RAG context block
        context_parts = []
        for idx, chunk in enumerate(chunks):
            filename = chunk["filename"]
            pages_str = ", ".join([str(p) for p in chunk["pages"]])
            context_parts.append(
                f"Source Document: {filename} (Page {pages_str}):\n{chunk['text']}\n"
            )

        context_block = "\n".join(context_parts)
        if len(context_block) > 12000:
            logger.info(f"RAG Context Truncation: Slicing context block from {len(context_block)} characters to 12000 characters.")
            context_block = context_block[:12000]

        # System Prompt Contract forcing markdown and citation constraints
        system_instruction = (
            "You are KnowDoc AI, a premium conversational document auditing assistant.\n"
            "Your task is to answer user queries using the provided Context Blocks from uploaded files and past conversation history.\n\n"
            "CRITICAL INSTRUCTIONS FOR RESPONSE FORMAT:\n"
            "1. Answer using facts from the Context Blocks. If the query asks for specific document details that cannot be found in the Context Blocks, you must reply with exactly: \"I cannot find any relevant document of your query.\" and nothing else. Do not guess or invent facts.\n"
            "2. If the user query is a simple conversational greeting (like 'hi', 'hello', 'hey', 'greetings'), or asks who you are, reply naturally, politely, and professionally as KnowDoc AI without saying you cannot find the document.\n"
            "3. DO NOT include any inline citations, document indexes, file references, or source brackets (e.g., do NOT write things like '[Doc: filename]', '[Doc X]', '[Page Y]', or similar references) in your response. Keep the reply clean and free of brackets.\n"
            "4. Respond in elegant, highly professional, and clean markdown formats. Use headings (###), bullet points for list elements, and bold formatting where appropriate.\n"
            "5. Keep answers highly concise, informative, and organized."
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

        logger.info("Invoking OpenRouter completions with RAG context...")
        reply_text = openrouter_service.generate_response(prompt, system_instruction=system_instruction)

        # Step 4: Backend-controlled Retrieval Citation Mapping
        # Map all actually retrieved documents to citations list for front-end
        citations_output = []
        retrieved_filenames = list(set([c["filename"] for c in chunks]))
        
        for doc_idx, filename in enumerate(retrieved_filenames):
            pages_queried = []
            for c in chunks:
                if c["filename"] == filename:
                    pages_queried.extend(c["pages"])
            pages_queried = sorted(list(set(pages_queried)))
            
            citations_output.append({
                "source_index": doc_idx + 1,
                "filename": filename,
                "pages": pages_queried
            })

        response = {
            "reply": reply_text,
            "citations": citations_output,
            "chunks_searched": len(chunks)
        }
        
        # Save to local cache if successful
        if reply_text != "Cannot connect to the API.":
            self._query_cache[cache_key] = response
            
        # Index this successful QA turn as long-term memory in the background
        if chat_id and reply_text != "I cannot find any relevant document of your query." and reply_text != "Cannot connect to the API.":
            try:
                from app.services.chat.chat_service import chat_service
                chat_obj = chat_service.get_chat_session(chat_id)
                chat_title = chat_obj.get("title", "Document Chat Session") if chat_obj else "Document Chat Session"
                self.index_chat_turn(chat_id, chat_title, query, reply_text)
            except Exception as e:
                logger.error(f"Failed to trigger QA memory turn indexing: {e}")
                
        return response

    def index_chat_turn(self, chat_id: str, chat_title: str, query: str, reply: str) -> bool:
        """
        Embeds and stores a QA turn into ChromaDB so it becomes searchable in subsequent retrievals.
        """
        import uuid
        try:
            qa_text = f"User Question: {query}\nAI Answer: {reply}"
            logger.info(f"RAG Indexer: Saving QA memory turn to ChromaDB for chat {chat_id}...")
            
            # Generate embedding vector for this QA block
            vector = embeddings_service.get_embedding(qa_text)
            chunk_id = f"mem_{chat_id}_{uuid.uuid4().hex[:6]}"
            
            self.collection.upsert(
                ids=[chunk_id],
                documents=[qa_text],
                embeddings=[vector],
                metadatas=[{
                    "doc_id": f"chat_memory_{chat_id}",
                    "filename": f"Chat History: {chat_title}",
                    "pages": "1",
                    "box_coords": "[]",
                    "type": "chat_memory",
                    "chat_id": chat_id
                }]
            )
            logger.info(f"Successfully indexed QA memory turn {chunk_id} in ChromaDB.")
            return True
        except Exception as e:
            logger.error(f"Error indexing QA memory turn in ChromaDB: {e}", exc_info=True)
            return False

    def delete_document_chunks(self, doc_id: str) -> bool:
        """
        Deletes all chunks associated with a doc_id from ChromaDB collection.
        """
        logger.info(f"RAG Indexer: Deleting chunks for document ID {doc_id} from ChromaDB...")
        try:
            self.collection.delete(where={"doc_id": doc_id})
            return True
        except Exception as e:
            logger.error(f"Failed to delete chunks from ChromaDB: {e}")
            return False

# Initialize singleton pipeline
rag_pipeline = RAGPipeline()
