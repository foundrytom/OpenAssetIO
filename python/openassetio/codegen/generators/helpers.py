"""
Utility functions to help code generation templates.
"""
import re

def toUpperCamelAlnum(string):
    """
    Reformats a string to UpperCamelCase stripping out any non
    alpha-numeric characters.

    eg: "ThisIs! a complex-string" -> "ThisIsAComplexString"
    """
    words = re.split('([^a-zA-Z0-9]|[A-Z](?:[a-z]+)|[A-Z](?=[A-z]|$))', string)
    legalWords = [word.capitalize() for word in words if (word and word.isalnum())]
    return ''.join(legalWords)

def toLowerCamelAlnum(string):
    """
    Reformats a string to lowerCamelCase stripping out any non
    alpha-numeric characters.

    eg: "This is a complex-string" -> "thisIsAComplexString"
    """
    upper = toUpperCamelAlnum(string)
    return upper[0].lower() + upper[1:]
