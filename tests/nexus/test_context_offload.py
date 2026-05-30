"""Testes para ContextOffloadManager (logica pura)."""

import sys; from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"nexus"/"scripts"))
import pytest
from context_offload import ContextOffloadManager

class TestContextOffload:
    def test_create_session(self,tmp_path):
        m=ContextOffloadManager(base_dir=str(tmp_path/"co"))
        s=m.create_session(); assert s.startswith("session-")
    def test_add_entry(self,tmp_path):
        m=ContextOffloadManager(base_dir=str(tmp_path/"co"))
        m.create_session(); e=m.add_entry("hello")
        assert len(e)==12
    def test_add_without_session(self,tmp_path):
        m=ContextOffloadManager(base_dir=str(tmp_path/"co"))
        with pytest.raises(ValueError): m.add_entry("x")
    def test_intermediate_result(self,tmp_path):
        m=ContextOffloadManager(base_dir=str(tmp_path/"co"))
        m.create_session(); e=m.add_intermediate_result("t",{"k":42})
        assert m.sessions[m.active_session].entry_count==1
    def test_get_context(self,tmp_path):
        m=ContextOffloadManager(base_dir=str(tmp_path/"co"))
        m.create_session(); m.add_entry("a"); m.add_entry("b")
        assert len(m.get_session_context())==2
    def test_summary_after_threshold(self,tmp_path):
        m=ContextOffloadManager(base_dir=str(tmp_path/"co"),summary_threshold=3)
        m.create_session()
        for i in range(4): m.add_entry(f"e{i}")
        assert "Session Summary" in m.get_session_summary()
    def test_fingerprint(self,tmp_path):
        m=ContextOffloadManager(base_dir=str(tmp_path/"co"))
        m.create_session(); m.add_entry("must and should and must")
        fp=m.create_behavioral_fingerprint()
        assert "must" in fp["constraints"]
    def test_consistency_drift(self,tmp_path):
        m=ContextOffloadManager(base_dir=str(tmp_path/"co"))
        m.create_session(); m.add_entry("cat dog bird"); m.create_behavioral_fingerprint()
        r=m.check_resume_consistency(m.active_session,"math physics")
        assert r["status"]=="drift_detected"
    def test_consistency_match(self,tmp_path):
        m=ContextOffloadManager(base_dir=str(tmp_path/"co"))
        m.create_session(); m.add_entry("cat dog"); m.create_behavioral_fingerprint()
        r=m.check_resume_consistency(m.active_session,"cat dog again")
        assert r["status"]=="consistent"
    def test_list_sessions(self,tmp_path):
        m=ContextOffloadManager(base_dir=str(tmp_path/"co"))
        m.create_session(); assert len(m.list_sessions())==1
    def test_get_state_nonexistent(self,tmp_path):
        m=ContextOffloadManager(base_dir=str(tmp_path/"co"))
        assert m.get_session_state(session_id="nonexistent") is None
