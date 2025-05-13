#!/usr/bin/env python
import sys
from .crew import CompanyDescriptionRetrievalAutomationCrew

# This main file is intended to be a way for your to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

import os   
from dotenv import load_dotenv

load_dotenv()

def run(company_name=None):
    """
    Run the crew.
    
    Args:
        company_name (str): Name of the company to retrieve description for
    """
    if not company_name:
        raise ValueError("company_name must be provided")
        
    inputs = {
        'company_name': company_name
    }
    return CompanyDescriptionRetrievalAutomationCrew().crew().kickoff(inputs=inputs)

def train(n_iterations=None, filename=None, company_name=None):
    """
    Train the crew for a given number of iterations.
    """
    if not all([n_iterations, filename, company_name]):
        raise ValueError("n_iterations, filename and company_name must be provided")
        
    inputs = {
        'company_name': company_name
    }
    try:
        CompanyDescriptionRetrievalAutomationCrew().crew().train(n_iterations=n_iterations, filename=filename, inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay(task_id=None):
    """
    Replay the crew execution from a specific task.
    """
    if not task_id:
        raise ValueError("task_id must be provided")
        
    try:
        CompanyDescriptionRetrievalAutomationCrew().crew().replay(task_id=task_id)
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test(n_iterations=None, model_name=None, company_name=None):
    """
    Test the crew execution and returns the results.
    """
    if not all([n_iterations, model_name, company_name]):
        raise ValueError("n_iterations, model_name and company_name must be provided")
        
    inputs = {
        'company_name': company_name
    }
    try:
        CompanyDescriptionRetrievalAutomationCrew().crew().test(n_iterations=n_iterations, openai_model_name=model_name, inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: main.py <command> [<args>]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "run":
        if len(sys.argv) != 3:
            print("Usage: main.py run <company_name>")
            sys.exit(1)
        run(company_name=sys.argv[2])
    elif command == "train":
        if len(sys.argv) != 5:
            print("Usage: main.py train <n_iterations> <filename> <company_name>")
            sys.exit(1)
        train(n_iterations=int(sys.argv[2]), filename=sys.argv[3], company_name=sys.argv[4])
    elif command == "replay":
        if len(sys.argv) != 3:
            print("Usage: main.py replay <task_id>")
            sys.exit(1)
        replay(task_id=sys.argv[2])
    elif command == "test":
        if len(sys.argv) != 5:
            print("Usage: main.py test <n_iterations> <model_name> <company_name>")
            sys.exit(1)
        test(n_iterations=int(sys.argv[2]), model_name=sys.argv[3], company_name=sys.argv[4])
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
