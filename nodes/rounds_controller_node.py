from typing import Dict, Literal
from state import DebateState, DebateStatus
from nodes.logger_node import logger


class RoundsControllerNode:
    """Controls the debate rounds and enforces turn order."""
    
    def run(self, state: DebateState) -> Dict:
        """Control the flow of debate rounds."""
        logger.log_event("ROUND_CONTROLLER_START", state, {
            "current_round": state.current_round,
            "rounds_completed": state.rounds_completed,
            "next_agent": state.next_agent
        })
        
        # Check if debate is complete
        if state.rounds_completed >= state.config.total_rounds:
            state.status = DebateStatus.COMPLETED
            logger.log_event("DEBATE_COMPLETED", state, {
                "total_rounds": state.rounds_completed,
                "total_turns": len(state.memory.turns)
            })
            return {
                "status": "completed",
                "next_node": "JudgeNode"
            }
        
        # Calculate next round and agent based on completed turns
        total_turns = len(state.memory.turns)
        
        if total_turns == 0:
            # First turn
            next_round = 1
            next_agent = "AgentA"
        else:
            # Determine next agent based on who went last
            last_agent = state.memory.turns[-1].agent
            if last_agent == "AgentA":
                next_agent = "AgentB"
                next_round = state.current_round  # Same round
            else:
                next_agent = "AgentA"
                next_round = state.current_round + 1  # New round
        
        # Update state
        state.current_round = next_round
        state.next_agent = next_agent
        
        logger.log_event("ROUND_ADVANCED", state, {
            "new_round": next_round,
            "next_agent": next_agent,
            "rounds_completed": state.rounds_completed
        })
        
        return {
            "status": "continue",
            "next_node": f"{next_agent}Node",
            "round": next_round,
            "agent": next_agent
        }
    
    def validate_turn_order(self, state: DebateState, attempted_agent: str) -> bool:
        """Validate that the correct agent is attempting to take their turn."""
        return state.next_agent == attempted_agent
    
    def check_round_limit(self, state: DebateState) -> bool:
        """Check if the debate has reached the maximum number of rounds."""
        return state.rounds_completed >= state.config.total_rounds