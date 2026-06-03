"""
lean_verifier.py — Lean 4 Proof Verification
Session 11: Phase C Implementation

Verifies Lean proof code by running through Lean compiler.
Timeout: 120s (increased from 30s for complex proofs)
"""

import subprocess
import re
import json
from pathlib import Path
from typing import NamedTuple, Optional
from datetime import datetime


class VerificationResult(NamedTuple):
    """Result of Lean proof verification"""
    problem_id: str
    status: str  # "success", "partial", "failed"
    output: str
    error: Optional[str]
    timestamp: str
    duration_sec: float


class LeanVerifier:
    """Verify Lean 4 proofs using lean.exe"""
    
    def __init__(self, lean_path: str = r"C:\Users\marce\Downloads\lean-4.30.0-windows\lean-4.30.0-windows\bin\lean.exe"):
        """
        Initialize verifier
        
        Args:
            lean_path: Path to Lean 4 executable
        """
        self.lean_path = lean_path
        self.timeout = 120  # seconds (increased from 30s)
        self.verified_count = 0
    
    def verify_code(
        self,
        problem_id: str,
        lean_code: str,
        temp_dir: Optional[str] = None
    ) -> VerificationResult:
        """
        Verify a Lean proof code
        
        Args:
            problem_id: Problem identifier
            lean_code: Lean 4 code to verify
            temp_dir: Temporary directory for .lean files (default: /tmp)
            
        Returns:
            VerificationResult with status, output, error
        """
        if temp_dir is None:
            temp_dir = r"C:\Users\marce\OpenCode_Ecosystem\aletheia-superhuman-validation\temp"
        
        # Create temp directory if needed
        Path(temp_dir).mkdir(parents=True, exist_ok=True)
        
        # Write Lean file
        temp_file = Path(temp_dir) / f"{problem_id}.lean"
        try:
            temp_file.write_text(lean_code, encoding="utf-8")
        except Exception as e:
            return VerificationResult(
                problem_id=problem_id,
                status="failed",
                output="",
                error=f"Failed to write Lean file: {str(e)}",
                timestamp=datetime.now().isoformat(),
                duration_sec=0
            )
        
        # Run Lean verification
        try:
            start_time = datetime.now()
            result = subprocess.run(
                [self.lean_path, str(temp_file)],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            duration = (datetime.now() - start_time).total_seconds()
            
            # Parse output
            status, output, error = self._parse_output(
                result.stdout, result.stderr, result.returncode
            )
            
            self.verified_count += 1
            
            return VerificationResult(
                problem_id=problem_id,
                status=status,
                output=output,
                error=error,
                timestamp=datetime.now().isoformat(),
                duration_sec=round(duration, 2)
            )
        
        except subprocess.TimeoutExpired:
            return VerificationResult(
                problem_id=problem_id,
                status="failed",
                output="",
                error=f"Timeout (>{self.timeout}s)",
                timestamp=datetime.now().isoformat(),
                duration_sec=float(self.timeout)
            )
        
        except FileNotFoundError:
            return VerificationResult(
                problem_id=problem_id,
                status="failed",
                output="",
                error=f"Lean executable not found: {self.lean_path}",
                timestamp=datetime.now().isoformat(),
                duration_sec=0
            )
        
        except Exception as e:
            return VerificationResult(
                problem_id=problem_id,
                status="failed",
                output="",
                error=f"Verification error: {str(e)}",
                timestamp=datetime.now().isoformat(),
                duration_sec=0
            )
        
        finally:
            # Clean up
            try:
                temp_file.unlink()
            except:
                pass
    
    def _parse_output(
        self,
        stdout: str,
        stderr: str,
        returncode: int
    ) -> tuple:
        """
        Parse Lean compiler output
        
        Args:
            stdout: Standard output
            stderr: Standard error
            returncode: Return code
            
        Returns:
            Tuple of (status, output, error)
        """
        output = stdout + "\n" + stderr
        
        # Success: return code 0 and no "error" messages
        if returncode == 0 and "error" not in stderr.lower():
            return ("success", output, None)
        
        # Partial: code compiles but has "sorry" statements
        if "sorry" in output or returncode == 0:
            if "error" not in stderr.lower():
                return ("partial", output, None)
        
        # Failed: compilation errors
        if returncode != 0 or "error" in stderr.lower():
            return ("failed", output, stderr)
        
        # Default
        return ("failed", output, stderr)
    
    def batch_verify(
        self,
        candidates: list,
        temp_dir: Optional[str] = None
    ) -> list:
        """
        Verify multiple proofs
        
        Args:
            candidates: List of ProofCandidate objects
            temp_dir: Temporary directory for .lean files
            
        Returns:
            List of VerificationResult objects
        """
        results = []
        for candidate in candidates:
            result = self.verify_code(
                problem_id=candidate.problem_id,
                lean_code=candidate.lean_code,
                temp_dir=temp_dir
            )
            results.append(result)
        
        return results
    
    def summary(self, results: list) -> dict:
        """
        Generate summary statistics
        
        Args:
            results: List of VerificationResult objects
            
        Returns:
            Dictionary with summary statistics
        """
        total = len(results)
        success = sum(1 for r in results if r.status == "success")
        partial = sum(1 for r in results if r.status == "partial")
        failed = sum(1 for r in results if r.status == "failed")
        
        avg_duration = sum(r.duration_sec for r in results) / total if total > 0 else 0
        
        return {
            "total": total,
            "success": success,
            "partial": partial,
            "failed": failed,
            "success_rate": round(100 * success / total, 1) if total > 0 else 0,
            "avg_duration_sec": round(avg_duration, 2)
        }


# Example usage
if __name__ == "__main__":
    verifier = LeanVerifier()
    
    # Test simple proof
    test_code = """theorem test_simple : 2 + 2 = 4 := by
  norm_num"""
    
    result = verifier.verify_code("TEST001", test_code)
    
    print(f"✓ Verification for {result.problem_id}")
    print(f"  Status: {result.status}")
    print(f"  Duration: {result.duration_sec}s")
    if result.error:
        print(f"  Error: {result.error}")
