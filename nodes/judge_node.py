from typing import Dict, List, Any
from datetime import datetime
from state import DebateState, DebateStatus
from nodes.logger_node import logger


class JudgeNode:
    """Reviews the debate and declares a winner with justification."""
    
    def run(self, state: DebateState) -> Dict:
        """Execute the final judgment of the debate."""
        logger.log_event("JUDGE_NODE_START", state, {
            "total_turns": len(state.memory.turns),
            "total_rounds": state.rounds_completed
        })
        
        # Validate debate completeness
        if state.rounds_completed < state.config.total_rounds:
            state.errors.append(f"Debate incomplete: only {state.rounds_completed}/{state.config.total_rounds} rounds")
        
        # Analyze debate
        analysis = self._analyze_debate(state)
        
        # Determine winner
        winner, reasoning = self._determine_winner(state, analysis)
        
        # Generate summary
        summary = self._generate_summary(state, analysis)
        
        # Update state
        state.winner = winner
        state.judge_summary = summary
        state.judge_reasoning = reasoning
        state.status = DebateStatus.COMPLETED
        
        # Log judgment
        logger.log_judgment(winner, summary, reasoning, state)
        
        return {
            "status": "completed",
            "winner": winner,
            "summary": summary,
            "reasoning": reasoning,
            "analysis": analysis
        }
    
    def _analyze_debate(self, state: DebateState) -> Dict[str, Any]:
        """Analyze the debate arguments and quality."""
        
        agent_a_turns = [t for t in state.memory.turns if t.agent == "AgentA"]
        agent_b_turns = [t for t in state.memory.turns if t.agent == "AgentB"]
        
        analysis = {
            "agent_a": {
                "turns_count": len(agent_a_turns),
                "avg_response_length": sum(len(t.text) for t in agent_a_turns) / len(agent_a_turns) if agent_a_turns else 0,
                "argument_quality": self._assess_argument_quality(agent_a_turns, state.agent_a_persona),
                "coherence_score": self._assess_coherence(agent_a_turns),
                "relevance_score": self._assess_relevance(agent_a_turns, state.topic)
            },
            "agent_b": {
                "turns_count": len(agent_b_turns),
                "avg_response_length": sum(len(t.text) for t in agent_b_turns) / len(agent_b_turns) if agent_b_turns else 0,
                "argument_quality": self._assess_argument_quality(agent_b_turns, state.agent_b_persona),
                "coherence_score": self._assess_coherence(agent_b_turns),
                "relevance_score": self._assess_relevance(agent_b_turns, state.topic)
            },
            "debate_flow": {
                "total_rounds": state.rounds_completed,
                "alternating_turns": self._check_turn_alternation(state.memory.turns),
                "topic_adherence": self._assess_topic_adherence(state.memory.turns, state.topic)
            }
        }
        
        return analysis
    
    def _assess_argument_quality(self, turns: List[Any], persona: str) -> float:
        """Assess the quality of arguments based on persona."""
        if not turns:
            return 0.0
        
        quality_scores = []
        for turn in turns:
            text = turn.text.lower()
            score = 0.5  # Base score
            
            if persona == "scientist":
                # Look for scientific indicators
                scientific_terms = ["evidence", "data", "study", "research", "empirical", "analysis", "statistics"]
                for term in scientific_terms:
                    if term in text:
                        score += 0.1
                
                # Look for logical structure
                if any(word in text for word in ["therefore", "conclusion", "because", "since"]):
                    score += 0.1
                
                # Check for specific examples
                if any(word in text for word in ["example", "instance", "case study"]):
                    score += 0.05
            
            elif persona == "philosopher":
                # Look for philosophical indicators
                philo_terms = ["ethical", "moral", "justice", "principle", "virtue", "duty", "rights"]
                for term in philo_terms:
                    if term in text:
                        score += 0.1
                
                # Look for logical reasoning
                if any(word in text for word in ["argument", "premise", "conclusion", "logic", "fallacy"]):
                    score += 0.1
                
                # Check for consideration of multiple perspectives
                if any(phrase in text for phrase in ["on the other hand", "however", "consider", "perspective"]):
                    score += 0.05
            
            # Penalty for very short responses
            if len(text) < 50:
                score -= 0.2
            
            quality_scores.append(min(score, 1.0))
        
        return sum(quality_scores) / len(quality_scores)
    
    def _assess_coherence(self, turns: List[Any]) -> float:
        """Assess logical coherence between turns."""
        if len(turns) < 2:
            return 1.0
        
        coherence_scores = []
        for i in range(1, len(turns)):
            prev_text = turns[i-1].text.lower()
            curr_text = turns[i].text.lower()
            
            # Check for continuity in themes
            prev_words = set(prev_text.split())
            curr_words = set(curr_text.split())
            
            # Calculate overlap (excluding common words)
            common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
            prev_keywords = prev_words - common_words
            curr_keywords = curr_words - common_words
            
            if prev_keywords:
                overlap = len(prev_keywords.intersection(curr_keywords)) / len(prev_keywords)
                coherence_scores.append(overlap)
        
        return sum(coherence_scores) / len(coherence_scores) if coherence_scores else 1.0
    
    def _assess_relevance(self, turns: List[Any], topic: str) -> float:
        """Assess relevance to the debate topic."""
        if not turns:
            return 0.0
        
        topic_keywords = set(topic.lower().split())
        relevance_scores = []
        
        for turn in turns:
            text = turn.text.lower()
            text_words = set(text.split())
            
            if topic_keywords:
                overlap = len(topic_keywords.intersection(text_words)) / len(topic_keywords)
                relevance_scores.append(overlap)
            else:
                relevance_scores.append(0.5)
        
        return sum(relevance_scores) / len(relevance_scores)
    
    def _check_turn_alternation(self, turns: List[Any]) -> bool:
        """Check if turns properly alternated between agents."""
        for i in range(1, len(turns)):
            if turns[i].agent == turns[i-1].agent:
                return False
        return True
    
    def _assess_topic_adherence(self, turns: List[Any], topic: str) -> float:
        """Assess overall adherence to the topic."""
        return self._assess_relevance(turns, topic)
    
    def _determine_winner(self, state: DebateState, analysis: Dict[str, Any]) -> tuple:
        """Determine the winner based on analysis."""
        
        # Calculate overall scores
        agent_a_score = (
            analysis["agent_a"]["argument_quality"] * 0.4 +
            analysis["agent_a"]["coherence_score"] * 0.3 +
            analysis["agent_a"]["relevance_score"] * 0.3
        )
        
        agent_b_score = (
            analysis["agent_b"]["argument_quality"] * 0.4 +
            analysis["agent_b"]["coherence_score"] * 0.3 +
            analysis["agent_b"]["relevance_score"] * 0.3
        )
        
        # Determine winner
        if agent_a_score > agent_b_score:
            winner = "AgentA"
            reasoning = f"AgentA ({state.agent_a_persona}) demonstrated stronger arguments with better evidence and logical structure. Score: {agent_a_score:.2f} vs {agent_b_score:.2f}"
        elif agent_b_score > agent_a_score:
            winner = "AgentB"
            reasoning = f"AgentB ({state.agent_b_persona}) presented more coherent and relevant arguments. Score: {agent_b_score:.2f} vs {agent_a_score:.2f}"
        else:
            # Tie breaker based on persona-specific strengths
            if state.agent_a_persona == "scientist":
                winner = "AgentA"
                reasoning = f"Debate was tied, but AgentA ({state.agent_a_persona}) wins for evidence-based reasoning."
            else:
                winner = "AgentB"
                reasoning = f"Debate was tied, but AgentB ({state.agent_b_persona}) wins for ethical and logical analysis."
        
        return winner, reasoning
    
    def _generate_summary(self, state: DebateState, analysis: Dict[str, Any]) -> str:
        """Generate a comprehensive summary of the debate."""
        
        summary_parts = [
            f"Debate Topic: {state.topic}",
            f"Participants: AgentA ({state.agent_a_persona}) vs AgentB ({state.agent_b_persona})",
            f"Total Rounds: {state.rounds_completed}",
            f"Total Turns: {len(state.memory.turns)}",
            "",
            "Key Arguments:",
            ""
        ]
        
        # Add key arguments from each agent
        for turn in state.memory.turns:
            summary_parts.append(f"[{turn.persona} - Round {turn.round}] {turn.text[:150]}{'...' if len(turn.text) > 150 else ''}")
        
        summary_parts.extend([
            "",
            "Analysis:",
            f"- AgentA Argument Quality: {analysis['agent_a']['argument_quality']:.2f}",
            f"- AgentB Argument Quality: {analysis['agent_b']['argument_quality']:.2f}",
            f"- Debate Coherence: {analysis['debate_flow']['topic_adherence']:.2f}",
            f"- Proper Turn Alternation: {analysis['debate_flow']['alternating_turns']}"
        ])
        
        return "\n".join(summary_parts)