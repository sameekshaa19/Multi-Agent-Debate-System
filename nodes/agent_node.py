import json
from typing import Dict, Any
from pathlib import Path
from datetime import datetime
from state import DebateState
from nodes.logger_node import logger
from nodes.memory_node import MemoryNode


class AgentNode:
    """Generic agent node that can represent either AgentA or AgentB."""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name  # "AgentA" or "AgentB"
        self.memory_node = MemoryNode()
        self.personas = {}
        self._load_personas()
    
    def _load_personas(self):
        """Load persona templates."""
        persona_dir = Path("persona_templates")
        
        for persona_file in persona_dir.glob("*.txt"):
            persona_name = persona_file.stem
            try:
                with open(persona_file, 'r') as f:
                    self.personas[persona_name] = f.read()
            except Exception as e:
                print(f"Warning: Could not load persona {persona_name}: {e}")
    
    def run(self, state: DebateState) -> Dict:
        """Execute the agent's turn."""
        logger.log_event(f"{self.agent_name}_TURN_START", state, {
            "agent": self.agent_name,
            "round": state.current_round
        })
        
        # Validate turn order
        if not self._validate_turn_order(state):
            return {
                "status": "error",
                "error": f"Out of turn: {self.agent_name} attempted to go when it was {state.next_agent}'s turn"
            }
        
        # Get persona
        persona = self._get_persona(state)
        
        # Get context from memory
        context = self.memory_node.get_agent_context(state, self.agent_name)
        
        # Generate response
        response = self._generate_response(state, persona, context)
        
        # Validate response
        validation_result = self._validate_response(state, response)
        if not validation_result["valid"]:
            state._turn_rejected = True
            state._rejection_reason = validation_result["reason"]
            logger.log_validation_error("RESPONSE_REJECTED", validation_result["reason"], state)
            return {
                "status": "rejected",
                "error": validation_result["reason"]
            }
        
        # Update memory
        success = self.memory_node.update_memory(state, self.agent_name, persona, response)
        if not success:
            return {
                "status": "error",
                "error": "Failed to update memory - possible repetition"
            }
        
        # Log the turn
        logger.log_agent_turn(self.agent_name, persona, response, state)
        
        return {
            "status": "success",
            "response": response,
            "agent": self.agent_name,
            "persona": persona,
            "next_node": "RoundsControllerNode"
        }
    
    def _validate_turn_order(self, state: DebateState) -> bool:
        """Check if it's this agent's turn."""
        # For the first turn, AgentA always goes first
        if len(state.memory.turns) == 0:
            return self.agent_name == "AgentA"
        
        # Otherwise, check if it's this agent's turn
        return state.next_agent == self.agent_name
    
    def _get_persona(self, state: DebateState) -> str:
        """Get the persona for this agent."""
        if self.agent_name == "AgentA":
            return state.agent_a_persona
        else:
            return state.agent_b_persona
    
    def _generate_response(self, state: DebateState, persona: str, context: str) -> str:
        """Generate a response based on persona and context."""
        
        # For this demo, we'll use hardcoded responses based on topic and persona
        # In a real implementation, this would call an LLM
        
        topic = state.topic
        responses = self._get_demo_responses(topic, persona, context, state.current_round)
        
        # Select response based on agent's turn number (not round number)
        # AgentA goes on rounds 1, 3, 5, 7
        # AgentB goes on rounds 2, 4, 6, 8
        if self.agent_name == "AgentA":
            turn_number = (state.current_round + 1) // 2  # 1, 2, 3, 4
        else:
            turn_number = state.current_round // 2  # 1, 2, 3, 4
        
        response_index = min(turn_number - 1, len(responses) - 1)
        return responses[response_index]
    
    def _get_demo_responses(self, topic: str, persona: str, context: str, round_num: int) -> list:
        """Get demo responses for different topics and personas."""
        
        topic_lower = topic.lower()
        
        # Check for specific topics
        if "ai" in topic_lower or "artificial intelligence" in topic_lower:
            return self._ai_responses(persona, round_num)
        elif "climate" in topic_lower or "environment" in topic_lower:
            return self._climate_responses(persona, round_num)
        elif "medicine" in topic_lower or "health" in topic_lower:
            return self._medicine_responses(persona, round_num)
        elif "social media" in topic_lower or "social networking" in topic_lower:
            return self._social_media_responses(persona, round_num)
        else:
            return self._topic_specific_generic_responses(topic, persona, round_num)
    
    def _ai_responses(self, persona: str, round_num: int) -> list:
        """Responses for AI regulation topic."""
        if persona == "scientist":
            return [
                "AI must be regulated due to high-risk applications in healthcare, transportation, and finance. Machine learning models can perpetuate bias and cause real harm without oversight.",
                "We have precedent for this: medical devices, aircraft systems, and pharmaceuticals all face strict regulation. AI systems that impact human lives deserve the same scrutiny.",
                "From an empirical standpoint, studies show that unregulated AI systems exhibit biased behavior. Facial recognition has higher error rates for minorities, and algorithmic hiring perpetuates discrimination.",
                "The scientific method demands we test, validate, and peer-review AI systems before deployment. Regulation ensures this happens systematically."
            ]
        else:  # philosopher
            return [
                "Regulation could stifle philosophical progress and the open inquiry that drives innovation. We must consider the ethical implications of limiting knowledge creation.",
                "From a deontological perspective, regulation might violate the moral duty to pursue truth and understanding. Knowledge should be free, not constrained by bureaucratic oversight.",
                "History shows that overregulation often delays societal evolution. The precautionary principle can become the paralysis principle, preventing beneficial progress.",
                "We must balance risks with the fundamental human right to think, create, and innovate. Ethical AI development comes from wisdom and virtue, not just rules."
            ]
    
    def _climate_responses(self, persona: str, round_num: int) -> list:
        """Responses for climate change topic."""
        if persona == "scientist":
            return [
                "Climate change is supported by overwhelming scientific evidence. Temperature records, ice core data, and satellite measurements all confirm human-caused global warming.",
                "The physics is clear: increased CO2 concentrations trap heat in the atmosphere. This has been understood since the 1800s and is validated by current observations.",
                "Peer-reviewed studies show clear correlations between human activity and climate patterns. The scientific consensus exceeds 97% on this issue.",
                "Without immediate action based on scientific evidence, we face catastrophic consequences including sea level rise, extreme weather, and ecosystem collapse."
            ]
        else:  # philosopher
            return [
                "Climate change raises profound questions about intergenerational justice. What moral obligations do we have to future generations who cannot consent to our actions?",
                "The tragedy of the commons illustrates how individual rational behavior can lead to collective irrationality. We need ethical frameworks beyond mere technical solutions.",
                "Developed nations have benefited most from industrialization while developing nations suffer most consequences. This raises issues of global justice and reparations.",
                "We must consider what kind of relationship humans should have with nature. Are we stewards, masters, or merely participants in the web of life?"
            ]
    
    def _medicine_responses(self, persona: str, round_num: int) -> list:
        """Responses for medicine regulation topic."""
        if persona == "scientist":
            return [
                "Medical treatments must undergo rigorous clinical trials with placebo controls and peer review. This evidence-based approach has saved countless lives.",
                "The FDA and similar regulatory bodies ensure that treatments are safe and effective through systematic testing. Without this, we risk harmful or ineffective treatments.",
                "Randomized controlled trials are the gold standard for medical evidence. They eliminate bias and provide objective data on treatment efficacy and safety.",
                "Regulation also ensures consistency in manufacturing, proper dosing, and accurate labeling. These details matter enormously in medicine."
            ]
        else:  # philosopher
            return [
                "Medical regulation must balance safety with access. Overly strict regulation can deny beneficial treatments to suffering patients, raising questions about paternalism.",
                "Who decides what risks are acceptable? Individual autonomy suggests patients should have some say in their own treatment choices, even with experimental options.",
                "The placebo effect demonstrates the complex relationship between mind and body. Regulatory frameworks must account for psychological and social dimensions of healing.",
                "Medical decisions involve values and quality of life judgments that science alone cannot answer. We need philosophical reflection on what constitutes a life worth living."
            ]
    
    def _social_media_responses(self, persona: str, round_num: int) -> list:
        """Responses for social media ban topic."""
        if persona == "scientist":
            return [
                "Research shows social media platforms are designed to maximize engagement through addictive algorithms, leading to increased rates of depression, anxiety, and sleep disorders among adolescents.",
                "Studies demonstrate that social media contributes to the rapid spread of misinformation and conspiracy theories, with measurable impacts on public health outcomes and democratic processes.",
                "Data analysis reveals that social media algorithms create echo chambers and filter bubbles, reinforcing polarization and reducing exposure to diverse viewpoints.",
                "The neurological effects of constant social media stimulation show reduced attention spans and impaired face-to-face social skills, particularly in developing brains."
            ]
        else:  # philosopher
            return [
                "Banning social media raises fundamental questions about individual liberty versus collective harm. At what point does society's right to protect citizens override personal freedom of choice?",
                "Social media platforms have become the modern public square. Banning them could be seen as limiting free speech and the ability to organize for social and political change.",
                "We must consider whether social media is a tool or an environment. If it's shaping our very perception of reality and social relationships, perhaps regulation rather than outright bans is more appropriate.",
                "The question forces us to examine what constitutes meaningful human connection. Are social media interactions authentic relationships, or merely simulations that undermine genuine community bonds?"
            ]
    
    def _topic_specific_generic_responses(self, topic: str, persona: str, round_num: int) -> list:
        """More specific responses for any topic."""
        if persona == "scientist":
            return [
                f"From a scientific perspective, we must examine the empirical evidence regarding {topic}. Peer-reviewed studies and data analysis should inform our policy decisions.",
                f"The scientific method provides a framework for evaluating {topic} through controlled experiments and systematic observation of outcomes.",
                f"We should rely on statistical evidence and measurable impacts when assessing {topic}, rather than anecdotal accounts or emotional reasoning.",
                f"Longitudinal studies on {topic} would help us understand causal relationships and unintended consequences of potential interventions."
            ]
        else:  # philosopher
            return [
                f"The debate about {topic} raises fundamental ethical questions about individual rights, social responsibility, and the kind of society we want to create.",
                f"When considering {topic}, we must examine our underlying assumptions about human nature, freedom, and the role of government in personal choices.",
                f"The issue of {topic} forces us to balance competing values: liberty versus security, individual versus collective good, progress versus tradition.",
                f"Ultimately, our position on {topic} reflects our deeper philosophical commitments about what constitutes a good life and a just society."
            ]
    
    def _validate_response(self, state: DebateState, response: str) -> Dict[str, Any]:
        """Validate the generated response."""
        if not response or response.strip() == "":
            return {"valid": False, "reason": "Empty response generated"}
        
        if len(response) < 20:
            return {"valid": False, "reason": "Response too short"}
        
        if len(response) > 1000:
            return {"valid": False, "reason": "Response too long"}
        
        # For demo purposes, skip coherence checking or use very lenient threshold
        # In production, you might want more sophisticated topic modeling
        return {"valid": True, "reason": ""}