
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    print("Error: DEEPSEEK_API_KEY not found in .env")
    sys.exit(1)

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

def test_memory(ticker, date):
    print(f"Testing memory for {ticker} on {date}...")
    
    prompt = f"""
    What major financial news happened for {ticker} on or around {date}? 
    Summarize the key event in 1 headline-style sentence.
    Then, provide a sentiment score from -1.0 (very negative) to 1.0 (very positive).
    
    Format:
    HEADLINE: [Your headline]
    SCORE: [Your score]
    """
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a financial historian."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=100
        )
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test NVDA's massive jump in May 2023
    test_memory("NVDA", "2023-05-25")
    
    # Test a random bearish day (e.g., during 2022 crash)
    print("\n" + "-"*30 + "\n")
    test_memory("NVDA", "2022-09-01")
