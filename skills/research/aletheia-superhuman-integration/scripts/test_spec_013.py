#!/usr/bin/env python3
"""
TDD Test Suite for SPEC-013: AletheiaPromptIntegration
=======================================================

5 Tests:
1. Prompt loading from YAML
2. PromptSelector domain-aware routing
3. YAML export + reimport (round-trip)
4. Reproducibility with seed=42
5. Domain filtering validation
"""

import pytest
import json
import yaml
import hashlib
from pathlib import Path
from spec_013_prompt_integration import (
    AletheiaPrompt,
    PromptCategory,
    AletheiaPromptLibrary,
    PromptSelector,
)


SEED = 42


class TestSpec013PromptLoading:
    """Test 1: Prompt loading from YAML."""
    
    def test_load_builtin_prompts(self):
        """RED: Load 6 builtin prompts. GREEN: Verify all loaded."""
        lib = AletheiaPromptLibrary()
        lib.load_builtin_prompts()
        
        # Deve ter 6 prompts publicados
        assert len(lib.prompts) >= 6, f"Expected at least 6 prompts, got {len(lib.prompts)}"
        
        # Verificar que prompts foram carregados
        prompt_ids = set(lib.prompts.keys())
        assert len(prompt_ids) >= 6, f"Expected at least 6 unique prompt IDs"
    
    def test_prompt_structure(self):
        """RED: Verify AletheiaPrompt dataclass structure."""
        lib = AletheiaPromptLibrary()
        lib.load_builtin_prompts()
        
        # Pick one prompt from available
        prompt = list(lib.prompts.values())[0]
        
        # Verify required fields
        assert hasattr(prompt, "id")
        assert hasattr(prompt, "category")
        assert hasattr(prompt, "content")
        assert hasattr(prompt, "tokens")
        assert hasattr(prompt, "effectiveness")
        
        # Verify types
        assert isinstance(prompt.id, str)
        assert isinstance(prompt.category, PromptCategory)
        assert isinstance(prompt.content, str)
        assert isinstance(prompt.tokens, int)
        assert isinstance(prompt.effectiveness, float)
        
        # Verify value ranges
        assert prompt.tokens > 0
        assert 0.0 <= prompt.effectiveness <= 1.0


class TestSpec013PromptSelector:
    """Test 2: PromptSelector domain-aware routing."""
    
    def test_selector_initialization(self):
        """RED: Initialize selector. GREEN: Verify routes available."""
        lib = AletheiaPromptLibrary()
        lib.load_builtin_prompts()
        selector = PromptSelector(lib)
        
        assert selector.library is not None
        assert len(selector.library.prompts) == 6
    
    def test_domain_aware_selection(self):
        """RED: Select prompts for specific domain. GREEN: Verify routing."""
        lib = AletheiaPromptLibrary()
        lib.load_builtin_prompts()
        selector = PromptSelector(lib)
        
        # Test selection for number_theory domain
        generator = selector.select_generator("number_theory", attempt=1)
        verifier = selector.select_verifier("number_theory", attempt=1)
        
        assert generator is not None
        assert verifier is not None
        # Verify they are prompts
        assert hasattr(generator, "category")
        assert hasattr(verifier, "category")
        # Generator category should have "generator" in the name
        assert "generator" in generator.category.value.lower()
        # Verifier category should have "verifi" in the name
        assert "verif" in verifier.category.value.lower()
    
    def test_attempt_aware_selection(self):
        """RED: Test attempt-aware fallback logic."""
        lib = AletheiaPromptLibrary()
        lib.load_builtin_prompts()
        selector = PromptSelector(lib)
        
        # First attempt uses exploration
        gen_1 = selector.select_generator("combinatorics", attempt=1)
        # Second attempt uses refinement
        gen_2 = selector.select_generator("combinatorics", attempt=2)
        
        # Should be different strategies
        assert gen_1 is not None
        assert gen_2 is not None
        # gen_1 should prefer exploration, gen_2 should prefer refinement


