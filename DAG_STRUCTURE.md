# Multi-Agent Debate DAG Structure

## Visual Representation

```
┌─────────────────┐
│ UserInputNode   │
│ (Topic Input)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ RoundsController│
│ Node            │
│ (Turn Manager)  │
└───┬───────┬─────┘
    │       │
    │   ┌───┴───┐
    ▼   ▼       ▼
┌─────────────────┐    ┌─────────────────┐
│ AgentANode      │ ↔  │ AgentBNode      │
│ (Scientist)     │    │ (Philosopher)   │
└────────┬────────┘    └────────┬────────┘
         │                      │
         └──────────┬───────────┘
                    ▼
         ┌─────────────────┐
         │ JudgeNode       │
         │ (Evaluation)    │
         └────────┬────────┘
                  ▼
         ┌─────────────────┐
         │ END             │
         └─────────────────┘
```

## Node Descriptions

### 1. UserInputNode
- **Purpose**: Accepts and validates the debate topic
- **Input**: User input via CLI
- **Output**: Validated topic string
- **Validation**: 
  - Minimum length (10 characters)
  - Maximum length (200 characters)
  - No inappropriate content

### 2. RoundsControllerNode
- **Purpose**: Manages the 8-round debate structure
- **Responsibilities**:
  - Track current round (1-8)
  - Enforce turn order (AgentA → AgentB → AgentA...)
  - Prevent out-of-turn execution
  - Terminate after 8 rounds

### 3. AgentANode (Scientist)
- **Persona**: Evidence-based, logical reasoning
- **Characteristics**:
  - Uses scientific terminology
  - References empirical data
  - Employs structured arguments
  - Focuses on observable phenomena

### 4. AgentBNode (Philosopher)
- **Persona**: Ethical reasoning, logical analysis
- **Characteristics**:
  - Considers moral implications
  - Examines underlying assumptions
  - Uses thought experiments
  - Discusses historical context

### 5. JudgeNode
- **Purpose**: Evaluates debate and declares winner
- **Analysis Criteria**:
  - Argument quality (40%)
  - Coherence score (30%)
  - Relevance score (30%)
- **Output**: Winner, summary, and reasoning

### 6. MemoryNode (Implicit)
- **Purpose**: Maintains debate transcript and context
- **Functions**:
  - Stores all turns with metadata
  - Provides agent-specific context
  - Detects repetitions
  - Checks topic coherence

## Flow Control

1. **Entry**: UserInputNode
2. **Loop**: RoundsControllerNode coordinates 8 rounds
   - Alternates between AgentANode and AgentBNode
   - Each agent gets 4 turns total
3. **Exit**: JudgeNode evaluates and declares winner
4. **Termination**: END node

## Validation Mechanisms

### Turn Enforcement
```python
# In RoundsControllerNode
if round_num % 2 == 1:
    next_agent = "AgentA"
else:
    next_agent = "AgentB"
```

### Repetition Detection
- String similarity using SequenceMatcher
- Threshold: 0.95 (very lenient for demo)
- Prevents substantially similar arguments

### Topic Coherence
- Keyword overlap calculation
- Ensures responses stay on topic
- Prevents topic drift

## Data Flow

```
User Input → State Update → Node Processing → Memory Update → Next Node
```

### State Structure
```python
DebateState:
- topic: str
- current_round: int
- next_agent: str
- rounds_completed: int
- memory: DebateMemory
- status: DebateStatus
- winner: Optional[str]
```

### Memory Structure
```python
DebateMemory:
- turns: List[TurnRecord]
- summary: str
- current_round: int
- next_agent: str
```

## Logging

All events are logged to JSONL files:
- State transitions
- Agent responses
- Memory updates
- Validation errors
- Final judgment

## Configuration

Key parameters:
- `total_rounds`: 8 (fixed)
- `similarity_threshold`: 0.95 (repetition detection)
- `coherence_threshold`: 0.7 (topic drift detection)
- `max_tokens_per_response`: 200
- Personas: scientist, philosopher (customizable)

## Extension Points

1. **New Personas**: Add persona files to `persona_templates/`
2. **LLM Integration**: Replace `_generate_response()` in AgentNode
3. **Custom Validation**: Modify validation methods in nodes
4. **New Topics**: System automatically adapts to any debate topic

## Error Handling

- **Turn Order Violations**: Rejected with error message
- **Repetitions**: Detected and rejected
- **Topic Drift**: Coherence checking prevents off-topic responses
- **Empty Responses**: Validated and rejected

## Determinism

- Use `--seed` parameter for reproducible runs
- Response selection is deterministic based on round and topic
- Logging includes timestamps for traceability