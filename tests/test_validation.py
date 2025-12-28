#!/usr/bin/env python3
"""
Unit tests for validation logic in the debate system.
"""

import unittest
import tempfile
from pathlib import Path
from state import DebateState, DebateMemory, TurnRecord
from config import DebateConfig
from nodes.memory_node import MemoryNode
from nodes.rounds_controller_node import RoundsControllerNode


class TestTopicValidation(unittest.TestCase):
    """Test topic validation logic."""
    
    def setUp(self):
        self.config = DebateConfig()
        self.state = DebateState(config=self.config)
    
    def test_valid_topic(self):
        """Test valid topic acceptance."""
        from nodes.user_input_node import UserInputNode
        node = UserInputNode()
        
        result = node._validate_topic("Should AI be regulated like medicine?")
        self.assertTrue(result["valid"])
    
    def test_empty_topic(self):
        """Test rejection of empty topic."""
        from nodes.user_input_node import UserInputNode
        node = UserInputNode()
        
        result = node._validate_topic("")
        self.assertFalse(result["valid"])
        self.assertIn("empty", result["reason"])
    
    def test_short_topic(self):
        """Test rejection of too short topic."""
        from nodes.user_input_node import UserInputNode
        node = UserInputNode()
        
        result = node._validate_topic("AI?")
        self.assertFalse(result["valid"])
        self.assertIn("10 characters", result["reason"])
    
    def test_inappropriate_content(self):
        """Test rejection of inappropriate content."""
        from nodes.user_input_node import UserInputNode
        node = UserInputNode()
        
        result = node._validate_topic("This is spam content xxx")
        self.assertFalse(result["valid"])
        self.assertIn("inappropriate", result["reason"])


class TurnOrderValidation(unittest.TestCase):
    """Test turn order enforcement."""
    
    def setUp(self):
        self.config = DebateConfig()
        self.controller = RoundsControllerNode()
    
    def test_initial_turn_order(self):
        """Test initial turn is AgentA."""
        state = DebateState(config=self.config)
        state.current_round = 1
        state.next_agent = "AgentA"
        
        self.assertTrue(self.controller.validate_turn_order(state, "AgentA"))
        self.assertFalse(self.controller.validate_turn_order(state, "AgentB"))
    
    def test_alternating_turns(self):
        """Test turn alternation."""
        state = DebateState(config=self.config)
        
        # Round 1: AgentA
        state.next_agent = "AgentA"
        self.assertTrue(self.controller.validate_turn_order(state, "AgentA"))
        
        # After AgentA, should be AgentB
        state.next_agent = "AgentB"
        self.assertTrue(self.controller.validate_turn_order(state, "AgentB"))
        self.assertFalse(self.controller.validate_turn_order(state, "AgentA"))
    
    def test_round_limit(self):
        """Test round limit enforcement."""
        state = DebateState(config=self.config)
        state.rounds_completed = 8
        
        self.assertTrue(self.controller.check_round_limit(state))
        
        state.rounds_completed = 7
        self.assertFalse(self.controller.check_round_limit(state))


class TestRepetitionDetection(unittest.TestCase):
    """Test repetition detection logic."""
    
    def setUp(self):
        self.config = DebateConfig(similarity_threshold=0.8)
        self.memory_node = MemoryNode()
    
    def test_no_repetition(self):
        """Test that different responses are accepted."""
        state = DebateState(config=self.config)
        state.memory.turns = [
            TurnRecord(
                round=1, agent="AgentA", persona="scientist",
                text="AI should be regulated for safety reasons.",
                timestamp="2024-01-01T00:00:00"
            )
        ]
        
        new_response = "Regulation could stifle innovation and progress."
        result = self.memory_node._check_repetition(state, new_response)
        self.assertFalse(result)
    
    def test_exact_repetition(self):
        """Test that exact repetition is detected."""
        state = DebateState(config=self.config)
        original_text = "AI should be regulated for safety reasons."
        
        state.memory.turns = [
            TurnRecord(
                round=1, agent="AgentA", persona="scientist",
                text=original_text,
                timestamp="2024-01-01T00:00:00"
            )
        ]
        
        result = self.memory_node._check_repetition(state, original_text)
        self.assertTrue(result)
    
    def test_similar_repetition(self):
        """Test that very similar text is detected."""
        state = DebateState(config=self.config)
        state.memory.turns = [
            TurnRecord(
                round=1, agent="AgentA", persona="scientist",
                text="AI systems must be regulated due to safety concerns and potential risks.",
                timestamp="2024-01-01T00:00:00"
            )
        ]
        
        # Very similar response
        new_response = "AI systems must be regulated because of safety concerns and potential risks."
        result = self.memory_node._check_repetition(state, new_response)
        self.assertTrue(result)
    
    def test_similarity_calculation(self):
        """Test similarity calculation method."""
        text1 = "The quick brown fox jumps over the lazy dog."
        text2 = "The quick brown fox jumps over the lazy dog."
        
        similarity = self.memory_node._calculate_similarity(text1, text2)
        self.assertEqual(similarity, 1.0)
        
        text3 = "A completely different sentence with no overlap."
        similarity = self.memory_node._calculate_similarity(text1, text3)
        self.assertLess(similarity, 0.5)


