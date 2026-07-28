from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import settings
from .llm.provider import registry as provider_registry, OpenAICompatibleProvider
from .agent.copilot_agent import agent
from .sop.engine import sop_engine
from .rag.knowledge_base import knowledge_base


app = FastAPI(title="Tourism CS Copilot", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    ticket_id: str


class AnalyzeResponse(BaseModel):
    ticket_id: str
    analysis: dict
    reply_template: str
    suggested_actions: list
    references: dict
    warnings: list


@app.on_event("startup")
async def startup():
    provider_registry.register_chat(
        OpenAICompatibleProvider(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
        )
    )
    provider_registry.register_embed(
        OpenAICompatibleProvider(
            base_url=settings.embed_base_url,
            api_key=settings.embed_api_key,
            model=settings.embed_model,
        )
    )

    sop_engine.load_all()
    knowledge_base.initialize()


@app.get("/api/copilot/status")
async def get_status():
    return {
        "status": "running",
        "sop_count": len(sop_engine._sops),
        "knowledge_base": knowledge_base.get_status(),
        "max_iterations": settings.copilot_max_agent_iterations,
    }


@app.post("/api/copilot/analyze", response_model=AnalyzeResponse)
async def analyze_ticket(req: AnalyzeRequest):
    result = agent.analyze(req.ticket_id)
    return AnalyzeResponse(
        ticket_id=req.ticket_id,
        analysis=result.get("analysis", {}),
        reply_template=result.get("reply_template", ""),
        suggested_actions=result.get("suggested_actions", []),
        references=result.get("references", {}),
        warnings=result.get("warnings", []),
    )


@app.post("/admin/sop/reload")
async def reload_sop():
    result = sop_engine.reload()
    return result


@app.post("/admin/knowledge/ingest")
async def ingest_knowledge():
    result = knowledge_base.ingest_directory()
    return result


@app.get("/admin/knowledge/status")
async def knowledge_status():
    return knowledge_base.get_status()
