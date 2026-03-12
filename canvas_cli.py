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
        response.raise_for_status() # Check for HTTP errors
        data.extend(response.json())

        # Follow pagination 'next' links if they exist
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
    print("\nFetching your active courses...\n" + "-"*30)
    # Only get active courses where you are a student
    url = f"{BASE_URL}/courses?enrollment_state=active"
    courses = fetch_paginated_data(url)

    if not courses:
        print("No active courses found.")
        return

    for course in courses:
        # Some Canvas course objects don't have a name, so we use get() to avoid KeyErrors
        course_id = course.get('id')
        name = course.get('name', 'Unnamed Course')
        if name != 'Unnamed Course':
            print(f"ID: {course_id:<10} | Name: {name}")
    print("-" * 30)

def list_assignments(course_id):
    """Endpoint 2: Fetch and display assignments for a specific course."""
    print(f"\nFetching assignments for Course ID: {course_id}...\n" + "-"*30)
    url = f"{BASE_URL}/courses/{course_id}/assignments"
    assignments = fetch_paginated_data(url)

    if not assignments:
        print("No assignments found or invalid course ID.")
        return

    for assign in assignments:
        name = assign.get('name', 'Unknown')
        due_at = assign.get('due_at', 'No Due Date')
        # Simple formatting for the terminal
        print(f"Due: {due_at[:10] if due_at else 'None':<12} | Assignment: {name}")
    print("-" * 30)

def main():
    # Setup CLI argument parsing
    parser = argparse.ArgumentParser(description="A CLI tool to track Canvas Courses and Assignments.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: courses
    subparsers.add_parser("courses", help="List all active Canvas courses and their IDs")

    # Command: assignments
    assign_parser = subparsers.add_parser("assignments", help="List assignments for a specific course")
    assign_parser.add_argument("course_id", type=int, help="The ID of the course to fetch assignments for")

    args = parser.parse_args()

    # Route to the correct function based on user input
    if args.command == "courses":
        list_courses()
    elif args.command == "assignments":
        list_assignments(args.course_id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()