class TestTopicCoherence(unittest.TestCase):
    """Test topic coherence checking."""
    
    def setUp(self):
        self.config = DebateConfig(coherence_threshold=0.1)  # Lower threshold for testing
        self.memory_node = MemoryNode()
    
    def test_coherent_response(self):
        """Test that on-topic responses are coherent."""
        state = DebateState(config=self.config)
        state.topic = "Should AI be regulated like medicine?"
        
        response = "AI regulation is important for ensuring safety in medical applications."
        result = self.memory_node.check_topic_coherence(state, response)
        
        self.assertTrue(result["coherent"])
        self.assertGreater(result["score"], 0.3)
    
    def test_incoherent_response(self):
        """Test that off-topic responses are detected."""
        state = DebateState(config=self.config)
        state.topic = "Should AI be regulated like medicine?"
        
        response = "I really enjoy eating pizza and watching movies on weekends."
        result = self.memory_node.check_topic_coherence(state, response)
        
        self.assertFalse(result["coherent"])
        self.assertLess(result["score"], 0.3)


class TestMemoryManagement(unittest.TestCase):
    """Test memory management functionality."""
    
    def setUp(self):
        self.config = DebateConfig()
        self.memory_node = MemoryNode()
    
    def test_memory_update(self):
        """Test that memory is properly updated."""
        state = DebateState(config=self.config)
        state.topic = "Test Topic"
        state.current_round = 1
        
        success = self.memory_node.update_memory(
            state, "AgentA", "scientist", "Test response"
        )
        
        self.assertTrue(success)
        self.assertEqual(len(state.memory.turns), 1)
        self.assertEqual(state.memory.turns[0].agent, "AgentA")
        self.assertEqual(state.rounds_completed, 1)
    
    def test_agent_context(self):
        """Test that agent context is properly filtered."""
        state = DebateState(config=self.config)
        
        # Add turns
        state.memory.turns = [
            TurnRecord(round=1, agent="AgentA", persona="scientist", 
                      text="First argument from scientist", timestamp="2024-01-01T00:00:00"),
            TurnRecord(round=1, agent="AgentB", persona="philosopher", 
                      text="First argument from philosopher", timestamp="2024-01-01T00:01:00"),
            TurnRecord(round=2, agent="AgentA", persona="scientist", 
                      text="Second argument from scientist", timestamp="2024-01-01T00:02:00")
        ]
        
        # Get context for AgentA (should only see AgentB's turn)
        context_a = self.memory_node.get_agent_context(state, "AgentA")
        self.assertIn("philosopher", context_a)
        self.assertNotIn("scientist", context_a)
        
        # Get context for AgentB (should only see AgentA's turns)
        context_b = self.memory_node.get_agent_context(state, "AgentB")
        self.assertIn("scientist", context_b)
        self.assertNotIn("philosopher", context_b)


class TestDebateFlow(unittest.TestCase):
    """Test overall debate flow."""
    
    def setUp(self):
        self.config = DebateConfig()
    
    def test_debate_state_transitions(self):
        """Test state transitions through a debate."""
        state = DebateState(config=self.config)
        
        # Initial state
        self.assertEqual(state.status.value, "initialized")
        self.assertEqual(state.current_round, 0)
        self.assertEqual(state.next_agent, "AgentA")
        
        # Simulate a few rounds
        for round_num in range(1, 4):
            # AgentA turn
            state.current_round = round_num
            state.next_agent = "AgentA"
            
            # AgentB turn
            state.next_agent = "AgentB"
            state.rounds_completed += 1
        
        self.assertEqual(state.rounds_completed, 3)
        self.assertEqual(state.next_agent, "AgentB")


if __name__ == '__main__':
    unittest.main()