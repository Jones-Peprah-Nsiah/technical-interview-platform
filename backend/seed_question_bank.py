"""Seeds the shared question bank with a starter set of classic,
generically-worded algorithm problems. Safe to call repeatedly — skips any
title that already exists. Called automatically on backend startup (see
main.py) so it runs the same way in every environment, and can also be run
standalone: python3 seed_question_bank.py
"""
from database import SessionLocal, Base, engine
from models import QuestionBankItem


QUESTIONS = [
    # Easy
    {
        "title": "Two Sum",
        "description": (
            "Given an array of integers and a target value, return the "
            "indices of the two numbers that add up to the target."
        ),
        "difficulty": "easy",
    },
    {
        "title": "Valid Parentheses",
        "description": (
            "Given a string containing just the characters "
            "'(', ')', '{', '}', '[' and ']', determine if the input "
            "string is valid — every opening bracket must be closed by "
            "the same type of bracket, in the correct order."
        ),
        "difficulty": "easy",
    },
    {
        "title": "Reverse a String",
        "description": "Write a function that reverses a string in place.",
        "difficulty": "easy",
    },
    {
        "title": "FizzBuzz",
        "description": (
            "Print the numbers from 1 to n. For multiples of 3 print "
            "'Fizz', for multiples of 5 print 'Buzz', and for multiples "
            "of both print 'FizzBuzz'."
        ),
        "difficulty": "easy",
    },
    {
        "title": "Merge Two Sorted Lists",
        "description": (
            "Merge two sorted linked lists and return it as one sorted list."
        ),
        "difficulty": "easy",
    },
    {
        "title": "Binary Search",
        "description": (
            "Given a sorted array of integers and a target value, "
            "implement binary search to return the index of the target, "
            "or -1 if it isn't present."
        ),
        "difficulty": "easy",
    },
    # Medium
    {
        "title": "Reverse a Linked List",
        "description": (
            "Given the head of a singly linked list, reverse it in place "
            "and return the new head."
        ),
        "difficulty": "medium",
    },
    {
        "title": "Longest Substring Without Repeating Characters",
        "description": (
            "Given a string, find the length of the longest substring "
            "that doesn't contain any repeating characters."
        ),
        "difficulty": "medium",
    },
    {
        "title": "Binary Tree Level Order Traversal",
        "description": (
            "Given the root of a binary tree, return the level order "
            "traversal of its node values (left to right, level by level)."
        ),
        "difficulty": "medium",
    },
    {
        "title": "Group Anagrams",
        "description": (
            "Given an array of strings, group the anagrams together."
        ),
        "difficulty": "medium",
    },
    {
        "title": "Validate Binary Search Tree",
        "description": (
            "Given the root of a binary tree, determine if it is a valid "
            "binary search tree."
        ),
        "difficulty": "medium",
    },
    {
        "title": "Kth Largest Element",
        "description": (
            "Find the kth largest element in an unsorted array."
        ),
        "difficulty": "medium",
    },
    {
        "title": "Number of Islands",
        "description": (
            "Given a 2D grid of '1's (land) and '0's (water), count the "
            "number of islands. An island is surrounded by water and "
            "formed by connecting adjacent lands horizontally or "
            "vertically."
        ),
        "difficulty": "medium",
    },
    {
        "title": "Course Schedule",
        "description": (
            "Given a number of courses and a list of prerequisite pairs, "
            "determine whether it's possible to finish all courses "
            "(i.e., the prerequisite graph has no cycles)."
        ),
        "difficulty": "medium",
    },
    # Hard
    {
        "title": "Merge k Sorted Lists",
        "description": (
            "Merge k sorted linked lists into one sorted linked list."
        ),
        "difficulty": "hard",
    },
    {
        "title": "Longest Increasing Subsequence",
        "description": (
            "Given an integer array, return the length of the longest "
            "strictly increasing subsequence."
        ),
        "difficulty": "hard",
    },
    {
        "title": "Trapping Rain Water",
        "description": (
            "Given n non-negative integers representing an elevation map "
            "where the width of each bar is 1, compute how much water it "
            "can trap after raining."
        ),
        "difficulty": "hard",
    },
    {
        "title": "Median of Two Sorted Arrays",
        "description": (
            "Given two sorted arrays, find the median of the two sorted "
            "arrays combined, in O(log(min(m, n))) time."
        ),
        "difficulty": "hard",
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        existing_titles = {
            item.title for item in db.query(QuestionBankItem).all()
        }

        added = 0

        for question in QUESTIONS:
            if question["title"] in existing_titles:
                continue

            db.add(QuestionBankItem(**question))
            added += 1

        db.commit()
        print(f"Seeded {added} new question(s); {len(QUESTIONS) - added} already existed.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
