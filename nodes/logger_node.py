import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from state import DebateState, DebateStatus


class LoggerNode:
    """Handles all logging for the debate system."""
    
    def __init__(self, log_path: Path = Path("logs")):
        self.log_path = log_path
        self.log_path.mkdir(exist_ok=True)
        
        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_path / f"debate_log_{timestamp}.jsonl"
        self._log_entries = []
    
    def log_event(self, event_type: str, state: DebateState, details: Dict[str, Any]) -> None:
        """Log a single event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "round": state.current_round,
            "next_agent": state.next_agent,
            "status": state.status.value,
            "details": details
        }
        
        self._log_entries.append(event)
        
        # Write to file immediately
        with open(self.log_file, "a") as f:
            f.write(json.dumps(event) + "\n")
    
    def log_state_transition(self, from_node: str, to_node: str, state: DebateState) -> None:
        """Log state transitions between nodes."""
        self.log_event("STATE_TRANSITION", state, {
            "from_node": from_node,
            "to_node": to_node,
            "topic": state.topic,
            "rounds_completed": state.rounds_completed
        })
    
    def log_agent_turn(self, agent: str, persona: str, response: str, state: DebateState) -> None:
        """Log an agent's turn."""
        self.log_event("AGENT_TURN", state, {
            "agent": agent,
            "persona": persona,
            "response": response,
            "response_length": len(response)
        })
    
    def log_validation_error(self, error_type: str, reason: str, state: DebateState) -> None:
        """Log validation errors."""
        self.log_event("VALIDATION_ERROR", state, {
            "error_type": error_type,
            "reason": reason
        })
    
    def log_memory_update(self, memory_snapshot: Dict[str, Any], state: DebateState) -> None:
        """Log memory updates."""
        self.log_event("MEMORY_UPDATE", state, {
            "memory_snapshot": memory_snapshot
        })
    
    def log_judgment(self, winner: str, summary: str, reasoning: str, state: DebateState) -> None:
        """Log the final judgment."""
        self.log_event("JUDGMENT", state, {
            "winner": winner,
            "summary": summary,
            "reasoning": reasoning,
            "total_rounds": state.rounds_completed,
            "total_turns": len(state.memory.turns)
        })
    
    def get_log_file(self) -> Path:
        """Get the path to the log file."""
        return self.log_file
    
    def export_full_log(self) -> Dict[str, Any]:
        """Export the full log as a complete JSON structure."""
        return {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "total_events": len(self._log_entries),
                "log_file": str(self.log_file)
            },
            "events": self._log_entries
        }


# Global logger instance
logger = LoggerNode()