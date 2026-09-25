# IBM Bob Multi-Agent Execution Log — AfyaRisk 

## Agentic SDLC Integration
AfyaRisk 2.0 was engineered using IBM Bob as an enterprise agentic assistant across the entire SDLC:

1. **Architecture & Specification Agent (`/ask`):** Generated `docs/SPEC.md` defining clinical ML algorithms, actuarial loss reserving formulas (Chain-Ladder IBNR), and RAG vector search strategies.
2. **Backend & Data Science Agent (`/agent`):** Engineered FastAPI microservices (`backend/engine/`) covering Random Forest health risk scoring, XGBoost claims severity prediction, Isolation Forest fraud detection, and FAISS policy RAG.
3. **Frontend UI Agent (`/agent`):** Created Next.js 14 interactive dashboard components with Tailwind CSS styling and Recharts visualizations.