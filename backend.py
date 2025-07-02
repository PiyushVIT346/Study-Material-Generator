import os
import re
from typing import List, Dict, Any, TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import json
import uuid


load_dotenv()

class StudyMaterialState(TypedDict):
    """State schema for the study material generation workflow"""
    topic: str
    subtopics: List[str]
    current_subtopic_index: int
    study_materials: List[Dict[str, Any]]
    current_subtopic: str
    key_concepts: List[str]
    description: str
    summary: str
    quiz: Dict[str, Any]
    final_output: Dict[str, Any]
    max_iterations: int
    iteration_count: int

class StudyMaterialGenerator:
    """Main class for generating AI-powered study materials"""
    
    def __init__(self, groq_api_key: str = None):
        """
        Initialize the study material generator
        
        Args:
            groq_api_key: Groq API key (optional, can use env variable)
        """
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY must be provided or set as environment variable")
        
        self.llm = ChatGroq(
            api_key=self.groq_api_key,
            model="llama3-70b-8192",
            temperature=0.7
        )
        
        self.graph = self._build_graph()
    
    def _safe_json_parser(self, text):
        """
        Safely parse JSON from LLM output, handling cases where additional text is present
        
        Args:
            text: Raw text output from LLM
            
        Returns:
            Parsed JSON object
        """
        import re
        
        if hasattr(text, 'content'):
            text = text.content
        
        json_match = re.search(r'(\[.*\]|\{.*\})', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        try:
            parser = JsonOutputParser()
            return parser.parse(text)
        except Exception as e:
            print(f"JSON parsing failed: {e}")
            print(f"Raw output: {text[:200]}")
            if isinstance(text, str) and '[' in text:
                return []
            else:
                return {}
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(StudyMaterialState)
        
        workflow.add_node("get_topic", self.get_topic)
        workflow.add_node("generate_subtopics", self.generate_subtopics)
        workflow.add_node("generate_key_concepts", self.generate_key_concepts)
        workflow.add_node("generate_description", self.generate_description)
        workflow.add_node("generate_summary", self.generate_summary)
        workflow.add_node("generate_quiz", self.generate_quiz)
        workflow.add_node("process_next_subtopic", self.process_next_subtopic)
        workflow.add_node("finalize_output", self.finalize_output)
        
        workflow.set_entry_point("get_topic")
        workflow.add_edge("get_topic", "generate_subtopics")
        workflow.add_edge("generate_subtopics", "process_next_subtopic")
        workflow.add_edge("process_next_subtopic", "generate_key_concepts")
        workflow.add_edge("generate_key_concepts", "generate_description")
        workflow.add_edge("generate_description", "generate_summary")
        workflow.add_edge("generate_summary", "generate_quiz")
        
        workflow.add_conditional_edges(
            "generate_quiz",
            self._should_continue,
            {
                "continue": "process_next_subtopic",
                "end": "finalize_output"
            }
        )
        workflow.add_edge("finalize_output", END)
        
        return workflow.compile(checkpointer=MemorySaver())
    
    def get_topic(self, state: StudyMaterialState) -> StudyMaterialState:
        """
        Process and validate the input topic
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with processed topic
        """
        topic = state.get("topic", "").strip()
        if not topic:
            raise ValueError("Topic cannot be empty")
        
        print(f" Processing topic: {topic}")
        return {
            **state,
            "topic": topic,
            "subtopics": [],
            "current_subtopic_index": 0,
            "study_materials": [],
            "max_iterations": 50,
            "iteration_count": 0
        }
    
    def generate_subtopics(self, state: StudyMaterialState) -> StudyMaterialState:
        """
        Generate relevant subtopics for the main topic
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with generated subtopics
        """
        prompt = ChatPromptTemplate.from_template("""
        Generate 5-7 relevant subtopics for the topic: "{topic}"
        
        Requirements:
        - Each subtopic should be specific and focused
        - Subtopics should cover different aspects of the main topic
        - Avoid overlap between subtopics
        - Make them suitable for educational content
        
        IMPORTANT: Return ONLY a valid JSON array of strings. No additional text, explanations, or formatting.
        
        Format: ["Subtopic 1", "Subtopic 2", "Subtopic 3"]
        """)
        
        chain = prompt | self.llm | self._safe_json_parser
        subtopics = chain.invoke({"topic": state["topic"]})
        
        print(f" Generated {len(subtopics)} subtopics")
        for i, subtopic in enumerate(subtopics, 1):
            print(f"  {i}. {subtopic}")
        
        return {
            **state,
            "subtopics": subtopics
        }
    
    def process_next_subtopic(self, state: StudyMaterialState) -> StudyMaterialState:
        """
        Set up processing for the next subtopic
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with current subtopic information
        """
        current_index = state.get("current_subtopic_index", 0)
        subtopics = state.get("subtopics", [])
        
        if current_index >= len(subtopics):
            print(f"  No more subtopics to process. Index: {current_index}, Total: {len(subtopics)}")
            return state
        
        current_subtopic = subtopics[current_index]
        
        print(f"\n Processing subtopic {current_index + 1}/{len(subtopics)}: {current_subtopic}")
        
        return {
            **state,
            "current_subtopic": current_subtopic,
            "iteration_count": state.get("iteration_count", 0) + 1
        }
    
    def generate_key_concepts(self, state: StudyMaterialState) -> StudyMaterialState:
        """
        Generate key concepts for the current subtopic
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with key concepts
        """
        prompt = ChatPromptTemplate.from_template("""
        Generate 4-6 key concepts for the subtopic: "{subtopic}" 
        within the context of the main topic: "{topic}"
        
        Requirements:
        - Each concept should be fundamental to understanding the subtopic
        - Concepts should be concise (1-3 words each)
        - Focus on the most important ideas students need to know
        
        IMPORTANT: Return ONLY a valid JSON array of strings. No additional text or explanations.
        
        Format: ["Concept 1", "Concept 2", "Concept 3"]
        """)
        
        chain = prompt | self.llm | self._safe_json_parser
        key_concepts = chain.invoke({
            "topic": state["topic"],
            "subtopic": state["current_subtopic"]
        })
        
        print(f"   Key concepts: {', '.join(key_concepts)}")
        
        return {
            **state,
            "key_concepts": key_concepts
        }
    
    def generate_description(self, state: StudyMaterialState) -> StudyMaterialState:
        """
        Generate detailed description for the current subtopic
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with description
        """
        prompt = ChatPromptTemplate.from_template("""
        Write a comprehensive description for the subtopic: "{subtopic}"
        within the context of the main topic: "{topic}"
        
        Key concepts to cover: {key_concepts}
        
        Requirements:
        - 200-300 words
        - Educational and informative tone
        - Include examples where relevant
        - Make it accessible to students
        - Cover all the key concepts naturally
        - Try to also include formula if subtopic is related to math or science.
        - Try to include code lines also if subtopic is related to programming.
        
        Return only the description text, no additional formatting.
        """)
        
        chain = prompt | self.llm | StrOutputParser()
        description = chain.invoke({
            "topic": state["topic"],
            "subtopic": state["current_subtopic"],
            "key_concepts": ", ".join(state["key_concepts"])
        })
        
        print(f"   Generated description ({len(description)} characters)")
        
        return {
            **state,
            "description": description.strip()
        }
    
    def generate_summary(self, state: StudyMaterialState) -> StudyMaterialState:
        """
        Generate summary for the current subtopic
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with summary
        """
        prompt = ChatPromptTemplate.from_template("""
        Create a concise summary of the following description about "{subtopic}":
        
        Description: {description}
        
        Requirements:
        - 50-80 words maximum
        - Capture the essential points
        - Use clear, simple language
        - Focus on the most important information
        
        Return only the summary text.
        """)
        
        chain = prompt | self.llm | StrOutputParser()
        summary = chain.invoke({
            "subtopic": state["current_subtopic"],
            "description": state["description"]
        })
        
        print(f"   Generated summary ({len(summary)} characters)")
        
        return {
            **state,
            "summary": summary.strip()
        }
    
    def generate_quiz(self, state: StudyMaterialState) -> StudyMaterialState:
        """
        Generate quiz questions for the current subtopic
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with quiz
        """
        prompt = ChatPromptTemplate.from_template("""
        Create a quiz for the subtopic: "{subtopic}" based on this content:
        
        Key Concepts: {key_concepts}
        Description: {description}
        
        Generate exactly 3 multiple-choice questions with 4 options each.
        
        IMPORTANT: Return ONLY valid JSON. No additional text or explanations.
        
        Format:
        {{
            "questions": [
                {{
                    "question": "Question text?",
                    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                    "correct_answer": "A",
                    "explanation": "Brief explanation of why this is correct"
                }}
            ]
        }}
        """)
        
        chain = prompt | self.llm | self._safe_json_parser
        quiz = chain.invoke({
            "subtopic": state["current_subtopic"],
            "key_concepts": ", ".join(state["key_concepts"]),
            "description": state["description"]
        })
        
        print(f"   Generated quiz with {len(quiz['questions'])} questions")
        
        subtopic_material = {
            "subtopic": state["current_subtopic"],
            "key_concepts": state["key_concepts"],
            "description": state["description"],
            "summary": state["summary"],
            "quiz": quiz
        }
        
        study_materials = state.get("study_materials", []).copy()
        study_materials.append(subtopic_material)
        
        new_index = state.get("current_subtopic_index", 0) + 1
        print(f"   Completed subtopic {new_index}/{len(state.get('subtopics', []))}")
        
        return {
            **state,
            "quiz": quiz,
            "study_materials": study_materials,
            "current_subtopic_index": new_index
        }
    
    def _should_continue(self, state: StudyMaterialState) -> str:
        """
        Determine if there are more subtopics to process
        
        Args:
            state: Current workflow state
            
        Returns:
            "continue" if more subtopics exist, "end" otherwise
        """
        current_index = state.get("current_subtopic_index", 0)
        total_subtopics = len(state.get("subtopics", []))
        iteration_count = state.get("iteration_count", 0)
        max_iterations = state.get("max_iterations", 50)
        
        print(f"   Checking continuation: {current_index}/{total_subtopics} (iteration {iteration_count})")
        
        if iteration_count >= max_iterations:
            print(f"  Maximum iterations ({max_iterations}) reached. Ending workflow.")
            return "end"
        
        if current_index < total_subtopics:
            return "continue"
        return "end"
    
    def finalize_output(self, state: StudyMaterialState) -> StudyMaterialState:
        """
        Finalize and structure the complete study material
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with final output
        """
        final_output = {
            "topic": state["topic"],
            "total_subtopics": len(state["subtopics"]),
            "study_materials": state["study_materials"],
            "generation_summary": {
                "subtopics_covered": len(state["study_materials"]),
                "total_key_concepts": sum(len(material["key_concepts"]) for material in state["study_materials"]),
                "total_quiz_questions": sum(len(material["quiz"]["questions"]) for material in state["study_materials"])
            }
        }
        
        print(f"\n Study material generation completed!")
        print(f" Summary: {final_output['generation_summary']['subtopics_covered']} subtopics, "
              f"{final_output['generation_summary']['total_key_concepts']} key concepts, "
              f"{final_output['generation_summary']['total_quiz_questions']} quiz questions")
        
        return {
            **state,
            "final_output": final_output
        }
    
    def generate_study_material(self, topic: str) -> Dict[str, Any]:
        """
        Generate complete study material for a given topic
        
        Args:
            topic: The main topic to generate study materials for
            
        Returns:
            Dictionary containing all generated study materials
        """
        initial_state = StudyMaterialState(
            topic=topic,
            subtopics=[],
            current_subtopic_index=0,
            study_materials=[],
            current_subtopic="",
            key_concepts=[],
            description="",
            summary="",
            quiz={},
            final_output={},
            max_iterations=50,
            iteration_count=0
        )
        
        config = {
            "configurable": {"thread_id": str(uuid.uuid4())},
            "recursion_limit": 50
        }
        result = self.graph.invoke(initial_state, config=config)
        return result["final_output"]
    
    def save_study_material(self, study_material: Dict[str, Any], filename: str = None):
        """
        Save study material to a JSON file
        
        Args:
            study_material: The generated study material
            filename: Optional filename (auto-generated if not provided)
        """
        if not filename:
            safe_topic = "".join(c for c in study_material["topic"] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"study_material_{safe_topic.replace(' ', '_').lower()}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(study_material, f, indent=2, ensure_ascii=False)
        
        print(f" Study material saved to: {filename}")

def main():
    """Example usage of the Study Material Generator"""
    try:
        generator = StudyMaterialGenerator()
        
        topic = input("Enter a topic for study material generation: ").strip()
        if not topic:
            print(" Topic cannot be empty!")
            return
        
        print(f"\n Starting study material generation for: '{topic}'")
        print("=" * 60)
        
        study_material = generator.generate_study_material(topic)
        
        generator.save_study_material(study_material)
        
        print("\n" + "=" * 60)
        print(" STUDY MATERIAL PREVIEW")
        print("=" * 60)
        
        for i, material in enumerate(study_material["study_materials"], 1):
            print(f"\n{i}. {material['subtopic']}")
            print(f"   Key Concepts: {', '.join(material['key_concepts'])}")
            print(f"   Summary: {material['summary'][:100]}...")
            print(f"   Quiz Questions: {len(material['quiz']['questions'])}")
        
    except KeyboardInterrupt:
        print("\n\n  Generation stopped by user")
    except Exception as e:
        print(f"\n Error: {str(e)}")

if __name__ == "__main__":
    main()