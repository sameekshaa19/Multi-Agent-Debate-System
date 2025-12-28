from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum
from config import DebateConfig, DEFAULT_CONFIG


class DebateStatus(str, Enum):
    """Status of the debate."""
    INITIALIZED = "initialized"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"


class TurnRecord(BaseModel):
    """Record of a single turn in the debate."""
    round: int
    agent: str  # "AgentA" or "AgentB"
    persona: str  # "scientist", "philosopher", etc.
    text: str
    timestamp: str
    meta: Dict[str, Any] = Field(default_factory=dict)


class DebateMemory(BaseModel):
    """Structured memory of the debate."""
    turns: List[TurnRecord] = Field(default_factory=list)
    summary: str = ""
    current_round: int = 0
    next_agent: Literal["AgentA", "AgentB"] = "AgentA"
    
    def add_turn(self, turn: TurnRecord) -> None:
        """Add a turn to memory."""
        self.turns.append(turn)
        self.current_round = turn.round
        self._update_summary()
    
    def _update_summary(self) -> None:
        """Update the summary of the debate so far."""
        if not self.turns:
            self.summary = "Debate not started."
            return
        
        summary_parts = []
        summary_parts.append(f"Debate is at round {self.current_round}.")
        
        # Key points from each agent
        agent_a_points = [t.text[:100] + "..." if len(t.text) > 100 else t.text 
                         for t in self.turns[-3:] if t.agent == "AgentA"]
        agent_b_points = [t.text[:100] + "..." if len(t.text) > 100 else t.text 
                         for t in self.turns[-3:] if t.agent == "AgentB"]
        
        if agent_a_points:
            summary_parts.append(f"AgentA arguments: {' | '.join(agent_a_points)}")
        if agent_b_points:
            summary_parts.append(f"AgentB arguments: {' | '.join(agent_b_points)}")
        
        self.summary = " ".join(summary_parts)
    
    def get_agent_context(self, agent: str) -> str:
        """Get context relevant for the specified agent."""
        context_parts = []
        context_parts.append(f"Debate summary: {self.summary}")
        
        # Get last few turns for context
        recent_turns = self.turns[-4:]  # Last 2 rounds
        for turn in recent_turns:
            if turn.agent != agent:  # Only include opponent's turns
                context_parts.append(f"[{turn.persona}] {turn.text}")
        
        return "\n".join(context_parts)


class DebateState(BaseModel):
    """Main state for the LangGraph debate workflow."""
    
    # Configuration
    config: DebateConfig = Field(default_factory=lambda: DEFAULT_CONFIG)
    
    # Core debate info
    topic: str = ""
    status: DebateStatus = DebateStatus.INITIALIZED
    
    # Agent configuration
    agent_a_persona: str = "scientist"
    agent_b_persona: str = "philosopher"
    
    # State tracking
    current_round: int = 0
    next_agent: Literal["AgentA", "AgentB"] = "AgentA"
    rounds_completed: int = 0
    
    # Memory
    memory: DebateMemory = Field(default_factory=DebateMemory)
    
    # Validation and errors
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    # Final results
    winner: Optional[Literal["AgentA", "AgentB"]] = None
    judge_summary: str = ""
    judge_reasoning: str = ""
    
    # Internal state for node communication
    _next_step: str = "UserInputNode"
    _last_response: str = ""
    _turn_rejected: bool = False
    _rejection_reason: str = ""
    
    class Config:
        arbitrary_types_allowed = True