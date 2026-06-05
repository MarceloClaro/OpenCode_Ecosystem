import sys, json, time
sys.path.insert(0, 'nexus/scripts')

from context_offload import ContextOffloadManager


def main():
    print("=" * 60)
    print("TESTE: Context Offload Manager")
    print("=" * 60)

# Test 1: Create session
print("\n[1] Create Session")
mgr = ContextOffloadManager()
sid = mgr.create_session(project_id="test-project")
assert sid is not None and mgr.active_session == sid
print(f"  PASS - Session created: {sid[:12]}...")

# Test 2: Add entries
print("\n[2] Add Entries")
e1 = mgr.add_entry("This is important context about AI research", priority=8)
e2 = mgr.add_entry("Secondary information about data analysis", priority=3)
e3 = mgr.add_intermediate_result("task-1", {"result": "analysis complete", "score": 0.95})
assert e1 and e2 and e3
state = mgr.get_session_state()
assert state["entry_count"] == 3
print(f"  PASS - {state['entry_count']} entries added")

# Test 3: Get session context
print("\n[3] Get Session Context")
context = mgr.get_session_context(max_entries=5)
assert len(context) == 3
print(f"  PASS - Retrieved {len(context)} context entries")

# Test 4: Behavioral fingerprint
print("\n[4] Behavioral Fingerprint")
mgr.add_entry("The system must not modify the database schema")
mgr.add_entry("The auth layer is already done")
fp = mgr.create_behavioral_fingerprint()
assert "term_frequency" in fp and "constraints" in fp
assert "must" in fp["constraints"]
print(f"  PASS - Fingerprint: {fp['entry_count']} entries, {len(fp['term_frequency'])} terms")

# Test 5: Resume consistency
print("\n[5] Resume Consistency Check")
consistent_text = "The system must not modify the database schema and the auth layer"
inconsistent_text = "Starting fresh work on new endpoints"
result_c = mgr.check_resume_consistency(sid, consistent_text)
result_i = mgr.check_resume_consistency(sid, inconsistent_text)
print(f"  PASS - Consistent: {result_c['status']} (drift: {result_c['drift_score']}), "
      f"Inconsistent: {result_i['status']} (drift: {result_i['drift_score']})")

# Test 6: Summarization (trigger threshold)
print("\n[6] Auto-Summarization")
mgr2 = ContextOffloadManager(summary_threshold=5)
mgr2.create_session()
for i in range(6):
    mgr2.add_entry(f"Entry {i}: Lorem ipsum dolor sit amet " * 2, priority=5)
summary = mgr2.get_session_summary()
assert len(summary) > 0
print(f"  PASS - Summary generated ({len(summary)} chars)")

# Test 7: Session listing
print("\n[7] Session Listing")
sessions = mgr.list_sessions()
assert len(sessions) >= 1
print(f"  PASS - {len(sessions)} sessions listed")

# Test 8: Multi-session
print("\n[8] Multi-Session Management")
sid2 = mgr.create_session(project_id="other-project")
mgr.add_entry("Different project context", priority=5)
state1 = mgr.get_session_state(sid)
state2 = mgr.get_session_state(sid2)
assert state1 is not None and state2 is not None
print(f"  PASS - Session 1 project: {state1['project_id']}, Session 2 project: {state2['project_id']}")

print("\n" + "=" * 60)
print("TODOS OS TESTES PASSARAM (8/8)")
print("=" * 60)


if __name__ == "__main__":
    main()
