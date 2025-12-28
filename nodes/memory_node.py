from typing import Dict, List, Any
from datetime import datetime
from difflib import SequenceMatcher
from state import DebateState, DebateMemory, TurnRecord
from nodes.logger_node import logger


class MemoryNode:
    """Manages debate memory and provides context to agents."""
    
    def __init__(self):
        self.similarity_cache = {}  # Cache for similarity calculations
    
    def update_memory(self, state: DebateState, agent: str, persona: str, response: str) -> bool:
        """Update memory with a new turn and validate for repetitions."""
        logger.log_event("MEMORY_UPDATE_START", state, {
            "agent": agent,
            "persona": persona,
            "response_length": len(response)
        })
        
        # Check for repetition
        if self._check_repetition(state, response):
            logger.log_validation_error("REPETITION_DETECTED", "Response is too similar to previous arguments", state)
            return False
        
        # Create turn record
        turn = TurnRecord(
            round=state.current_round,
            agent=agent,
            persona=persona,
            text=response,
            timestamp=datetime.now().isoformat(),
            meta={
                "response_length": len(response),
                "unique_words": len(set(response.split()))
            }
        )
        
        # Update memory
        state.memory.add_turn(turn)
        
        # Update rounds completed
        state.rounds_completed += 1
        
        logger.log_memory_update({
            "turn_added": turn.model_dump(),
            "total_turns": len(state.memory.turns),
            "rounds_completed": state.rounds_completed
        }, state)
        
        return True
    
    def get_agent_context(self, state: DebateState, agent: str) -> str:
        """Get relevant context for the specified agent."""
        return state.memory.get_agent_context(agent)
    
    def _check_repetition(self, state: DebateState, new_response: str) -> bool:
        """Check if the new response is too similar to previous ones."""
        threshold = state.config.similarity_threshold
        
        for turn in state.memory.turns:
            similarity = self._calculate_similarity(new_response, turn.text)
            if similarity > threshold:
                logger.log_validation_error("REPETITION_CHECK", 
                                          f"Similarity {similarity:.2f} > threshold {threshold}", state)
                return True
        
        return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts."""
        # Use simple string similarity for now
        # In a production system, you might use embeddings or more sophisticated methods
        
        cache_key = (text1, text2)
        if cache_key in self.similarity_cache:
            return self.similarity_cache[cache_key]
        
        # Normalize texts
        text1_norm = text1.lower().strip()
        text2_norm = text2.lower().strip()
        
        # Quick string similarity using SequenceMatcher
        similarity = SequenceMatcher(None, text1_norm, text2_norm).ratio()
        
        # Also check for common phrases
        words1 = set(text1_norm.split())
        words2 = set(text2_norm.split())
        
        if words1 and words2:
            word_overlap = len(words1.intersection(words2)) / len(words1.union(words2))
            # Combine both similarities
            similarity = max(similarity, word_overlap)
        
        self.similarity_cache[cache_key] = similarity
        return similarity
    
    def check_topic_coherence(self, state: DebateState, response: str) -> Dict[str, Any]:
        """Check if the response stays on topic."""
        topic_keywords = set(state.topic.lower().split())
        response_keywords = set(response.lower().split())
        
        # Calculate overlap
        overlap = topic_keywords.intersection(response_keywords)
        coherence_score = len(overlap) / len(topic_keywords) if topic_keywords else 0
        
        is_coherent = coherence_score >= state.config.coherence_threshold
        
        return {
            "coherent": is_coherent,
            "score": coherence_score,
            "topic_keywords": list(topic_keywords),
            "matched_keywords": list(overlap)
        }
    
    def export_memory(self, state: DebateState) -> Dict[str, Any]:
        """Export the complete memory structure."""
        return {
            "topic": state.topic,
            "total_turns": len(state.memory.turns),
            "turns": [turn.dict() for turn in state.memory.turns],
            "summary": state.memory.summary
        }