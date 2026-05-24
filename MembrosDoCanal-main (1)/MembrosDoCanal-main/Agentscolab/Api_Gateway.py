from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import engine, SessionLocal
from models import Base, Agent, Collaboration

app = FastAPI(title="AgentHub API")

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------ AGENTS ------------------

@app.post("/agents")
def register_agent(agent: dict, db: Session = Depends(get_db)):
    exists = db.query(Agent).filter(
        Agent.agent_id == agent["agent_id"]
    ).first()

    if not exists:
        db.add(Agent(**agent))
        db.commit()

    return {"status": "registered", "agent_id": agent["agent_id"]}


@app.get("/agents")
def discover_agents(skill: str | None = None, db: Session = Depends(get_db)):
    agents = db.query(Agent).all()

    if skill:
        agents = [
            a for a in agents
            if a.skills and skill in a.skills
        ]

    return agents

@app.get("/agents/search")
def search_agents(
    skill: str,
    status: str = "available",
    db: Session = Depends(get_db)
):
    agents = db.query(Agent).filter(
        Agent.status == status
    ).all()

    return [
        a for a in agents
        if a.skills and skill in a.skills
    ]


# ------------------ COLLABORATION ------------------

@app.post("/collaboration/request")
def request_collaboration(payload: dict, db: Session = Depends(get_db)):
    collab = Collaboration(**payload)
    db.add(collab)
    db.commit()
    return {"status": "requested", "collaboration_id": collab.id}


@app.get("/collaboration/pending/{agent_id}")
def pending_collaborations(agent_id: str, db: Session = Depends(get_db)):
    return db.query(Collaboration).filter(
        Collaboration.to_agent == agent_id,
        Collaboration.status == "pending"
    ).all()


@app.post("/collaboration/complete/{collab_id}")
def complete_collaboration(collab_id: int, payload: dict, db: Session = Depends(get_db)):
    collab = db.query(Collaboration).get(collab_id)

    collab.output = payload["output"]
    collab.latency_ms = payload["latency_ms"]
    collab.success = payload["success"]
    collab.rating = payload["rating"]
    collab.status = "completed"

    db.commit()
    return {"status": "completed"}

@app.get("/collaboration/{collab_id}")
def get_collaboration(collab_id: int, db: Session = Depends(get_db)):
    return db.query(Collaboration).get(collab_id)
