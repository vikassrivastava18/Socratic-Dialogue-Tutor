from typing import cast

from app.utils.schemas import CodeListSchema, QuizSchema
from app.utils.open_ai import llm


def create_coding_problems(content: str) -> CodeListSchema:
    prompt = f"""
    You are a code chef. Use the content to create 5 coding problems. 
    Keep the problem level to be easy for first 3 and medium for remaining two.
    Use the content provided only.

    Content: {content}

    Sample: 
    Question: Write a Python function to validate if an email address is valid. An email is considered valid if it contains an '@' symbol. Use the `re` module to implement this.
    Code: import re

    def is_valid_email(email):
        raise NotImplementedError


    print(is_valid_email('malan.harvard.edu'))
    print(is_valid_email('malan@harvard'))

    Answer: Invalid\n Valid
    """
    structured_llm = llm.with_structured_output(CodeListSchema)
    messages = [
        {
            "role": "system",
            "content": prompt
        }
    ]

    response = structured_llm.invoke(messages)
    return cast(CodeListSchema, response)


def create_quizzes(content: str) -> QuizSchema:
    prompt = f"""
    You are a quiz master. Use the content of a chapter to create quizzes that help students in their study.
    For MCQ, only one option should be correct.
    Return the response in the format specified.    

    Content: {content}
    """
    structured_llm = llm.with_structured_output(QuizSchema)
    messages = [
        {
            "role": "system",
            "content": prompt
        }
    ]

    response = structured_llm.invoke(messages)
    return cast(QuizSchema, response)