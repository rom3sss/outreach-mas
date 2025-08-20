#!/usr/bin/env python3
"""
Multi-Agent Email Outreach System
Main entry point for the application.
"""

import logging
import sys
from datetime import datetime

from agents.orchestrator import OrchestratorAgent
from config import config


def setup_logging() -> None:
    """Configure logging for the application."""
    # Create logs directory if it doesn't exist
    import os
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # File handler for detailed logs
    file_handler = logging.FileHandler(
        f"logs/outreach_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Console handler for important messages
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    ))
    
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[file_handler, console_handler]
    )


def main() -> None:
    """Main function to run the multi-agent email outreach system."""
    try:
        # Setup logging
        setup_logging()
        
        # Log startup
        logging.info("Starting Multi-Agent Email Outreach System")
        logging.info(f"Configuration loaded successfully")
        
        # Instantiate the orchestrator
        orchestrator = OrchestratorAgent()
        
        # Run the main workflow
        orchestrator.run_workflow()
        
        logging.info("Application completed successfully")
        
    except Exception as e:
        logging.error(f"Application failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()