#!/usr/bin/env python3
"""
Multi-Agent Debate System - Simplified Implementation
A structured debate between two AI agents with different personas.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from state import DebateState, DebateStatus, DebateMemory, TurnRecord
from config import DebateConfig, DEFAULT_CONFIG
from nodes.user_input_node import UserInputNode
from nodes.rounds_controller_node import RoundsControllerNode
from nodes.agent_node import AgentNode
from nodes.judge_node import JudgeNode
from nodes.logger_node import logger


class DebateSystem:
    """Main debate system that orchestrates the entire debate."""
    
    def __init__(self, config: Optional[DebateConfig] = None):
        self.config = config or DEFAULT_CONFIG
        self.console = Console()
        
        # Initialize components
        self.user_input_node = UserInputNode()
        self.rounds_controller = RoundsControllerNode()
        self.agent_a_node = AgentNode("AgentA")
        self.agent_b_node = AgentNode("AgentB")
        self.judge_node = JudgeNode()
        
        # State
        self.state = DebateState(config=self.config)
    
    def run(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """Run the complete debate."""
        
        try:
            # Step 1: Get topic from user or use provided topic
            if topic:
                self.state.topic = topic
                self.console.print(f"[green]Topic: {topic}[/green]")
            else:
                self.console.print("[bold blue]Multi-Agent Debate System[/bold blue]")
                self.console.print("=" * 50)
                self.console.print()
                from rich.prompt import Prompt
                topic = Prompt.ask(
                    "[green]Enter topic for debate[/green]",
                    default="Should AI be regulated like medicine?"
                )
                self.state.topic = topic
            
            self.console.print(f"[green]Starting debate between {self.config.agent_a_persona} and {self.config.agent_b_persona}...[/green]")
            self.console.print()
            
            # Step 2: Run debate rounds
            for round_num in range(1, self.config.total_rounds + 1):
                # Determine which agent's turn
                if round_num % 2 == 1:
                    # Odd rounds: AgentA
                    agent = "AgentA"
                    agent_node = self.agent_a_node
                    self.state.next_agent = "AgentA"
                else:
                    # Even rounds: AgentB
                    agent = "AgentB"
                    agent_node = self.agent_b_node
                    self.state.next_agent = "AgentB"
                
                self.state.current_round = round_num
                
                # Run agent turn
                result = agent_node.run(self.state)
                
                if result["status"] == "success":
                    self._display_turn(result["agent"], result["persona"], result["response"], round_num)
                    self.state.rounds_completed += 1
                else:
                    self.console.print(f"[red]Error in {agent} turn: {result.get('error', 'Unknown error')}[/red]")
            
            # Step 3: Judge the debate
            judgment = self.judge_node.run(self.state)
            self._display_judgment(judgment)
            
            # Export results
            return self._export_results()
            
        except KeyboardInterrupt:
            self.console.print("\n[red]Debate interrupted by user.[/red]")
            sys.exit(1)
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
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
    
    def _export_results(self) -> Dict[str, Any]:
        """Export the final results."""
        
        results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "topic": self.state.topic,
                "agent_a_persona": self.state.agent_a_persona,
                "agent_b_persona": self.state.agent_b_persona,
                "total_rounds": self.state.rounds_completed,
                "status": self.state.status.value
            },
            "results": {
                "winner": self.state.winner,
                "judge_summary": self.state.judge_summary,
                "judge_reasoning": self.state.judge_reasoning
            },
            "debate_transcript": [
                {
                    "round": turn.round,
                    "agent": turn.agent,
                    "persona": turn.persona,
                    "text": turn.text,
                    "timestamp": turn.timestamp
                }
                for turn in self.state.memory.turns
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


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Multi-Agent Debate System')
    parser.add_argument('topic', nargs='?', help='Debate topic (optional)')
    parser.add_argument('--agent-a', default='scientist', help='Persona for AgentA')
    parser.add_argument('--agent-b', default='philosopher', help='Persona for AgentB')
    parser.add_argument('--rounds', type=int, default=8, help='Total number of rounds')
    parser.add_argument('--seed', type=int, help='Random seed for reproducibility')
    parser.add_argument('--log-path', default='logs', help='Path to log directory')
    
    args = parser.parse_args()
    
    # Create custom config
    config = DebateConfig(
        total_rounds=args.rounds,
        seed=args.seed,
        log_path=Path(args.log_path),
        agent_a_persona=args.agent_a,
        agent_b_persona=args.agent_b
    )
    
    # Create and run debate
    debate = DebateSystem(config)
    results = debate.run(args.topic)
    
    return results


if __name__ == "__main__":
    main()