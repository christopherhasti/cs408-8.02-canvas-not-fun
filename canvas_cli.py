import os
import argparse
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("CANVAS_API_TOKEN")
BASE_URL = "https://boisestatecanvas.instructure.com/api/v1"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

def fetch_paginated_data(url):
    """Fetches data from Canvas, handling pagination automatically."""
    if not TOKEN:
        print("Error: CANVAS_API_TOKEN is missing. Please check your .env file.")
        return []

    data = []
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data.extend(response.json())

        while 'next' in response.links:
            next_url = response.links['next']['url']
            response = requests.get(next_url, headers=HEADERS)
            response.raise_for_status()
            data.extend(response.json())
            
    except requests.exceptions.RequestException as e:
        print(f"Network or API Error: {e}")
    
    return data

def list_courses():
    """Endpoint 1: Fetch and display active courses."""
    print("\nFetching your active courses...\n" + "-"*40)
    url = f"{BASE_URL}/courses?enrollment_state=active"
    courses = fetch_paginated_data(url)

    if not courses:
        print("No active courses found.")
        return

    for course in courses:
        course_id = course.get('id')
        name = course.get('name', 'Unnamed Course')
        if name != 'Unnamed Course':
            print(f"ID: {course_id:<10} | Name: {name}")
    print("-" * 40)

def list_assignments(course_id):
    """Endpoint 2: Fetch and display assignments for a specific course."""
    print(f"\nFetching assignments for Course ID: {course_id}...\n" + "-"*40)
    url = f"{BASE_URL}/courses/{course_id}/assignments"
    assignments = fetch_paginated_data(url)

    if not assignments:
        print("No assignments found or invalid course ID.")
        return

    for assign in assignments:
        assign_id = assign.get('id', 'Unknown')
        name = assign.get('name', 'Unknown')
        due_at = assign.get('due_at', 'No Due Date')
        print(f"Assign ID: {assign_id:<8} | Due: {due_at[:10] if due_at else 'None':<10} | Name: {name}")
    print("-" * 40)

def list_todos():
    """Endpoint 3: Fetch global user TODO items."""
    print("\nFetching your Canvas TODO list...\n" + "-"*40)
    url = f"{BASE_URL}/users/self/todo"
    todos = fetch_paginated_data(url)

    if not todos:
        print("You're all caught up! No TODOs found.")
        return

    for item in todos:
        ignore_url = item.get('ignore', 'Unknown')
        context = item.get('context_type', 'Unknown')
        print(f"Type: {context:<10} | URL: {ignore_url}")
    print("-" * 40)

def list_announcements(course_id):
    """Endpoint 4: Fetch announcements for a specific course."""
    print(f"\nFetching announcements for Course ID: {course_id}...\n" + "-"*40)
    url = f"{BASE_URL}/announcements?context_codes[]=course_{course_id}"
    announcements = fetch_paginated_data(url)

    if not announcements:
        print("No announcements found for this course.")
        return

    for ann in announcements:
        title = ann.get('title', 'No Title')
        posted_at = ann.get('posted_at', 'Unknown Date')
        print(f"Posted: {posted_at[:10] if posted_at else 'None':<10} | Title: {title}")
    print("-" * 40)

def submit_assignment(course_id, assignment_id, github_url):
    """Endpoint 5: POST a URL submission to an assignment."""
    print(f"\nAttempting to submit {github_url} to Assignment {assignment_id}...\n" + "-"*40)
    url = f"{BASE_URL}/courses/{course_id}/assignments/{assignment_id}/submissions"
    
    # Payload required by Canvas for a URL submission
    payload = {
        "submission[submission_type]": "online_url",
        "submission[url]": github_url
    }

    try:
        response = requests.post(url, headers=HEADERS, data=payload)
        response.raise_for_status()
        print("Success! Your assignment has been submitted.")
    except requests.exceptions.RequestException as e:
        print(f"Submission Failed: {e}")
        if response.content:
            print(f"Canvas Response: {response.json()}")
    print("-" * 40)

def main():
    parser = argparse.ArgumentParser(description="A CLI tool to track and manage Canvas.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: courses
    subparsers.add_parser("courses", help="List all active Canvas courses and their IDs")
    
    # Command: todos
    subparsers.add_parser("todos", help="List your global Canvas TODO items")

    # Command: assignments
    assign_parser = subparsers.add_parser("assignments", help="List assignments for a specific course")
    assign_parser.add_argument("course_id", type=int, help="The ID of the course")

    # Command: announcements
    ann_parser = subparsers.add_parser("announcements", help="List announcements for a specific course")
    ann_parser.add_argument("course_id", type=int, help="The ID of the course")

    # Command: submit
    submit_parser = subparsers.add_parser("submit", help="Submit a URL to a specific assignment")
    submit_parser.add_argument("course_id", type=int, help="The ID of the course")
    submit_parser.add_argument("assignment_id", type=int, help="The ID of the assignment")
    submit_parser.add_argument("url", type=str, help="The URL to submit (e.g., your GitHub repo)")

    args = parser.parse_args()

    if args.command == "courses":
        list_courses()
    elif args.command == "todos":
        list_todos()
    elif args.command == "assignments":
        list_assignments(args.course_id)
    elif args.command == "announcements":
        list_announcements(args.course_id)
    elif args.command == "submit":
        submit_assignment(args.course_id, args.assignment_id, args.url)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()