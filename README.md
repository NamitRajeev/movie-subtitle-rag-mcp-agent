# Movie Subtitle RAG MCP Agent

A movie subtitle question-answering system built using Retrieval-Augmented Generation (RAG), with an agent layer for routing requests and an MCP-based email tool for sending results.

The system works with `.srt` subtitle files and allows users to ask questions about specific movies. Relevant subtitle sections are retrieved from a ChromaDB vector store and passed to a local LLM to generate a grounded answer with timestamp-based citations.

## Features

- Parse and clean `.srt` subtitle files
- Create contextual subtitle chunks
- Generate sentence embeddings using Sentence Transformers
- Store subtitle chunks in ChromaDB
- Retrieve relevant subtitle evidence for a question
- Filter retrieval by movie
- Rerank retrieved evidence using semantic and keyword relevance
- Generate answers using a local Qwen model through Ollama
- Provide timestamp-based citations
- Resolve movie names and handle ambiguous movie names
- Handle missing movies and missing information
- Maintain conversation state for follow-up requests
- Send movie answers through an MCP email server
- Validate email input and handle SMTP errors
- Streamlit interface for interacting with the system
- Automated tests using pytest
- Evaluation dataset and evaluation script

## How it works

The main flow of the application is:

```text
                 SRT Files
                     |
                     v
              SRT Parser
                     |
                     v
                Cleaner
                     |
                     v
             Contextual Chunks
                     |
                     v
          Sentence Transformer
                     |
                     v
                ChromaDB
                     |
                     |
                User Query
                     |
                     v
              Movie Agent
                     |
          +----------+----------+
          |          |          |
          v          v          v
     Information   Email   Clarification
          |          |
          +-----+----+
                |
                v
             Retriever
                |
                v
             Reranker
                |
                v
          Subtitle Evidence
                |
                v
          Qwen2.5 LLM
                |
                v
        Answer + Citations
                |
                v
          MCP Email Tool
                |
                v
               SMTP
```

## Project structure

```text
movie-subtitle-rag-mcp-agent/
│
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── data/
│   └── subtitles/
│
├── chroma_db/
│
├── src/
│   ├── ingestion/
│   │   ├── parser.py
│   │   ├── cleaner.py
│   │   └── chunker.py
│   │
│   ├── retrieval/
│   │   ├── embedding.py
│   │   ├── vector_store.py
│   │   ├── retriever.py
│   │   ├── reranker.py
│   │   └── citations.py
│   │
│   ├── generation/
│   │   └── answer_generator.py
│   │
│   └── agent/
│       ├── agent.py
│       ├── schemas.py
│       ├── router.py
│       ├── movie_resolver.py
│       ├── clarification.py
│       └── state.py
│
├── mcp/
│   ├── server.py
│   └── client.py
│
├── scripts/
│   ├── test_agent.py
│   └── test_mcp_edgecase.py
│
├── evaluation/
│   ├── questions.json
│   ├── run_evaluation.py
│   └── results.json
│
└── tests/
```

`chroma_db/` is generated locally and is excluded from Git.

## Technology stack

- Python
- Streamlit
- pysrt
- Sentence Transformers
- ChromaDB
- Ollama
- Qwen2.5 3B
- Pydantic
- MCP Python SDK
- SMTP
- pytest

## RAG pipeline

### 1. Subtitle parsing

Subtitle files are parsed using `pysrt`. Each subtitle entry contains the movie name, subtitle ID, timestamps and dialogue.

### 2. Cleaning

Subtitle formatting such as HTML tags and unnecessary whitespace is cleaned before the text is used for retrieval.

### 3. Chunking

Individual subtitle entries are combined into contextual chunks instead of embedding every subtitle line separately.

The current chunking setup uses:

- Target duration: 45 seconds
- Maximum duration: 60 seconds
- Overlap: 7 seconds

### 4. Embeddings

The project uses:

```text
all-MiniLM-L6-v2
```

to convert subtitle chunks and user questions into vector embeddings.

### 5. Vector database

Embeddings and subtitle metadata are stored in ChromaDB.

The stored metadata includes:

- Movie
- Chunk ID
- Start timestamp
- End timestamp
- Subtitle start ID
- Subtitle end ID

### 6. Retrieval

When a user asks a question, the question is embedded and compared with the stored subtitle chunks.

The search can be restricted to a specific movie.

The system initially retrieves multiple candidates and then reranks them using:

- Semantic relevance
- Keyword overlap

The final evidence passed to the answer generator is limited to the most relevant results.

### 7. Answer generation

The retrieved subtitle evidence is passed to Qwen2.5 running locally through Ollama.

The model is instructed to use only the supplied subtitle evidence and not rely on general knowledge about the movie.

