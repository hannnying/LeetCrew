import requests

# LEETCODE_API = "https://alfa-leetcode-api.onrender.com" # replace with local host
LEETCODE_API = "http://localhost:3000" 

def fetch_question_details(question):
    """Fetch a LeetCode question and its metadata from the hosted API."""
    url = f"{LEETCODE_API}/select?titleSlug={question}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data 
    except requests.RequestException as e:
        print(f"Error fetching problems: {e}")
        return None
    