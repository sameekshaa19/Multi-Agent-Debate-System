#!/usr/bin/env python3
"""
Demo script for the Multi-Agent Debate System
Runs a quick demonstration of the debate system.
"""

from debate_system import DebateSystem
from config import DebateConfig


def run_demo():
    """Run a demonstration debate."""
    print("🎭 Multi-Agent Debate System Demo")
    print("=" * 50)
    
    # Create config
    config = DebateConfig(
        total_rounds=8,
        agent_a_persona="scientist",
        agent_b_persona="philosopher"
    )
    
    # Create and run debate
    debate = DebateSystem(config)
    
    # Run with a sample topic
    topic = "Should AI be regulated like medicine?"
    print(f"\nRunning debate on: {topic}")
    print("=" * 50)
    
    results = debate.run(topic)
    
    print("\n" + "=" * 50)
    print("Demo completed successfully!")
    print(f"Winner: {results['results']['winner']}")
    print(f"Log file: {results['log_file']}")
    print("=" * 50)


if __name__ == "__main__":
    run_demo()