#!/usr/bin/env python3
import openai
import os

def test_openai_connection():
    """Test OpenAI API connection"""
    try:
        client = openai.OpenAI()
        
        # Test embeddings
        print("Testing OpenAI embeddings...")
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input="This is a test sentence."
        )
        print(f"✅ Embeddings API working. Dimension: {len(response.data[0].embedding)}")
        
        # Test chat completion
        print("Testing OpenAI chat completion...")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        print(f"✅ Chat API working. Response: {response.choices[0].message.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_openai_connection()

