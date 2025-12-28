#!/usr/bin/env python3
"""
Generate a visual DAG diagram of the debate system.
"""

from pathlib import Path
from graphviz import Digraph


def generate_dag(output_path: str = "dag.png"):
    """Generate the DAG visualization."""
    
    # Create a new directed graph
    dot = Digraph(
        comment='Multi-Agent Debate DAG',
        graph_attr={
            'rankdir': 'TB',
            'bgcolor': 'white',
            'margin': '0.5',
            'fontname': 'Arial'
        },
        node_attr={
            'shape': 'box',
            'style': 'rounded,filled',
            'fontname': 'Arial',
            'fontsize': '12'
        },
        edge_attr={
            'fontname': 'Arial',
            'fontsize': '10'
        }
    )
    
    # Define node colors
    colors = {
        'input': '#E8F4F8',      # Light blue
        'control': '#FFF4E6',     # Light orange
        'agent_a': '#E8F5E9',     # Light green
        'agent_b': '#F3E5F5',     # Light purple
        'judge': '#FFEBEE',       # Light red
        'end': '#ECEFF1'          # Light gray
    }
    
    # Add nodes
    dot.node('UserInputNode', 'UserInputNode\n(Topic Input)', 
             fillcolor=colors['input'], color='#0277BD')
    
    dot.node('RoundsControllerNode', 'RoundsControllerNode\n(Turn Management)', 
             fillcolor=colors['control'], color='#EF6C00')
    
    dot.node('AgentANode', 'AgentANode\n(Scientist)', 
             fillcolor=colors['agent_a'], color='#2E7D32')
    
    dot.node('AgentBNode', 'AgentBNode\n(Philosopher)', 
             fillcolor=colors['agent_b'], color='#7B1FA2')
    
    dot.node('JudgeNode', 'JudgeNode\n(Final Judgment)', 
             fillcolor=colors['judge'], color='#C62828')
    
    dot.node('END', 'END', 
             fillcolor=colors['end'], color='#455A64', shape='ellipse')
    
    # Add edges
    dot.edge('UserInputNode', 'RoundsControllerNode', 'topic validated')
    
    # Controller to agents (bidirectional flow)
    dot.edge('RoundsControllerNode', 'AgentANode', 'turn: AgentA')
    dot.edge('AgentANode', 'RoundsControllerNode', 'response complete')
    
    dot.edge('RoundsControllerNode', 'AgentBNode', 'turn: AgentB')
    dot.edge('AgentBNode', 'RoundsControllerNode', 'response complete')
    
    # Controller to judge when rounds complete
    dot.edge('RoundsControllerNode', 'JudgeNode', 'all rounds complete\n(8 rounds)')
    
    # Judge to end
    dot.edge('JudgeNode', 'END', 'winner declared')
    
    # Add a subgraph for the debate loop
    with dot.subgraph(name='cluster_debate_loop') as c:
        c.attr(label='Debate Loop (8 Rounds)', style='dashed', color='#666666')
        c.node('RoundsControllerNode')
        c.node('AgentANode')
        c.node('AgentBNode')
    
    # Save the graph
    output_file = Path(output_path)
    dot.format = 'png'
    dot.render(str(output_file.with_suffix('')), cleanup=True)
    
    print(f"DAG diagram saved to: {output_path}")
    
    # Also generate a textual representation
    print("\nDAG Structure:")
    print("=" * 50)
    print("Nodes:")
    print("  1. UserInputNode - Accepts and validates debate topic")
    print("  2. RoundsControllerNode - Manages turn order and round counting")
    print("  3. AgentANode - Scientist persona agent")
    print("  4. AgentBNode - Philosopher persona agent")
    print("  5. JudgeNode - Evaluates debate and declares winner")
    print("  6. END - Terminal node")
    print()
    print("Flow:")
    print("  UserInputNode → RoundsControllerNode")
    print("  RoundsControllerNode ↔ AgentANode (alternating turns)")
    print("  RoundsControllerNode ↔ AgentBNode (alternating turns)")
    print("  RoundsControllerNode → JudgeNode (after 8 rounds)")
    print("  JudgeNode → END")
    
    return str(output_path)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate DAG visualization')
    parser.add_argument('--output', '-o', default='dag.png', 
                       help='Output file path (default: dag.png)')
    
    args = parser.parse_args()
    generate_dag(args.output)