#!/usr/bin/env python3
"""
Quantum Computing Learning Roadmap
Interactive guide through quantum computing concepts and exercises
"""

import sys
import json
from typing import Dict, List, Tuple

class LearningRoadmap:
    """Interactive quantum computing learning roadmap"""
    
    def __init__(self):
        self.levels = self._initialize_levels()
        self.current_level = 1
        self.completed_topics = set()
    
    def _initialize_levels(self) -> Dict:
        """Initialize learning levels and topics"""
        return {
            1: {
                'name': 'Foundations',
                'duration': '2-3 weeks',
                'topics': [
                    {
                        'name': 'Basic Gates',
                        'subtopics': ['Pauli gates (X, Y, Z)', 'Hadamard (H)', 'Phase gates (S, T)', 'Measurement'],
                        'time': '3-4 hours',
                        'exercises': 5
                    },
                    {
                        'name': 'Multi-Qubit Gates',
                        'subtopics': ['CNOT', 'CZ', 'SWAP', 'Entanglement'],
                        'time': '3-4 hours',
                        'exercises': 5
                    },
                    {
                        'name': 'Measurement & Collapse',
                        'subtopics': ['Measurement basis', 'State collapse', 'Partial measurement'],
                        'time': '2-3 hours',
                        'exercises': 3
                    }
                ]
            },
            2: {
                'name': 'Algorithms',
                'duration': '3-4 weeks',
                'topics': [
                    {
                        'name': 'Deutsch-Jozsa',
                        'subtopics': ['Function classification', 'Oracle design', 'Quantum advantage'],
                        'time': '4-5 hours',
                        'exercises': 4
                    },
                    {
                        'name': 'Grover\'s Algorithm',
                        'subtopics': ['Database search', 'Amplitude amplification', 'Iteration count'],
                        'time': '4-5 hours',
                        'exercises': 4
                    },
                    {
                        'name': 'Quantum Fourier Transform',
                        'subtopics': ['Frequency domain', 'Phase kickback', 'Applications'],
                        'time': '4-5 hours',
                        'exercises': 3
                    },
                    {
                        'name': 'Phase Estimation',
                        'subtopics': ['Eigenvalue estimation', 'Shor\'s algorithm', 'VQE'],
                        'time': '4-5 hours',
                        'exercises': 3
                    }
                ]
            },
            3: {
                'name': 'Advanced Topics',
                'duration': '4-6 weeks',
                'topics': [
                    {
                        'name': 'Error Correction',
                        'subtopics': ['Bit-flip code', 'Phase-flip code', 'Surface code'],
                        'time': '5-6 hours',
                        'exercises': 4
                    },
                    {
                        'name': 'Variational Algorithms',
                        'subtopics': ['VQE', 'QAOA', 'QNN', 'Parameter optimization'],
                        'time': '5-6 hours',
                        'exercises': 4
                    },
                    {
                        'name': 'Quantum Simulation',
                        'subtopics': ['Molecular simulation', 'Hamiltonian simulation', 'Trotter formula'],
                        'time': '5-6 hours',
                        'exercises': 3
                    },
                    {
                        'name': 'Quantum Machine Learning',
                        'subtopics': ['Quantum kernels', 'QNN', 'Autoencoders', 'GANs'],
                        'time': '5-6 hours',
                        'exercises': 4
                    }
                ]
            }
        }
    
    def display_welcome(self):
        """Display welcome message"""
        print("\n" + "="*60)
        print("🚀 QUANTUM COMPUTING LEARNING ROADMAP")
        print("="*60)
        print("\nWelcome! This roadmap will guide you through quantum computing")
        print("from basics to advanced topics.\n")
        print("Levels:")
        print("  1. Foundations (2-3 weeks)")
        print("  2. Algorithms (3-4 weeks)")
        print("  3. Advanced Topics (4-6 weeks)")
        print("\nEstimated total time: 9-13 weeks")
        print("="*60 + "\n")
    
    def display_level(self, level: int):
        """Display level details"""
        if level not in self.levels:
            print(f"❌ Level {level} not found")
            return
        
        level_info = self.levels[level]
        print(f"\n{'='*60}")
        print(f"📚 LEVEL {level}: {level_info['name'].upper()}")
        print(f"{'='*60}")
        print(f"Duration: {level_info['duration']}")
        print(f"Topics: {len(level_info['topics'])}\n")
        
        total_exercises = 0
        total_hours = 0
        
        for i, topic in enumerate(level_info['topics'], 1):
            print(f"{i}. {topic['name']}")
            print(f"   Time: {topic['time']}")
            print(f"   Exercises: {topic['exercises']}")
            print(f"   Subtopics:")
            for subtopic in topic['subtopics']:
                print(f"     • {subtopic}")
            total_exercises += topic['exercises']
            # Parse hours (rough estimate)
            hours = int(topic['time'].split('-')[0])
            total_hours += hours
            print()
        
        print(f"Total Exercises: {total_exercises}")
        print(f"Estimated Hours: {total_hours}+")
        print("="*60 + "\n")
    
    def display_topic_details(self, level: int, topic_idx: int):
        """Display detailed topic information"""
        if level not in self.levels or topic_idx < 1 or topic_idx > len(self.levels[level]['topics']):
            print(f"❌ Invalid level or topic")
            return
        
        topic = self.levels[level]['topics'][topic_idx - 1]
        print(f"\n{'='*60}")
        print(f"📖 {topic['name'].upper()}")
        print(f"{'='*60}")
        print(f"Time: {topic['time']}")
        print(f"Exercises: {topic['exercises']}\n")
        
        print("Subtopics to master:")
        for i, subtopic in enumerate(topic['subtopics'], 1):
            print(f"  {i}. {subtopic}")
        
        print("\nLearning path:")
        print("  1. Read theory and concepts")
        print("  2. Study code examples")
        print("  3. Complete exercises")
        print("  4. Build mini-project")
        print("  5. Review and consolidate")
        
        print("\nResources:")
        print("  • Qiskit Textbook: https://qiskit.org/textbook")
        print("  • Microsoft Quantum Katas: https://github.com/microsoft/QuantumKatas")
        print("  • PennyLane Demos: https://pennylane.ai/qml/demos/")
        print("="*60 + "\n")
    
    def display_learning_tips(self):
        """Display learning tips"""
        print("\n" + "="*60)
        print("💡 LEARNING TIPS")
        print("="*60)
        print("""
1. CONSISTENCY: Study 1-2 hours daily, not cramming
2. PRACTICE: Complete all exercises, don't just read
3. UNDERSTAND: Focus on concepts, not just code
4. EXPERIMENT: Modify code and see what happens
5. VISUALIZE: Draw circuits and quantum states
6. DEBUG: Use simulators to debug your code
7. COMMUNITY: Join quantum computing communities
8. BUILD: Apply knowledge to real projects

Recommended Schedule:
  • Monday-Friday: 1.5 hours daily (theory + exercises)
  • Saturday: 2 hours (review + mini-project)
  • Sunday: 1 hour (consolidation + planning)

Total: ~12 hours/week = ~13 weeks for all 3 levels
""")
        print("="*60 + "\n")
    
    def display_assessment_guide(self, level: int):
        """Display self-assessment guide"""
        assessments = {
            1: {
                'title': 'After Level 1 (Foundations)',
                'criteria': [
                    'Can create basic quantum circuits',
                    'Understand superposition and entanglement',
                    'Can measure quantum states correctly',
                    'Familiar with common gates (H, X, Y, Z, CNOT)',
                    'Can visualize quantum circuits'
                ]
            },
            2: {
                'title': 'After Level 2 (Algorithms)',
                'criteria': [
                    'Can implement Deutsch-Jozsa algorithm',
                    'Can implement Grover\'s algorithm',
                    'Understand quantum advantage concepts',
                    'Can design simple oracles',
                    'Understand QFT and phase estimation'
                ]
            },
            3: {
                'title': 'After Level 3 (Advanced)',
                'criteria': [
                    'Can implement VQE for molecular simulation',
                    'Can implement QAOA for optimization',
                    'Understand error correction basics',
                    'Can build quantum ML models',
                    'Ready for research or production work'
                ]
            }
        }
        
        if level not in assessments:
            return
        
        assessment = assessments[level]
        print(f"\n{'='*60}")
        print(f"✅ {assessment['title'].upper()}")
        print(f"{'='*60}")
        print("\nYou should be able to:\n")
        
        for i, criterion in enumerate(assessment['criteria'], 1):
            print(f"  ☐ {criterion}")
        
        print("\n" + "="*60 + "\n")
    
    def display_resources(self):
        """Display learning resources"""
        print("\n" + "="*60)
        print("📚 LEARNING RESOURCES")
        print("="*60)
        print("""
Official Tutorials:
  • Qiskit Textbook: https://qiskit.org/textbook
  • IBM Quantum: https://quantum.ibm.com/
  • Microsoft Quantum: https://azure.microsoft.com/en-us/services/quantum/
  • Google Cirq: https://quantumai.google/cirq
  • Xanadu PennyLane: https://pennylane.ai/

Interactive Learning:
  • Microsoft Quantum Katas: https://github.com/microsoft/QuantumKatas
  • Qiskit Challenges: https://www.ibm.com/quantum/challenges
  • PennyLane Demos: https://pennylane.ai/qml/demos/

Books:
  • "Quantum Computation and Quantum Information" - Nielsen & Chuang
  • "Programming Quantum Computers" - Aaronson et al.
  • "Quantum Computing in Action" - Hidary
  • "Learn Quantum Computing with Python and Q#" - Kaiser

Communities:
  • Qiskit Slack: https://qiskit.slack.com/
  • Quantum Computing Stack Exchange: https://quantumcomputing.stackexchange.com/
  • Reddit: r/QuantumComputing
  • GitHub Discussions

Benchmarks & Challenges:
  • IBM Quantum Challenges
  • Qiskit Global Summer School
  • Quantum Katas (Microsoft)
""")
        print("="*60 + "\n")
    
    def generate_personalized_plan(self, current_level: int, hours_per_week: float) -> Dict:
        """Generate personalized learning plan"""
        plan = {
            'current_level': current_level,
            'hours_per_week': hours_per_week,
            'weekly_schedule': [],
            'estimated_completion': None
        }
        
        # Generate weekly schedule
        if current_level <= 3:
            level_info = self.levels[current_level]
            topics = level_info['topics']
            
            weekly_hours = hours_per_week
            current_week = 1
            
            for topic in topics:
                hours_needed = int(topic['time'].split('-')[0])
                weeks_needed = max(1, int(hours_needed / weekly_hours))
                
                plan['weekly_schedule'].append({
                    'topic': topic['name'],
                    'weeks': weeks_needed,
                    'exercises': topic['exercises']
                })
                current_week += weeks_needed
            
            plan['estimated_completion'] = current_week
        
        return plan
    
    def display_menu(self):
        """Display main menu"""
        print("\n" + "="*60)
        print("MAIN MENU")
        print("="*60)
        print("""
1. View Level 1 (Foundations)
2. View Level 2 (Algorithms)
3. View Level 3 (Advanced Topics)
4. View Learning Tips
5. Self-Assessment Guide
6. Learning Resources
7. Generate Personalized Plan
8. Exit
""")
        print("="*60)
    
    def run_interactive(self):
        """Run interactive roadmap"""
        self.display_welcome()
        
        while True:
            self.display_menu()
            choice = input("Select option (1-8): ").strip()
            
            if choice == '1':
                self.display_level(1)
                topic = input("View topic details (1-3) or press Enter to skip: ").strip()
                if topic.isdigit() and 1 <= int(topic) <= 3:
                    self.display_topic_details(1, int(topic))
            
            elif choice == '2':
                self.display_level(2)
                topic = input("View topic details (1-4) or press Enter to skip: ").strip()
                if topic.isdigit() and 1 <= int(topic) <= 4:
                    self.display_topic_details(2, int(topic))
            
            elif choice == '3':
                self.display_level(3)
                topic = input("View topic details (1-4) or press Enter to skip: ").strip()
                if topic.isdigit() and 1 <= int(topic) <= 4:
                    self.display_topic_details(3, int(topic))
            
            elif choice == '4':
                self.display_learning_tips()
            
            elif choice == '5':
                level = input("Assessment for level (1-3): ").strip()
                if level.isdigit() and 1 <= int(level) <= 3:
                    self.display_assessment_guide(int(level))
            
            elif choice == '6':
                self.display_resources()
            
            elif choice == '7':
                level = input("Current level (1-3): ").strip()
                hours = input("Hours per week (default 10): ").strip()
                if level.isdigit() and 1 <= int(level) <= 3:
                    hours_per_week = float(hours) if hours else 10.0
                    plan = self.generate_personalized_plan(int(level), hours_per_week)
                    print("\n" + "="*60)
                    print("📅 PERSONALIZED LEARNING PLAN")
                    print("="*60)
                    print(f"Current Level: {plan['current_level']}")
                    print(f"Hours per Week: {plan['hours_per_week']}")
                    print(f"Estimated Completion: {plan['estimated_completion']} weeks\n")
                    print("Weekly Topics:")
                    for i, item in enumerate(plan['weekly_schedule'], 1):
                        print(f"  Week {i}: {item['topic']} ({item['weeks']} weeks, {item['exercises']} exercises)")
                    print("="*60 + "\n")
            
            elif choice == '8':
                print("\n✨ Good luck with your quantum computing journey!")
                break
            
            else:
                print("❌ Invalid option. Please try again.")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Quantum Computing Learning Roadmap')
    parser.add_argument('--level', type=int, choices=[1, 2, 3], help='Display specific level')
    parser.add_argument('--tips', action='store_true', help='Display learning tips')
    parser.add_argument('--resources', action='store_true', help='Display resources')
    parser.add_argument('--assessment', type=int, choices=[1, 2, 3], help='Display assessment guide')
    parser.add_argument('--interactive', action='store_true', help='Run interactive mode')
    
    args = parser.parse_args()
    
    roadmap = LearningRoadmap()
    
    if args.level:
        roadmap.display_level(args.level)
    elif args.tips:
        roadmap.display_learning_tips()
    elif args.resources:
        roadmap.display_resources()
    elif args.assessment:
        roadmap.display_assessment_guide(args.assessment)
    elif args.interactive or not any([args.level, args.tips, args.resources, args.assessment]):
        roadmap.run_interactive()


if __name__ == '__main__':
    main()

if __name__ == "__main__":
    main()
