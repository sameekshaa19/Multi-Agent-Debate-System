#!/usr/bin/env python3
"""
Multi-Agent Debate System using LangGraph
A structured debate between two AI agents with different personas.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import typer

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Local imports
from state import DebateState, DebateStatus
from config import DebateConfig, DEFAULT_CONFIG
from nodes.user_input_node import UserInputNode
from nodes.rounds_controller_node import RoundsControllerNode
from nodes.agent_node import AgentNode
from nodes.judge_node import JudgeNode
from nodes.logger_node import logger


class DebateRunner:
    """Main class for running the debate system."""
    
    def __init__(self, config: Optional[DebateConfig] = None):
        self.config = config or DEFAULT_CONFIG
        self.console = Console()
        self.graph = None
        self.memory_saver = MemorySaver()
        
        # Initialize nodes
        self.user_input_node = UserInputNode()
        self.rounds_controller = RoundsControllerNode()
        self.agent_a_node = AgentNode("AgentA")
        self.agent_b_node = AgentNode("AgentB")
        self.judge_node = JudgeNode()
        
        self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow."""
        
        # Create the state graph
        workflow = StateGraph(DebateState)
        
        # Add nodes
        workflow.add_node("UserInputNode", self._user_input_wrapper)
        workflow.add_node("RoundsControllerNode", self._rounds_controller_wrapper)
        workflow.add_node("AgentANode", self._agent_a_wrapper)
        workflow.add_node("AgentBNode", self._agent_b_wrapper)
        workflow.add_node("JudgeNode", self._judge_wrapper)
        
        # Set entry point
        workflow.set_entry_point("UserInputNode")
        
        # Add edges
        workflow.add_edge("UserInputNode", "RoundsControllerNode")
        workflow.add_edge("RoundsControllerNode", "AgentANode")
        workflow.add_edge("RoundsControllerNode", "AgentBNode")
        workflow.add_edge("AgentANode", "RoundsControllerNode")
        workflow.add_edge("AgentBNode", "RoundsControllerNode")
        workflow.add_edge("RoundsControllerNode", "JudgeNode")
        workflow.add_edge("JudgeNode", END)
        
        # Compile the graph
        self.graph = workflow.compile(checkpointer=self.memory_saver)
    
    def _user_input_wrapper(self, state: DebateState) -> Dict:
        """Wrapper for user input node."""
        result = self.user_input_node.run(state)
        
        if result["status"] == "retry":
            # Stay in user input node
            return {"_next_step": "UserInputNode"}
        
        return {"_next_step": "RoundsControllerNode"}
    
    def _rounds_controller_wrapper(self, state: DebateState) -> Dict:
        """Wrapper for rounds controller node."""
        result = self.rounds_controller.run(state)
        
        if result["status"] == "completed":
            return {"_next_step": "JudgeNode"}
        else:
            next_agent = result.get("agent", "AgentA")
            # Return the agent node name directly
            return {"_next_step": f"{next_agent}Node"}
    
    def _agent_a_wrapper(self, state: DebateState) -> Dict:
        """Wrapper for AgentA node."""
        result = self.agent_a_node.run(state)
        
        if result["status"] == "success":
            # Display the turn
            self._display_turn(result["agent"], result["persona"], result["response"], state.current_round)
            return {"_next_step": "RoundsControllerNode"}
        else:
            self.console.print(f"[red]Error in AgentA turn: {result.get('error', 'Unknown error')}[/red]")
            return {"_next_step": "RoundsControllerNode"}
    
    def _agent_b_wrapper(self, state: DebateState) -> Dict:
        """Wrapper for AgentB node."""
        result = self.agent_b_node.run(state)
        
        if result["status"] == "success":
            # Display the turn
            self._display_turn(result["agent"], result["persona"], result["response"], state.current_round)
            return {"_next_step": "RoundsControllerNode"}
        else:
            self.console.print(f"[red]Error in AgentB turn: {result.get('error', 'Unknown error')}[/red]")
            return {"_next_step": "RoundsControllerNode"}
    
    def _judge_wrapper(self, state: DebateState) -> Dict:
        """Wrapper for judge node."""
        result = self.judge_node.run(state)
        self._display_judgment(result)
        return {"_next_step": END}
    
    def _display_turn(self, agent: str, persona: str, response: str, round_num: int):
        """Display a turn in the debate."""
        agent_color = "blue" if agent == "AgentA" else "green"
        
        self.console.print(Panel(
            response,
            title=f"[Round {round_num}] {agent} ({persona})",
            title_align="left",
            border_style=agent_color
        ))
        self.console.print()
    
    def _display_judgment(self, result: Dict):
        """Display the final judgment."""
        winner = result["winner"]
        summary = result["summary"]
        reasoning = result["reasoning"]
        
        self.console.print(Panel(
            f"[bold]Winner: {winner}[/bold]\n\n{reasoning}",
            title="[red]Final Judgment[/red]",
            border_style="red"
        ))
        self.console.print()
        
        # Display full summary
        self.console.print(Panel(
            Markdown(summary),
            title="Debate Summary",
            border_style="yellow"
        ))
    
    def run(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """Run the debate system."""
        
        # Initialize state
        initial_state = DebateState(
            config=self.config,
            agent_a_persona=self.config.agent_a_persona,
            agent_b_persona=self.config.agent_b_persona
        )
        
        # If topic provided, set it directly
        if topic:
            initial_state.topic = topic
        
        # Run the graph
        config = {"configurable": {"thread_id": "1"}}
        
        try:
            final_state = self.graph.invoke(initial_state, config)
            
            # Export results
            return self._export_results(final_state)
            
        except Exception as e:
            self.console.print(f"[red]Error running debate: {e}[/red]")
            raise
    
    def _export_results(self, final_state: DebateState) -> Dict[str, Any]:
        """Export the final results."""
        
        results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "topic": final_state.topic,
                "agent_a_persona": final_state.agent_a_persona,
                "agent_b_persona": final_state.agent_b_persona,
                "total_rounds": final_state.rounds_completed,
                "status": final_state.status.value
            },
            "results": {
                "winner": final_state.winner,
                "judge_summary": final_state.judge_summary,
                "judge_reasoning": final_state.judge_reasoning
            },
            "debate_transcript": [
                {
                    "round": turn.round,
                    "agent": turn.agent,
                    "persona": turn.persona,
                    "text": turn.text,
                    "timestamp": turn.timestamp
                }
                for turn in final_state.memory.turns
            ],
            "log_file": str(logger.get_log_file())
        }
        
        # Save results to file
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = results_dir / f"debate_results_{timestamp}.json"
        
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        
        self.console.print(f"[green]Results saved to: {results_file}[/green]")
        self.console.print(f"[green]Log file: {logger.get_log_file()}[/green]")
        
        return results


def main(
    topic: Optional[str] = typer.Argument(None, help="Debate topic (optional)"),
    agent_a: str = typer.Option("scientist", help="Persona for AgentA"),
    agent_b: str = typer.Option("philosopher", help="Persona for AgentB"),
    rounds: int = typer.Option(8, help="Total number of rounds"),
    seed: Optional[int] = typer.Option(None, help="Random seed for reproducibility"),
    log_path: str = typer.Option("logs", help="Path to log directory")
):
    """Run the multi-agent debate system."""
    
    # Create custom config if options provided
    config = DebateConfig(
        total_rounds=rounds,
        seed=seed,
        log_path=Path(log_path),
        agent_a_persona=agent_a,
        agent_b_persona=agent_b
    )
    
    # Create and run debate
    debate = DebateRunner(config)
    
    try:
        results = debate.run(topic)
        return results
    except KeyboardInterrupt:
        print("\n[red]Debate interrupted by user.[/red]")
        sys.exit(1)
    except Exception as e:
        print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    typer.run(main)