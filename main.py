# main.py


from dotenv import load_dotenv
from agents.orchestrator import OrchestratorAgent


def main():
    """
    Main function to run the multi-agent email outreach system.
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Instantiate the orchestrator
    orchestrator = OrchestratorAgent()
    
    # Run the main workflow
    orchestrator.run_workflow()


if __name__ == "__main__":
    main()