# Quick Start Guide

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create directories:
```bash
mkdir -p logs results
```

## Running the System

### Quick Demo
```bash
python demo.py
```

### Interactive Mode
```bash
python debate_system.py
```

### With Topic
```bash
python debate_system.py "Should AI be regulated like medicine?"
```

### Custom Options
```bash
python debate_system.py --agent-a scientist --agent-b philosopher --rounds 8 "Your topic here"
```

## Files

- `debate_system.py` - Main application (recommended)
- `run_debate.py` - Alternative LangGraph implementation
- `demo.py` - Quick demonstration
- `generate_dag.py` - DAG visualization
- `tests/test_validation.py` - Unit tests

## Sample Topics

- "Should AI be regulated like medicine?"
- "Is space exploration worth the cost?"
- "Should we ban social media?"
- "Is renewable energy the future?"
- "Should genetic engineering be allowed?"

## Output

- Console: Rich colored output with debate progression
- Logs: JSONL files in `logs/` directory
- Results: JSON files in `results/` directory

## Testing

```bash
python -m tests.test_validation
```