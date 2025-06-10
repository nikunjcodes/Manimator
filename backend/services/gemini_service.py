"""
Google Gemini AI Service for ManimAI
Handles AI-powered code generation, improvement, and chat functionality
"""

import logging
import re
import json
from typing import Dict, List, Optional, Any
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

logger = logging.getLogger(__name__)

class GeminiService:
    """Google Gemini AI service for Manim code generation and assistance"""
    
    def __init__(self, api_key: str):
        """Initialize Gemini service"""
        if not api_key:
            raise ValueError("Gemini API key is required")
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Safety settings
            self.safety_settings = {
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
            
            logger.info("Gemini service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {e}")
            raise
    
    def health_check(self) -> bool:
        """Check if Gemini service is available"""
        try:
            # Simple test generation
            response = self.model.generate_content(
                "Say 'OK' if you're working",
                safety_settings=self.safety_settings,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=10,
                )
            )
            return response.text is not None
        except Exception as e:
            logger.error(f"Gemini health check failed: {e}")
            return False
    
    def generate_manim_code(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate Manim code from natural language prompt"""
        try:
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(prompt, context)
            
            full_prompt = f"{system_prompt}\n\nUser Request: {user_prompt}"
            
            response = self.model.generate_content(
                full_prompt,
                safety_settings=self.safety_settings,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2048,
                )
            )
            
            if not response.text:
                raise ValueError("No response generated from Gemini")
            
            # Parse the response
            parsed_response = self._parse_response(response.text)
            
            # Validate the generated code
            validation = self._validate_manim_code(parsed_response.get('code', ''))
            parsed_response['validation'] = validation
            
            logger.info(f"Manim code generated successfully for prompt: {prompt[:50]}...")
            return parsed_response
            
        except Exception as e:
            logger.error(f"Manim code generation failed: {e}")
            raise
    
    def improve_manim_code(self, code: str, improvement_request: str = "") -> Dict[str, Any]:
        """Improve existing Manim code"""
        try:
            prompt = f"""
            Please improve this Manim code based on the following request: {improvement_request}
            
            Current code:
            ```python
            {code}
            ```
            
            Please provide the improved code with explanations of what was changed.
            """
            
            return self.generate_manim_code(prompt, {'type': 'improvement'})
        except Exception as e:
            logger.error(f"Code improvement failed: {e}")
            raise
    
    def explain_code(self, code: str) -> str:
        """Generate explanation for Manim code"""
        try:
            prompt = f"""
            Please explain this Manim code in simple terms, describing what animation it creates:
            
            ```python
            {code}
            ```
            
            Provide a clear, educational explanation suitable for someone learning mathematical visualization.
            Include:
            1. What mathematical concept is being visualized
            2. Key animation steps
            3. Educational value
            """
            
            response = self.model.generate_content(
                prompt,
                safety_settings=self.safety_settings,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1024,
                )
            )
            
            return response.text or "Unable to generate explanation"
        except Exception as e:
            logger.error(f"Code explanation failed: {e}")
            return "Error generating explanation"
    
    def suggest_improvements(self, code: str) -> List[str]:
        """Suggest improvements for Manim code"""
        try:
            prompt = f"""
            Analyze this Manim code and suggest 3-5 specific improvements:
            
            ```python
            {code}
            ```
            
            Focus on:
            - Mathematical accuracy
            - Visual clarity
            - Animation smoothness
            - Code efficiency
            - Educational value
            
            Provide suggestions as a numbered list.
            """
            
            response = self.model.generate_content(
                prompt,
                safety_settings=self.safety_settings,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.5,
                    max_output_tokens=1024,
                )
            )
            
            if response.text:
                # Extract numbered suggestions
                suggestions = re.findall(r'\d+\.\s*(.+)', response.text)
                return suggestions[:5]  # Limit to 5 suggestions
            
            return []
        except Exception as e:
            logger.error(f"Suggestion generation failed: {e}")
            return []
    
    def chat_response(self, message: str, chat_history: List[Dict[str, str]] = None) -> str:
        """Generate a chat response for general Manim/math questions"""
        try:
            # Build context from chat history
            context = ""
            if chat_history:
                for msg in chat_history[-5:]:  # Last 5 messages for context
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    context += f"{role}: {content}\n"
            
            prompt = f"""
            You are a helpful assistant specializing in mathematical visualization and Manim animations.
            You help users understand mathematical concepts and create beautiful animations.
            
            Previous conversation:
            {context}
            
            User question: {message}
            
            Provide a helpful, educational response. If the question is about creating animations, 
            suggest using the animation generation feature. Keep responses concise but informative.
            """
            
            response = self.model.generate_content(
                prompt,
                safety_settings=self.safety_settings,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1024,
                )
            )
            
            return response.text or "I'm sorry, I couldn't generate a response. Please try again."
        except Exception as e:
            logger.error(f"Chat response generation failed: {e}")
            return "I'm experiencing some technical difficulties. Please try again later."
    
    def generate_animation_title(self, prompt: str, code: str = "") -> str:
        """Generate a title for the animation"""
        try:
            title_prompt = f"""
            Generate a concise, descriptive title for a mathematical animation based on this prompt:
            "{prompt}"
            
            The title should be:
            - Clear and descriptive
            - Under 60 characters
            - Educational and engaging
            - Focused on the mathematical concept
            
            Return only the title, nothing else.
            """
            
            response = self.model.generate_content(
                title_prompt,
                safety_settings=self.safety_settings,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.5,
                    max_output_tokens=100,
                )
            )
            
            title = response.text.strip() if response.text else "Mathematical Animation"
            # Clean up the title
            title = re.sub(r'^["\']|["\']$', '', title)  # Remove quotes
            title = title[:60]  # Limit length
            
            return title
        except Exception as e:
            logger.error(f"Title generation failed: {e}")
            return "Mathematical Animation"
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for Manim code generation"""
        return """
        You are an expert in mathematical visualization and the Manim library. Your task is to generate clean, 
        well-commented Python code using Manim that creates beautiful mathematical animations.
        
        Guidelines:
        1. Always import necessary Manim components at the top
        2. Create a class that inherits from Scene
        3. Use proper mathematical notation and symbols
        4. Include smooth animations and transitions
        5. Add helpful comments explaining the mathematical concepts
        6. Ensure code is executable and follows Manim best practices
        7. Use appropriate colors and styling for clarity
        8. Include proper timing and sequencing
        9. Make animations educational and visually appealing
        10. Use self.play() for animations and self.wait() for pauses
        
        Response format:
        TITLE: [Brief title for the animation]
        DESCRIPTION: [One-line description of what the animation shows]
        CODE:
        ```python
        [Your complete, executable Manim code here]
        ```
        EXPLANATION: [Brief explanation of the mathematical concept being visualized]
        EDUCATIONAL_VALUE: [Why this visualization is helpful for learning]
        SUGGESTIONS: [Optional suggestions for variations or extensions]
        """
    
    def _build_user_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build the user prompt with context"""
        user_prompt = f"Create a Manim animation for: {prompt}"
        
        if context:
            if context.get('type') == 'improvement':
                user_prompt += "\n\nThis is an improvement request for existing code."
            if context.get('difficulty'):
                user_prompt += f"\n\nDifficulty level: {context['difficulty']}"
            if context.get('duration'):
                user_prompt += f"\n\nTarget duration: {context['duration']} seconds"
            if context.get('style'):
                user_prompt += f"\n\nVisualization style: {context['style']}"
        
        return user_prompt
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the AI response to extract structured information"""
        try:
            result = {}
            
            # Extract title
            title_match = re.search(r'TITLE:\s*(.+)', response_text, re.IGNORECASE)
            result['title'] = title_match.group(1).strip() if title_match else "Generated Animation"
            
            # Extract description
            desc_match = re.search(r'DESCRIPTION:\s*(.+)', response_text, re.IGNORECASE)
            result['description'] = desc_match.group(1).strip() if desc_match else ""
            
            # Extract code
            code_match = re.search(r'```python\s*\n(.*?)\n```', response_text, re.DOTALL | re.IGNORECASE)
            if code_match:
                result['code'] = code_match.group(1).strip()
            else:
                # Fallback: try to extract any code block
                code_match = re.search(r'```\s*\n(.*?)\n```', response_text, re.DOTALL)
                result['code'] = code_match.group(1).strip() if code_match else response_text
            
            # Extract explanation
            exp_match = re.search(r'EXPLANATION:\s*(.+?)(?=EDUCATIONAL_VALUE:|SUGGESTIONS:|$)', response_text, re.DOTALL | re.IGNORECASE)
            result['explanation'] = exp_match.group(1).strip() if exp_match else ""
            
            # Extract educational value
            edu_match = re.search(r'EDUCATIONAL_VALUE:\s*(.+?)(?=SUGGESTIONS:|$)', response_text, re.DOTALL | re.IGNORECASE)
            result['educational_value'] = edu_match.group(1).strip() if edu_match else ""
            
            # Extract suggestions
            sugg_match = re.search(r'SUGGESTIONS:\s*(.+)', response_text, re.DOTALL | re.IGNORECASE)
            if sugg_match:
                suggestions_text = sugg_match.group(1).strip()
                result['suggestions'] = [s.strip() for s in suggestions_text.split('\n') if s.strip()]
            else:
                result['suggestions'] = []
            
            return result
        except Exception as e:
            logger.error(f"Response parsing failed: {e}")
            return {
                'code': response_text,
                'title': 'Generated Animation',
                'description': '',
                'explanation': '',
                'educational_value': '',
                'suggestions': []
            }
    
    def _validate_manim_code(self, code: str) -> Dict[str, Any]:
        """Validate the generated Manim code"""
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        try:
            # Check for required imports
            if 'from manim import' not in code and 'import manim' not in code:
                validation['errors'].append("Missing Manim import statement")
                validation['is_valid'] = False
            
            # Check for Scene class
            if 'class' not in code or 'Scene' not in code:
                validation['errors'].append("Missing Scene class definition")
                validation['is_valid'] = False
            
            # Check for construct method
            if 'def construct(self):' not in code:
                validation['errors'].append("Missing construct method")
                validation['is_valid'] = False
            
            # Check for basic syntax issues
            try:
                compile(code, '<string>', 'exec')
            except SyntaxError as e:
                validation['errors'].append(f"Syntax error: {str(e)}")
                validation['is_valid'] = False
            
            # Warnings and suggestions
            if 'self.play(' not in code:
                validation['warnings'].append("No animations found - consider adding self.play() calls")
            
            if 'self.wait(' not in code:
                validation['suggestions'].append("Consider adding wait times between animations")
            
            if len(code.split('\n')) > 100:
                validation['warnings'].append("Code is quite long - consider breaking into smaller scenes")
            
            # Check for common Manim patterns
            if 'self.add(' in code and 'self.play(' not in code:
                validation['suggestions'].append("Consider using self.play() instead of self.add() for animations")
            
        except Exception as e:
            logger.error(f"Code validation failed: {e}")
            validation['errors'].append(f"Validation error: {str(e)}")
            validation['is_valid'] = False
        
        return validation