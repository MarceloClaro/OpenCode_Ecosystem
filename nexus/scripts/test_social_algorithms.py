import sys, json, time, asyncio
sys.path.insert(0, 'nexus/scripts')
from social_algorithms import Agent, SocialAlgorithms, SocialAlgorithmType


def main():
    print("=" * 60)
    print("TESTE: Social Algorithms")
    print("=" * 60)

# Test 1: Sequential
print("\n[1] Sequential")
agents = [Agent(f"A{i}", (lambda i: lambda t, **kw: f"R{i}")(i)) for i in range(3)]
s = SocialAlgorithms("seq", agents, algorithm_type=SocialAlgorithmType.SEQUENTIAL)
r = s.run("test")
assert r.success and len(r.final_outputs) == 3
print(f"  PASS - {len(r.final_outputs)} outputs")

# Test 2: Concurrent
print("\n[2] Concurrent")
agents = [Agent(f"W{i}", (lambda i: lambda t, **kw: f"R{i}")(i)) for i in range(5)]
s = SocialAlgorithms("conc", agents, algorithm_type=SocialAlgorithmType.CONCURRENT)
r = s.run("test")
assert r.success and len(r.final_outputs) == 5
print(f"  PASS - {len(r.final_outputs)} concurrent results")

# Test 3: Research-Analysis-Synthesis
print("\n[3] Research-Analysis-Synthesis")
agents = [Agent("Res", lambda t, **kw: "research_data"),
          Agent("Ana", lambda t, **kw: "analysis_data"),
          Agent("Syn", lambda t, **kw: "synthesis_data")]
s = SocialAlgorithms("ras", agents, algorithm_type=SocialAlgorithmType.RESEARCH_ANALYSIS_SYNTHESIS)
r = s.run("AI trends")
assert r.success and "research" in r.final_outputs and "analysis" in r.final_outputs and "synthesis" in r.final_outputs
print(f"  PASS - Research/Analysis/Synthesis pipeline")

# Test 4: Debate with Judge
print("\n[4] Debate with Judge")
agents = [Agent("Pro", lambda t, **kw: "pro_arg"),
          Agent("Con", lambda t, **kw: "con_arg"),
          Agent("Judge", lambda t, **kw: "verdict")]
s = SocialAlgorithms("debate", agents, algorithm_type=SocialAlgorithmType.DEBATE_WITH_JUDGE)
r = s.run("AI regulation", algorithm_args={"rounds": 2})
assert r.success and len(r.final_outputs["pro_arguments"]) == 2
print(f"  PASS - {len(r.final_outputs['pro_arguments'])} rounds, verdict delivered")

# Test 5: Council of Judges
print("\n[5] Council of Judges")
agents = [Agent(f"J{i}", (lambda i: lambda t, **kw: "APPROVE" if i < 3 else "REJECT")(i)) for i in range(5)]
s = SocialAlgorithms("council", agents, algorithm_type=SocialAlgorithmType.COUNCIL_OF_JUDGES)
r = s.run("Evaluate article")
assert r.success and r.final_outputs["verdict"] == "APPROVED"
print(f"  PASS - Verdict: {r.final_outputs['verdict']} ({r.final_outputs['approve_count']}/{r.final_outputs['reject_count']})")

# Test 6: Custom
print("\n[6] Custom Algorithm")
def custom_alg(agents, task, **kw):
    return {a.name: a.run(f"Process: {task}", **kw) for a in agents}
agents = [Agent("V", lambda t, **kw: f"Validated"), Agent("F", lambda t, **kw: f"Formatted")]
s = SocialAlgorithms("custom", agents, social_algorithm=custom_alg)
r = s.run("test")
assert r.success and len(r.final_outputs) == 2
print(f"  PASS - {len(r.final_outputs)} custom results")

# Test 7: Add/Remove
print("\n[7] Dynamic Agent Management")
agents = [Agent("A", lambda t, **kw: "A")]
s = SocialAlgorithms("dyn", agents)
s.add_agent(Agent("B", lambda t, **kw: "B"))
assert len(s.agents) == 2
s.add_agent(Agent("C", lambda t, **kw: "C"))
assert len(s.agents) == 3
s.remove_agent("B")
assert len(s.agents) == 2
print(f"  PASS - Add/Remove works correctly")

# Test 8: Async
print("\n[8] Async Concurrent")
@pytest.mark.asyncio
async def test_async():
    agents = [Agent(f"Async{i}", (lambda i: lambda t, **kw: f"R{i}")(i)) for i in range(3)]
    s = SocialAlgorithms("async", agents, algorithm_type=SocialAlgorithmType.CONCURRENT)
    r = await s.run_async("test")
    assert r.success and len(r.final_outputs) == 3
    return len(r.final_outputs)
count = asyncio.run(test_async())
print(f"  PASS - {count} async results")

print("\n" + "=" * 60)
print("TODOS OS TESTES PASSARAM (8/8)")
print("=" * 60)


if __name__ == "__main__":
    main()
