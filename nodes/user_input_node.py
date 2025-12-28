import re
from typing import Dict
from rich.console import Console
from rich.prompt import Prompt
from state import DebateState, DebateStatus
from nodes.logger_node import logger


class UserInputNode:
    """Handles user input for the debate topic."""
    
    def __init__(self):
        self.console = Console()
    
    def run(self, state: DebateState) -> Dict:
        """Prompt user for debate topic and validate input."""
        logger.log_event("USER_INPUT_START", state, {"message": "Starting user input collection"})
        
        # Clear console and show header
        self.console.clear()
        self.console.print("[bold blue]Multi-Agent Debate System[/bold blue]")
        self.console.print("=" * 50)
        self.console.print()
        
        # Get topic from user
        topic = Prompt.ask(
            "[green]Enter topic for debate[/green]",
            default="Should AI be regulated like medicine?"
        )
        
        # Validate topic
        validation_result = self._validate_topic(topic)
        
        if not validation_result["valid"]:
            logger.log_validation_error("TOPIC_VALIDATION", validation_result["reason"], state)
            self.console.print(f"[red]Error: {validation_result['reason']}[/red]")
            return {"status": "retry", "error": validation_result["reason"]}
        
        # Clean and set topic
        cleaned_topic = self._sanitize_topic(topic)
        state.topic = cleaned_topic
        state.status = DebateStatus.INITIALIZED
        
        logger.log_event("TOPIC_ACCEPTED", state, {
            "original_topic": topic,
            "cleaned_topic": cleaned_topic,
            "length": len(cleaned_topic)
        })
        
        self.console.print(f"[green]✓ Topic accepted:[/green] {cleaned_topic}")
        self.console.print()
        
        return {
            "status": "success",
            "topic": cleaned_topic,
            "next_node": "RoundsControllerNode"
        }
    
    def _validate_topic(self, topic: str) -> Dict[str, str]:
        """Validate the debate topic."""
        if not topic or topic.strip() == "":
            return {"valid": False, "reason": "Topic cannot be empty"}
        
        if len(topic) < 10:
            return {"valid": False, "reason": "Topic must be at least 10 characters long"}
        
        if len(topic) > 200:
            return {"valid": False, "reason": "Topic must be less than 200 characters"}
        
        # Check for inappropriate content
        inappropriate_keywords = ["spam", "testtest", "xxx", "spamtest"]
        topic_lower = topic.lower()
        for keyword in inappropriate_keywords:
            if keyword in topic_lower:
                return {"valid": False, "reason": f"Topic contains inappropriate content: {keyword}"}
        
        return {"valid": True, "reason": ""}
    
    def _sanitize_topic(self, topic: str) -> str:
        """Clean and sanitize the topic."""
        # Remove extra whitespace
        topic = re.sub(r'\s+', ' ', topic.strip())
        
        # Remove special characters but keep basic punctuation
        topic = re.sub(r'[^\w\s\?\!\.,\-\']', '', topic)
        
        # Capitalize first letter
        if topic:
            topic = topic[0].upper() + topic[1:]
        
        return topic