<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# TMA v5.0 MICRO - Operações Atômicas Detalhadas

## 1. Definição de Operação Atômica

Uma **operação atômica MICRO** é uma unidade de trabalho **indivisível** que:

- Recebe entrada estruturada
- Executa lógica bem-definida
- Produz saída validada
- Registra feedback
- Cria checkpoint
- Não pode ser interrompida

## 2. Anatomia de uma Operação Atômica

```python
class AtomicOperation:
    barrier_id: str              # SB1.1, SB2.5, etc
    operation_name: str          # "Extract Concepts"
    input_schema: Dict           # Estrutura esperada
    output_schema: Dict          # Estrutura produzida
    constraints: List[Constraint]  # 5-12 constraints
    timeout_ms: int              # 5000-30000ms
    retry_count: int             # 1-3 retentativas
    fallback_strategy: str       # "cache", "default", "skip"
    
    def execute(self, input_data: Dict) -> Dict:
        """Executa operação atomicamente"""
        # 1. Validar entrada
        # 2. Executar lógica
        # 3. Validar saída
        # 4. Registrar feedback
        # 5. Criar checkpoint
        # 6. Retornar resultado
```

## 3. Exemplo Completo: SB1.1 (Extract Concepts)

### Definição

```yaml
Barrier: SB1.1
Operation: Extract Concepts
Category: Discovery
Layer: 1
Complexity: 0.4
Confidence: 0.85

Input:
  - domain_text: str (1000-50000 chars)
  - language: str ("en", "pt", "es")
  - max_concepts: int (10-100)

Output:
  - concepts: List[Concept]
  - extraction_quality: float (0-1)
  - extraction_time_ms: float

Constraints:
  - min_concepts: 5
  - max_concepts: 100
  - concept_quality_min: 0.7
  - concept_length_min: 3 chars
  - concept_length_max: 100 chars
  - extraction_time_max: 5000ms
  - language_support: ["en", "pt", "es"]
  - uniqueness_ratio: > 0.95
  - coverage_ratio: > 0.8
  - confidence_min: 0.7
  - error_rate_max: 0.05
  - retry_count_max: 3
```

### Implementação

```python
class SB1_1_ExtractConcepts(AtomicOperation):
    def __init__(self):
        self.barrier_id = "SB1.1"
        self.operation_name = "Extract Concepts"
        self.timeout_ms = 5000
        self.retry_count = 3
        self.fallback_strategy = "cache"
    
    def execute(self, input_data: Dict) -> Dict:
        start_time = time.time()
        
        try:
            # 1. Validar entrada
            self._validate_input(input_data)
            
            # 2. Extrair conceitos
            concepts = self._extract_concepts(
                input_data["domain_text"],
                input_data["language"],
                input_data["max_concepts"]
            )
            
            # 3. Validar saída
            self._validate_output(concepts)
            
            # 4. Calcular métricas
            execution_time = (time.time() - start_time) * 1000
            quality_score = self._calculate_quality(concepts)
            
            # 5. Registrar feedback
            self._record_feedback(
                success=True,
                quality_score=quality_score,
                execution_time_ms=execution_time
            )
            
            # 6. Criar checkpoint
            self._create_checkpoint({
                "barrier_id": self.barrier_id,
                "concepts": concepts,
                "quality": quality_score,
                "time": execution_time
            })
            
            return {
                "concepts": concepts,
                "extraction_quality": quality_score,
                "extraction_time_ms": execution_time,
                "success": True
            }
        
        except Exception as e:
            # Tratamento de erro
            self._handle_error(e)
            return self._execute_fallback(input_data)
    
    def _validate_input(self, input_data: Dict):
        """Valida entrada contra schema"""
        assert "domain_text" in input_data
        assert len(input_data["domain_text"]) >= 1000
        assert len(input_data["domain_text"]) <= 50000
        assert input_data["language"] in ["en", "pt", "es"]
        assert 10 <= input_data["max_concepts"] <= 100
    
    def _extract_concepts(self, text: str, lang: str, max_count: int) -> List:
        """Extrai conceitos usando LLM"""
        # Implementação específica
        pass
    
    def _validate_output(self, concepts: List):
        """Valida saída contra constraints"""
        assert len(concepts) >= 5
        assert len(concepts) <= 100
        for concept in concepts:
            assert len(concept) >= 3
            assert len(concept) <= 100
            assert concept["quality"] >= 0.7
    
    def _calculate_quality(self, concepts: List) -> float:
        """Calcula qualidade da extração"""
        # Média ponderada de métricas
        pass
    
    def _record_feedback(self, success: bool, quality_score: float, execution_time_ms: float):
        """Registra feedback para aprendizado"""
        feedback = OperationFeedback(
            barrier_id=self.barrier_id,
            operation_name=self.operation_name,
            success=success,
            quality_score=quality_score,
            execution_time_ms=execution_time_ms
        )
        # Salvar em banco de dados
    
    def _create_checkpoint(self, state: Dict):
        """Cria checkpoint do estado"""
        checkpoint = Checkpoint(
            barrier_id=self.barrier_id,
            timestamp=datetime.now(),
            state=state
        )
        # Salvar checkpoint
    
    def _handle_error(self, error: Exception):
        """Trata erro e registra"""
        # Logging, alertas, etc
        pass
    
    def _execute_fallback(self, input_data: Dict) -> Dict:
        """Executa estratégia de fallback"""
        if self.fallback_strategy == "cache":
            return self._get_cached_result(input_data)
        elif self.fallback_strategy == "default":
            return self._get_default_result()
        else:
            return {"success": False, "error": "Operation failed"}
```

