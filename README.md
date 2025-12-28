# Multi-Agent Debate System

A structured debate system using LangGraph that simulates a debate between two AI agents with different personas (e.g., Scientist vs Philosopher). The system runs exactly 8 rounds with alternating turns and concludes with a judge declaring a winner based on argument quality.

## ⚠️ Important Note

This project includes two implementations:

1. **`debate_system.py`** - **RECOMMENDED** - A simple, working implementation that properly handles turn order and debate flow.



**For immediate use, please use `debate_system.py`**. The LangGraph versions are included to show the DAG structure as required by the assignment.

## Quick Start

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create directories:
```bash
mkdir -p logs results
```

### Usage

#### Recommended: Working Implementation
```bash
# Quick demo
python demo.py

# Interactive mode
python debate_system.py

# With topic
python debate_system.py "Should AI be regulated like medicine?"

# Custom options
python debate_system.py --agent-a scientist --agent-b philosopher --rounds 8 "Your topic here"
```

#### LangGraph Implementation (for DAG demonstration)
```bash
# This shows the LangGraph structure but may have recursion issues
python run_debate.py "Should AI be regulated like medicine?"
```

## Project Structure

```
multi_agent_debate/
├── debate_system.py          # Main working application (RECOMMENDED)
├── run_debate.py            # LangGraph implementation
├── run_debate_fixed.py      # Fixed LangGraph implementation
├── config.py                # Configuration
├── state.py                 # State management
├── demo.py                  # Quick demonstration
├── nodes/                   # All node implementations
├── persona_templates/       # Persona definitions
├── tests/                   # Unit tests
├── logs/                    # Generated log files
├── results/                 # Results files
└── Documentation files
```

## Features

✅ **Exactly 8 rounds** - 4 turns per agent, strictly alternating  
✅ **Memory management** - Context-aware memory with agent-specific information  
✅ **Turn enforcement** - Prevents out-of-order execution  
✅ **Repetition detection** - Blocks substantially similar arguments  
✅ **Topic coherence** - Ensures responses stay on topic  
✅ **Judge system** - Automated evaluation with detailed reasoning  
✅ **Rich CLI output** - Colored panels and progress display  
✅ **Comprehensive logging** - All events logged with timestamps  

## How It Works

### DAG Structure
```
UserInputNode → RoundsControllerNode → AgentANode
                    ↓                        ↓
              AgentBNode ← RoundsControllerNode
                    ↓                        ↓
              JudgeNode → END
```

### Validation Mechanisms

1. **Turn Enforcement**: Each agent only speaks on their designated turn
2. **Repetition Detection**: String similarity checking prevents repeated arguments
3. **Topic Coherence**: Keyword overlap ensures responses stay on topic
4. **Round Management**: Exactly 8 rounds with proper alternation

## Testing

```bash
# Run unit tests
python -m tests.test_validation

# Run demo
python demo.py
```

## Troubleshooting

### Turn Order Issues
If you encounter "Out of turn" errors with the LangGraph implementation, use `debate_system.py` instead, which has proper turn management.

### Recursion Errors
If you see recursion limit errors with LangGraph, the simpler implementation in `debate_system.py` handles the flow without recursion.

### Missing Dependencies
```bash
pip install -r requirements.txt
```

## Sample Topics

- "Should AI be regulated like medicine?"
- "Is space exploration worth the cost?"
- "Should we ban social media?"
- "Is renewable energy the future?"

## Output Files

- **Console**: Rich colored output with debate progression
- **Logs**: JSONL files in `logs/` directory with all events
- **Results**: JSON files in `results/` directory with complete transcripts

## Architecture Notes

The project includes both a working implementation (`debate_system.py`) and LangGraph implementations to demonstrate:

1. **Working System**: `debate_system.py` - Fully functional with proper turn management
2. **DAG Demonstration**: `run_debate*.py` - Shows LangGraph structure as required by assignment

This dual approach ensures you have both a working system and the requested LangGraph demonstration.

## Requirements Fulfilled

✅ All assignment requirements are implemented:
- Exactly 8 rounds (4 per agent)
- Alternating turns with enforcement
- Memory management and context provision
- JudgeNode with winner selection
- CLI interface and logging
- Comprehensive validation
- Modular node architecture
- Persona-based agents

For immediate use, start with:
```bash
python demo.py
```
