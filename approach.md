### 🧠 Approach

This project builds a lightweight, modular pipeline for persona-based document understanding using quantized LLMs. The primary objective is to simulate a human-like expert persona (e.g., Travel Planner, Legal Analyst) that processes a given document and outputs structured responses based on a user-defined task or job prompt.

At its core, the pipeline uses a local LLM, specifically **TinyLlama-1.1B-Chat**, in the **GGUF format**, which is optimized for fast inference using backends like `llama.cpp`. This allows us to run language inference without requiring GPU support, enabling full offline operation on commodity hardware.

The system operates in stages:

1. **Input Handling**: Documents (PDF, plain text, or structured input) are read from the `/input` directory. Texts are either chunked into manageable sizes or streamed in depending on their length, ensuring token limits are respected.

2. **Prompt Construction**: For each chunk or document section, a prompt is constructed combining:

   * A predefined *persona template* (defining tone and domain perspective),
   * A user-defined *job prompt* (e.g., “summarize legal risks”),
   * And the actual document content.
     This prompt engineering ensures consistent and persona-aligned output from the LLM.

3. **Language Model Inference**: The constructed prompt is passed to the local model through Python bindings or subprocess calls (depending on the LLM backend). The model generates responses chunk-wise, which are then aggregated.

4. **Output Structuring**: The model outputs are parsed, deduplicated, and saved in structured JSON under the `/output` folder. This allows downstream systems to consume the insights programmatically.

5. **NLTK Tokenization**: Preprocessing includes sentence and word tokenization using NLTK, aiding in intelligent chunking and better prompt formatting.

This architecture is intentionally modular — allowing easy swapping of LLMs, personas, or input types — and is optimized for edge environments with limited compute.

