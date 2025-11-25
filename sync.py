# sync.py - Sync solved LeetCode problems to Notion (no duplicates)

import os
import requests
import time
import socket
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
LEETCODE_CSRF = os.getenv("LEETCODE_CSRF")

NOTION_VERSION = "2022-06-28"
NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION
}

def check_internet_connection(timeout=5):
    """
    Check if internet connection is available by trying to connect to Google DNS
    """
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        return True
    except OSError:
        return False

def wait_for_internet(max_retries=None, retry_interval=30):
    """
    Wait for internet connection with exponential backoff.
    If max_retries is None, it will retry indefinitely.
    retry_interval is the initial wait time in seconds.
    """
    attempt = 0
    while True:
        if check_internet_connection():
            print(f"✓ Internet connection restored at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return True
        
        attempt += 1
        if max_retries is not None and attempt > max_retries:
            print(f"✗ Failed to connect after {max_retries} attempts")
            return False
        
        wait_time = retry_interval * (2 ** (attempt - 1)) if attempt > 1 else retry_interval
        wait_time = min(wait_time, 300)  # Cap at 5 minutes
        
        print(f"No internet connection. Waiting {wait_time}s before retry (attempt {attempt})...")
        time.sleep(wait_time)

def get_existing_problems():
    """
    Returns a dict mapping problem_id -> notion page_id
    """
    existing = {}
    has_more = True
    start_cursor = None
    
    print("Checking existing problems in Notion...")
    
    if not check_internet_connection():
        print("No internet connection. Waiting for connection...")
        if not wait_for_internet():
            print("Could not establish internet connection")
            return existing
    
    try:
        while has_more:
            url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
            payload = {"page_size": 100}
            if start_cursor:
                payload["start_cursor"] = start_cursor
            
            response = requests.post(url, json=payload, headers=NOTION_HEADERS)
            response.raise_for_status()
            data = response.json()
            
            for page in data["results"]:
                id_prop = page["properties"].get("ID", {})
                if id_prop.get("type") == "number" and id_prop.get("number") is not None:
                    problem_id = int(id_prop["number"])
                    page_id = page["id"]
                    existing[problem_id] = page_id
            
            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")
        
        print(f"✓ Found {len(existing)} existing problems")
    except Exception as e:
        print(f"Error: {e}")
    
    return existing

def get_all_solved_problems():
    """
    Fetch all solved problems from LeetCode
    """
    url = "https://leetcode.com/graphql"
    
    query = """
    query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
        problemsetQuestionList: questionList(
            categorySlug: $categorySlug
            limit: $limit
            skip: $skip
            filters: $filters
        ) {
            total: totalNum
            questions: data {
                difficulty
                frontendQuestionId: questionFrontendId
                status
                title
                titleSlug
                topicTags {
                    name
                }
            }
        }
    }
    """
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}; csrftoken={LEETCODE_CSRF}",
        "x-csrftoken": LEETCODE_CSRF,
        "Referer": "https://leetcode.com"
    }
    
    all_solved = []
    skip = 0
    limit = 100
    
    print("\nFetching solved problems from LeetCode...")
    
    if not check_internet_connection():
        print("No internet connection. Waiting for connection...")
        if not wait_for_internet():
            print("Could not establish internet connection")
            return all_solved
    
    while True:
        payload = {
            "query": query,
            "variables": {
                "categorySlug": "",
                "skip": skip,
                "limit": limit,
                "filters": {}
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            problems = data['data']['problemsetQuestionList']['questions']
            total = data['data']['problemsetQuestionList']['total']
            
            solved = [p for p in problems if p.get('status') == 'ac']
            all_solved.extend(solved)
            
            print(f"Fetched {skip + len(problems)}/{total} problems... {len(all_solved)} solved")
            
            if skip + len(problems) >= total:
                break
                
            skip += limit
            
        except Exception as e:
            print(f"Error: {e}")
            break
    
    print(f"✓ Total solved: {len(all_solved)}")
    return all_solved

def sync_to_notion(existing_problems, solved_problems):
    """
    Sync problems to Notion - update existing, create new
    """
    print(f"\n{'='*60}")
    print("Starting sync...")
    print(f"{'='*60}\n")
    
    skipped = 0
    created = 0
    
    for problem in solved_problems:
        problem_id = int(problem['frontendQuestionId'])
        title = problem['title']
        level = problem['difficulty']
        topics = [tag['name'] for tag in problem['topicTags']]
        titleSlug = problem['titleSlug']
        link = f"https://leetcode.com/problems/{titleSlug}/"
        
        properties = {
            "Problem name": {
                "title": [{"text": {"content": title}}]
            },
            "Level": {
                "select": {"name": level}
            },
            "Topics": {
                "multi_select": [{"name": topic} for topic in topics]
            },
            "ID": {
                "number": problem_id
            },
            "Link": {
                "url": link
            }
        }
        
        try:
            if problem_id in existing_problems:
                # Already exists - skip it``
                skipped += 1
            else:
                # Create new problem
                url = "https://api.notion.com/v1/pages"
                payload = {
                    "parent": {"database_id": DATABASE_ID},
                    "properties": properties
                }
                response = requests.post(url, json=payload, headers=NOTION_HEADERS)
                response.raise_for_status()
                print(f"✓ Created: {problem_id}. {title}")
                created += 1
                
        except Exception as e:
            print(f"✗ Failed: {title} - {e}")
    
    print(f"\n{'='*60}")
    print(f"✓ Sync complete!")
    print(f"  New problems added: {created}")
    print(f"  Existing (skipped): {skipped}")
    print(f"  Total solved: {len(solved_problems)}")
    print(f"{'='*60}")
def main():
    if not all([NOTION_TOKEN, DATABASE_ID, LEETCODE_SESSION, LEETCODE_CSRF]):
        print("ERROR: Missing credentials in .env file!")
        return
    
    # Wait for internet connection before starting
    if not check_internet_connection():
        print("No internet connection at startup. Waiting for connection...")
        if not wait_for_internet():
            print("Could not establish internet connection. Aborting sync.")
            return
    
    # Step 1: Get existing problems from Notion
    existing_problems = get_existing_problems()
    
    # Step 2: Get solved problems from LeetCode
    solved_problems = get_all_solved_problems()
    
    if not solved_problems:
        print("No solved problems found!")
        return
    
    # Step 3: Sync to Notion (update existing, create new)
    sync_to_notion(existing_problems, solved_problems)

if __name__ == "__main__":
    print("LeetCode → Notion Sync")
    print("=" * 60)
    main()