This is important because the system is intended to answer questions based on the indexed subtitle dataset rather than acting as a general movie chatbot.

### 8. Citations

Citations are generated deterministically from the retrieved metadata.

A citation contains the movie name and timestamp range, for example:

```text
[Iron.Man.2008.1080p.BluRay.x265-YAWNTiC_eng — 00:42:10,000 -> 00:42:48,000]
```

## Agent

The agent coordinates the different parts of the application.

It currently handles:

- Information requests
- Email requests
- Movie resolution
- Clarification
- Conversation state
- Retrieval
- Answer generation
- Citations
- Email actions

For example, a conversation can work like:

```text
User:
What happened when Tony returned home from captivity?

User:
Email me that

Agent:
What email address should I send the previous answer to?

User:
example@email.com
```

The second request uses the previous answer stored in the conversation state rather than performing a completely new search.

## MCP email integration

The project includes a small MCP server with a `send_email` tool.

The flow is:

```text
Movie Agent
     |
     v
MCP Client
     |
     v
MCP Email Server
     |
     v
SMTP
     |
     v
Email
```

The MCP server performs:

- Recipient validation
- Subject validation
- Body validation
- SMTP authentication
- Email sending
- SMTP error handling
- Retry handling for connection failures

SMTP configuration is stored in `.env`.

Example:

```text
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-app-password
```

The real `.env` file should never be committed to the repository.

## Running the project

### 1. Clone the repository

```bash
git clone <repository-url>
cd movie-subtitle-rag-mcp-agent
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Install and start Ollama

Make sure Ollama is installed and running.

Pull the model:

```powershell
ollama pull qwen2.5:3b
```

### 5. Configure email

Create a `.env` file in the project root.

Add the SMTP configuration:

```text
SMTP_HOST=your-smtp-host
SMTP_PORT=587
SMTP_USERNAME=your-email
SMTP_PASSWORD=your-app-password
```

### 6. Add subtitles

Place `.srt` files inside:

```text
data/subtitles/
```

The subtitle files should contain the movie name in their filename so that the system can identify the movie.

### 7. Build the vector database

Run the project's ingestion process used to parse the subtitle files, create chunks, generate embeddings and store them in ChromaDB.

The resulting vector database is stored locally in:

```text
chroma_db/
```

### 8. Start the application

```powershell
streamlit run app.py
```

The Streamlit interface can then be used to select a movie, enter a question and view the answer and sources.

## Testing

The project uses pytest for testing.

Run the complete test suite with:

```powershell
pytest -v
```

The tests cover areas including:

- Agent behavior
- Movie resolution
- Clarification
- Follow-up requests
- MCP email validation
- SMTP failure handling
- MCP availability

## Evaluation

The project contains a small evaluation dataset in:

```text
evaluation/questions.json
```

The evaluation script tests different types of requests including:

- Direct movie questions
- Character questions
- Scene questions
- Contextual questions
- Questions where evidence is insufficient
- Unknown movies
- Missing movie information
- Clarification cases

Run the evaluation with:

```powershell
python -m evaluation.run_evaluation
```

The results are written to:

```text
evaluation/results.json
```

The evaluation is intended as a baseline for checking system behavior, answer grounding and unsupported claims.

## Current dataset

The current local dataset contains subtitle files for six movies:

- Avengers: Age of Ultron
- Avengers: Endgame
- Avengers: Infinity War
- Iron Man
- Iron Man 2
- Iron Man 3

The system is designed so that additional subtitle files can be added to the dataset.

## Design decisions

The project deliberately keeps most of the system deterministic.

Python is responsible for tasks such as:

- Subtitle parsing
- Cleaning
- Chunking
- Movie identification
- Movie filtering
- Vector storage
- Retrieval
- Reranking
- Citation construction
- Email validation
- Conversation state
- Routing
- Error handling

The LLM is mainly used for:

- Generating grounded natural-language answers
- Summarizing retrieved subtitle information

MCP is used for the external email action.

This separation makes it easier to test and debug the individual parts of the system.

## Limitations

The current system has some limitations:

- Answer quality depends on the retrieved subtitle evidence.
- Poor retrieval can result in incomplete or incorrect answers.
- Subtitle files may contain formatting or transcription errors.
- The current evaluation dataset is relatively small.
- The local 3B language model has limited reasoning capability compared with larger models.
- Movie metadata is currently derived from the indexed subtitle collection rather than a separate movie database.

## Future improvements

Possible improvements include:

- Better retrieval and reranking
- Improved handling of character names and dialogue
- More robust citation relevance
- Larger evaluation datasets
- Support for more subtitle files
- Better conversational intent handling
- Additional MCP tools

## Author

Namit Rajeev
