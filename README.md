# AI-Powered IT Service Desk & Production Incident Resolution Platform

> An end-to-end AI platform for investigating production incidents, retrieving operational knowledge, and recommending safe resolutions using **Multi-Agent AI, RAG, MCP, and Human Approval**.

## Overview

This system takes a production incident and automatically:

1. Classifies the incident.
2. Retrieves relevant runbooks, SOPs, and previous RCAs.
3. Investigates service health, logs, and asset information.
4. Generates an evidence-based resolution recommendation.
5. Requires human approval before production-changing actions.
6. Executes the approved action and verifies service health.

### Example

```
Incident
   ↓
Classification → Knowledge RAG
   ↓
Investigation → IT Ops + Asset MCP
   ↓
Resolution Recommendation
   ↓
Human Approval
   ↓
Approved Action → Health Verification
```

## Architecture

```
Streamlit
   ↓
FastAPI
   ↓
CrewAI Multi-Agent Workflow
   ├── Classification Agent
   ├── Knowledge Agent ──→ Knowledge RAG MCP ──→ ChromaDB
   ├── Investigation Agent → IT Operations MCP + Asset MCP
   └── Resolution Agent
                ↓
         Human Approval
                ↓
       IT Operations MCP
```

The backend runs the MCP servers as stdio subprocesses and uses Groq for LLM reasoning.

## Key Features

- **Multi-Agent AI:** classification, knowledge retrieval, investigation, and resolution.
- **RAG + MCP:** operational knowledge and live system capabilities are exposed through MCP tools.
- **Human-in-the-loop:** production-changing actions require explicit approval.
- **Production-style deployment:** FastAPI + Streamlit + Docker Compose with persistent application state.
- **Evidence-based resolution:** recommendations are based on retrieved knowledge and investigation results.

## Technology Stack

**Python · CrewAI · Groq · LlamaIndex · ChromaDB · Hugging Face Embeddings · MCP · FastAPI · Streamlit · Docker · pytest · AWS EC2**

## Testing & Validation

The project was validated at component, integration, workflow, and Docker levels.

- RAG retrieval and similarity threshold
- 4 MCP servers
- 4 AI agents
- Complete multi-agent workflow
- FastAPI incident-resolution API
- Human approval/rejection flow
- Persistent service state
- Docker networking and containerized workflow

**Docker regression: 12/12 tests passed.**

```bash
python -m pytest tests/docker/test_docker_regression.py -v
```

## Quick Start

```bash
# Configure environment
copy .env.example .env

# Install dependencies
uv pip install -r requirements.txt

# Build knowledge base
python -m src.rag_src.ingestion.ingestion_docs

# Start application
docker compose up -d
```

- Streamlit: `http://localhost:8501`
- FastAPI Swagger: `http://localhost:8000/docs`

## Project Structure

```text
docs_dir/       → Runbooks, SOPs, RCAs
src/agents_src/ → CrewAI agents and workflow
src/mcp_src/    → MCP servers and clients
src/rag_src/    → RAG ingestion and retrieval
src/backend_src/→ FastAPI API
src/frontend_src/→ Streamlit UI
tests/          → Unit, functional, integration and Docker tests
Dockerfile      → Container image
docker-compose.yml → Local orchestration
```