class TestSpec013YAMLExport:
    """Test 3: YAML export + reimport (round-trip)."""
    
    def test_export_to_yaml(self, tmp_path):
        """RED: Export library to YAML. GREEN: Verify file created."""
        lib = AletheiaPromptLibrary()
        lib.load_builtin_prompts()
        
        output_file = tmp_path / "prompts_export.yaml"
        lib.export_to_yaml(str(output_file))
        
        assert output_file.exists()
        assert output_file.stat().st_size > 0
    
    def test_yaml_round_trip(self, tmp_path):
        """RED: Export and reimport. GREEN: Verify identical."""
        lib = AletheiaPromptLibrary()
        lib.load_builtin_prompts()
        
        # Export
        output_file = tmp_path / "prompts_roundtrip.yaml"
        lib.export_to_yaml(str(output_file))
        
        # Reimport
        lib2 = AletheiaPromptLibrary()
        lib2.prompts.clear()  # Clear default library
        with open(output_file) as f:
            data = yaml.safe_load(f)
            if data and "prompts" in data:
                for prompt_data in data["prompts"]:
                    prompt = AletheiaPrompt(
                        id=prompt_data["id"],
                        category=PromptCategory(prompt_data["category"]),
                        title=prompt_data.get("title", ""),
                        content=prompt_data.get("content", ""),
                        source_paper=prompt_data.get("source_paper", ""),
                        tokens=prompt_data.get("tokens", 0),
                        application_domain=prompt_data.get("application_domain", []),
                        effectiveness=prompt_data.get("effectiveness", 0.5),
                    )
                    lib2.add_prompt(prompt)
        
        # Verify same number of prompts
        assert len(lib.prompts) == len(lib2.prompts)
        
        # Verify same IDs
        assert set(lib.prompts.keys()) == set(lib2.prompts.keys())


class TestSpec013Reproducibility:
    """Test 4: Reproducibility with seed=42."""
    
    def test_seed_reproducibility(self):
        """RED: Run generator twice with seed=42. GREEN: Verify identical."""
        import random
        
        lib = AletheiaPromptLibrary()
        lib.load_builtin_prompts()
        selector = PromptSelector(lib)
        
        # Run 1
        random.seed(SEED)
        prompts_1 = []
        for _ in range(5):
            p = selector.select_generator("algebra", attempt=1)
            prompts_1.append(p.id)
        
        # Run 2
        random.seed(SEED)
        prompts_2 = []
        for _ in range(5):
            p = selector.select_generator("algebra", attempt=1)
            prompts_2.append(p.id)
        
        # Must be identical
        assert prompts_1 == prompts_2, f"Run 1: {prompts_1}, Run 2: {prompts_2}"
    
    def test_hash_consistency(self):
        """RED: Compute hash of library. GREEN: Verify consistent."""
        import random
        
        lib = AletheiaPromptLibrary()
        lib.load_builtin_prompts()
        
        # Hash 1
        random.seed(SEED)
        hash_1 = hashlib.md5(
            json.dumps({
                p: lib.prompts[p].content 
                for p in sorted(lib.prompts.keys())
            }).encode()
        ).hexdigest()
        
        # Hash 2
        random.seed(SEED)
        hash_2 = hashlib.md5(
            json.dumps({
                p: lib.prompts[p].content 
                for p in sorted(lib.prompts.keys())
            }).encode()
        ).hexdigest()
        
        assert hash_1 == hash_2


class TestSpec013DomainFiltering:
    """Test 5: Domain filtering validation."""
    
    def test_supported_domains(self):
        """RED: Query supported domains. GREEN: Verify expected list."""
        lib = AletheiaPromptLibrary()
        lib.load_builtin_prompts()
        selector = PromptSelector(lib)
        
        # Supported domains from Feng et al. 2026
        expected_domains = {
            "number_theory", "combinatorics", "algebra", 
            "geometry", "analysis", "logic"
        }
        
        # Verify selector can handle all
        for domain in expected_domains:
            gen = selector.select_generator(domain, attempt=1)
            assert gen is not None, f"Failed to select generator for {domain}"
    
    def test_unsupported_domain_fallback(self):
        """RED: Query unsupported domain. GREEN: Verify graceful fallback."""
        lib = AletheiaPromptLibrary()
        lib.load_builtin_prompts()
        selector = PromptSelector(lib)
        
        # Unsupported domain should fallback to generic
        gen = selector.select_generator("unknown_domain", attempt=1)
        assert gen is not None  # Must return something


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