## 4. Padrão de Operações Atômicas

### Padrão 1: Extração

```
Input: Raw Data
  ↓
Validate Input
  ↓
Extract Information
  ↓
Validate Output
  ↓
Calculate Metrics
  ↓
Record Feedback
  ↓
Create Checkpoint
  ↓
Output: Structured Data
```

### Padrão 2: Validação

```
Input: Data to Validate
  ↓
Check Constraints
  ↓
Generate Report
  ↓
Determine Status
  ↓
Record Feedback
  ↓
Create Checkpoint
  ↓
Output: Validation Result
```

### Padrão 3: Transformação

```
Input: Source Data
  ↓
Validate Input
  ↓
Transform Data
  ↓
Validate Output
  ↓
Optimize Result
  ↓
Record Feedback
  ↓
Create Checkpoint
  ↓
Output: Transformed Data
```

## 5. Composição de Operações (Sync Barriers)

### Exemplo: SB1 (Domain Discovery)

```
SB1.1 (Extract Concepts)
  ↓ [Feedback: concepts_extracted]
SB1.2 (Validate Concepts)
  ↓ [Feedback: concepts_validated]
SB1.3 (Deduplicate Concepts)
  ↓ [Feedback: concepts_deduplicated]
SB1.4 (Rank Concepts)
  ↓ [Feedback: concepts_ranked]
  ↓
[SYNC BARRIER 1: Domain Model Validation]
  ↓
Output: DomainModel
```

## 6. Tratamento de Erros em Operações Atômicas

### Estratégias de Retry

```python
class RetryStrategy:
    max_retries: int = 3
    backoff_factor: float = 1.5
    timeout_ms: int = 5000
    
    def execute_with_retry(self, operation: AtomicOperation, input_data: Dict) -> Dict:
        for attempt in range(self.max_retries):
            try:
                return operation.execute(input_data)
            except TimeoutError:
                if attempt < self.max_retries - 1:
                    wait_time = self.timeout_ms * (self.backoff_factor ** attempt)
                    time.sleep(wait_time / 1000)
                    continue
                else:
                    return operation.execute_fallback(input_data)
            except ValidationError as e:
                # Não retry em erro de validação
                return operation.execute_fallback(input_data)
            except Exception as e:
                if attempt < self.max_retries - 1:
                    continue
                else:
                    raise
```

### Fallback Strategies

```python
class FallbackStrategy:
    CACHE = "cache"           # Usar resultado em cache
    DEFAULT = "default"       # Usar valor padrão
    SKIP = "skip"             # Pular operação
    PROPAGATE = "propagate"   # Propagar erro
    
    def execute_fallback(self, strategy: str, operation: AtomicOperation) -> Dict:
        if strategy == self.CACHE:
            return operation.get_cached_result()
        elif strategy == self.DEFAULT:
            return operation.get_default_result()
        elif strategy == self.SKIP:
            return {"skipped": True}
        elif strategy == self.PROPAGATE:
            raise OperationFailedError()
```

## 7. Métricas de Operações Atômicas

### Por Operação

```python
@dataclass
class OperationMetrics:
    barrier_id: str
    operation_name: str
    total_executions: int
    successful: int
    failed: int
    avg_execution_time_ms: float
    avg_quality_score: float
    avg_confidence: float
    success_rate: float
    improvement_trend: float
    lessons_extracted: int
```

### Agregadas

```python
@dataclass
class LayerMetrics:
    layer_name: str  # "Discovery", "Reasoning", etc
    total_barriers: int
    total_operations: int
    total_constraints: int
    avg_success_rate: float
    avg_execution_time_ms: float
    total_feedback_points: int
    total_lessons: int
```

## 8. Exemplo Completo: Ciclo de Operações

```
Ciclo N:
  1. SB1.1: Extract Concepts (2500ms, quality=0.92)
     └─ Feedback: ✓ Success
     └─ Checkpoint: Saved
  
  2. SB1.2: Validate Concepts (1800ms, quality=0.95)
     └─ Feedback: ✓ Success
     └─ Checkpoint: Saved
  
  3. SB1.3: Deduplicate (1200ms, quality=0.98)
     └─ Feedback: ✓ Success
     └─ Checkpoint: Saved
  
  4. SB1.4: Rank Concepts (900ms, quality=0.96)
     └─ Feedback: ✓ Success
     └─ Checkpoint: Saved
  
  [SYNC BARRIER 1]
  └─ Validation: ✓ PASSED
  └─ Constraints: 70/70 ✓
  └─ Output: DomainModel
  
  Lições Extraídas:
  - Extração rápida (2500ms < 5000ms)
  - Qualidade alta (0.92 > 0.9)
  - Padrão: Usar estratégia X para domínios similares
  
Ciclo N+1:
  └─ Inicia com lições do Ciclo N
  └─ Otimizações aplicadas
  └─ Esperado: Melhoria de 5-10%
```

---

**Versão:** 5.0 MICRO | **Status:** Production Ready
