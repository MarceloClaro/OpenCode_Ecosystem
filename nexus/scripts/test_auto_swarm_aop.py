import sys, json, time
sys.path.insert(0, 'nexus/scripts')

from auto_swarm_builder import AutoSwarmBuilder, AgentSpec, SwarmRouterConfig, BuiltInTaskAnalyzers
from aop_service_discovery import AOPServer, TaskStatus, TaskQueue


def main():
    print("=" * 60)
    print("TESTE: AutoSwarmBuilder")
    print("=" * 60)

# Test 1: AutoSwarmBuilder with mock boss
print("\n[1] AutoSwarmBuilder - Mock Boss")
def mock_boss(system_prompt, task):
    return json.dumps({"name": "test-swarm", "description": "Test", "swarm_type": "sequential",
        "agents": [{"name": "researcher", "description": "Research", "system_prompt": "You are a researcher"},
                   {"name": "writer", "description": "Writer", "system_prompt": "You are a writer"}]})
b = AutoSwarmBuilder(name="test-builder", verbose=False, execution_type="return-agents")
agents = b.run("Create report", boss_agent_fn=mock_boss)
assert len(agents) == 2 and isinstance(agents[0], AgentSpec)
print(f"  PASS - {len(agents)} agent specs created")

# Test 2: Return config
print("\n[2] AutoSwarmBuilder - Return Config")
b2 = AutoSwarmBuilder(name="config-builder", verbose=False, execution_type="return-config")
config = b2.run("Research AI", boss_agent_fn=mock_boss)
assert isinstance(config, SwarmRouterConfig) and len(config.agents) == 2
print(f"  PASS - Config: {config.name}, {len(config.agents)} agents")

# Test 3: Built-in analyzers
print("\n[3] Built-in Task Analyzers")
research = BuiltInTaskAnalyzers.research_task_analyzer()
assert research["swarm_type"] == "research_analysis_synthesis" and len(research["agents"]) == 3
code_review = BuiltInTaskAnalyzers.code_review_task_analyzer()
assert code_review["swarm_type"] == "council_of_judges" and len(code_review["agents"]) == 3
content = BuiltInTaskAnalyzers.content_creation_task_analyzer()
assert content["swarm_type"] == "sequential" and len(content["agents"]) == 3
print(f"  PASS - All 3 analyzers work")

# Test 4: Batch run
print("\n[4] Batch Run")
call_count = 0
def mock_boss2(system_prompt, task):
    global call_count
    call_count += 1
    return json.dumps({"name": f"swarm-{call_count}", "description": "", "swarm_type": "sequential",
        "agents": [{"name": f"agent-{call_count}", "description": "", "system_prompt": ""}]})
b3 = AutoSwarmBuilder(verbose=False, execution_type="return-agents")
results = b3.batch_run(["Task 1", "Task 2", "Task 3"], mock_boss2)
assert len(results) == 3 and call_count == 3
print(f"  PASS - Batch processed {len(results)} tasks")

print("\n" + "=" * 60)
print("TESTE: AOP Service Discovery")
print("=" * 60)

from aop_service_discovery import AOPServer, TaskStatus, TaskQueue

# Test 5: Add agent
print("\n[5] AOP Server - Add Agent")
server = AOPServer(server_name="test-server", verbose=False, queue_enabled=True)
server.add_agent(name="research-agent", description="Research specialist",
    handler=lambda task: f"Research: {task}", max_workers=2, timeout=30)
assert "research-agent" in server.agents and server.agents["research-agent"].max_workers == 2
print(f"  PASS - Agent registered with queue")

# Test 6: Batch add
print("\n[6] AOP Server - Batch Add")
server2 = AOPServer(server_name="batch-server", queue_enabled=True)
agents = [{"name": f"agent-{i}", "description": f"Agent {i}", "handler": lambda t: t} for i in range(3)]
server2.add_agents_batch(agents)
assert len(server2.agents) == 3
print(f"  PASS - {len(server2.agents)} agents registered")

# Test 7: Direct task
print("\n[7] AOP Server - Direct Task")
server3 = AOPServer(server_name="direct-server", queue_enabled=False)
server3.add_agent(name="processor", description="Processor", handler=lambda task: f"Done: {task}")
task_id = server3.submit_task("processor", "Test data")
status = server3.get_task_status(task_id)
assert status["status"] == TaskStatus.COMPLETED.value and status["result"] == "Done: Test data"
print(f"  PASS - Task completed directly")

# Test 8: Queue stats
print("\n[8] AOP Server - Queue Stats")
server4 = AOPServer(server_name="stats-server", queue_enabled=True)
server4.add_agent(name="worker", description="Worker", handler=lambda t: t)
for i in range(5):
    server4.submit_task("worker", f"Task {i}", priority=i)
stats = server4.get_server_stats()
assert stats["total_tasks"] == 5 and stats["registered_agents"] == 1
print(f"  PASS - {stats['total_tasks']} tasks queued")

# Test 9: Service discovery
print("\n[9] AOP Server - Service Discovery")
server5 = AOPServer(server_name="discovery-server", queue_enabled=True)
server5.add_agent(name="agent-a", description="Agent A", handler=lambda t: t)
server5.add_agent(name="agent-b", description="Agent B", handler=lambda t: t)
discovered = server5.discover_agents()
assert len(discovered) == 2 and discovered[0]["name"] == "agent-a"
print(f"  PASS - Discovered {len(discovered)} agents")

# Test 10: Task queue priority
print("\n[10] Task Queue Priority")
queue = TaskQueue(max_workers=1)
class QT:
    def __init__(self, tid, pri):
        self.task_id = tid; self.agent_name = "a"; self.input_data = "x"
        self.status = TaskStatus.PENDING; self.priority = pri; self.retries = 0
        self.max_retries = 3; self.created_at = time.time()
        self.started_at = None; self.completed_at = None; self.result = None; self.error = None
queue.enqueue(QT("low", 1))
queue.enqueue(QT("high", 10))
first = queue.dequeue()
assert first.task_id == "high"
print(f"  PASS - High priority dequeued first")

print("\n" + "=" * 60)
print("TODOS OS TESTES PASSARAM (10/10)")
print("=" * 60)


if __name__ == "__main__":
    main()
