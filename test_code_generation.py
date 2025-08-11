#!/usr/bin/env python3
"""
Test script for the code generation feature
"""
import asyncio
import os
from app.mods.chat.code_generator import create_code_generator


async def test_code_generation():
    """Test the code generation functionality"""
    
    # Check if API key is available
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        print("Please set your Gemini API key to test the code generation feature")
        return
    
    print("🧪 Testing Code Generation Feature")
    print("=" * 50)
    
    # Create code generator
    generator = create_code_generator(api_key)
    
    # Test cases
    test_cases = [
        "Create a simple HTML button with CSS styling and JavaScript click handler",
        "Build a React login form component",
        "What's the weather like today?",  # Should not trigger code generation
        "Make a Python function to calculate fibonacci numbers",
        "Hello, how are you?"  # Should not trigger code generation
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case}")
        print("-" * 40)
        
        # Check if it's detected as a programming question
        is_programming = generator.is_programming_question(test_case)
        print(f"Programming question detected: {'✅ Yes' if is_programming else '❌ No'}")
        
        if is_programming:
            try:
                # Generate code
                result = await generator.generate_code(test_case)
                print(f"Description: {result.description}")
                print(f"Generated {len(result.files)} file(s):")
                
                for file in result.files:
                    print(f"  📄 {file.filename} ({file.language})")
                    # Show first few lines of content
                    lines = file.content.split('\n')[:3]
                    for line in lines:
                        print(f"    {line}")
                    if len(file.content.split('\n')) > 3:
                        print("    ...")
                        
            except Exception as e:
                print(f"❌ Error generating code: {e}")
    
    print("\n✅ Code generation testing completed!")


if __name__ == "__main__":
    asyncio.run(test_code_generation())