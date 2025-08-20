"""Email Crafting Agent with improved error handling and type hints."""

import logging
from typing import Dict, Optional
import google.generativeai as genai

from config import config


class EmailCraftingAgent:
    """Agent responsible for crafting personalized emails using templates and LLM."""
    
    def __init__(self):
        """Initialize the Email Crafting Agent."""
        try:
            genai.configure(api_key=config.google_api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            logging.info("Successfully initialized Gemini API")
        except Exception as e:
            logging.error(f"Error configuring Gemini API: {e}")
            self.model = None

    def draft_initial_email(self, lead: Dict[str, str]) -> Dict[str, str]:
        """
        Draft the initial personalized email using a consistent template.
        
        Args:
            lead: Dictionary containing lead information
            
        Returns:
            Dictionary with 'subject' and 'body' keys
        """
        try:
            subject = f"A Partnership in Storytelling for {lead['company']}"
            
            body_template = f"""Hi {lead['firstName']},

I'm {config.your_name} from Reason GTMC. We partner with creators and brands like yours to tell powerful stories through cinematic video.

Our team handles every aspect of production, from initial concept and creative strategy to the final cut, using the industry's best equipment to bring ambitious ideas to life. We believe the best work comes from true collaboration, where we serve as the creative and technical engine for your vision. This means we start by diving deep into your brand's objectives to ensure we're perfectly aligned.

Our in-house process covers everything: storyboarding, scripting, on-location shooting, and meticulous post-production, including cinematic editing, color grading, and sound design.

Whether it's a documentary that captures your brand's ethos, a high-energy brand campaign, or a polished podcast series, we build a process around your goals to ensure the final product is both beautiful and impactful.

Here's a glimpse into our style: {config.portfolio_link}

If you're looking for a dedicated partner for your next project, we'd love to schedule a brief call to learn more about your vision.

All the best,

{config.your_name}
{config.your_title}
Reason GTM&C"""
            
            logging.info(f"Drafted initial email for {lead['email']}")
            return {"subject": subject.strip(), "body": body_template.strip()}
            
        except KeyError as e:
            logging.error(f"Missing required lead field: {e}")
            return {"subject": "Error", "body": "Error drafting email"}
        except Exception as e:
            logging.error(f"Unexpected error drafting initial email: {e}")
            return {"subject": "Error", "body": "Error drafting email"}

    def draft_follow_up_email(self, lead: Dict[str, str]) -> Optional[Dict[str, str]]:
        """
        Use Google's Gemini model to draft a concise follow-up email.
        
        Args:
            lead: Dictionary containing lead information
            
        Returns:
            Dictionary with 'subject' and 'body' keys, or None if failed
        """
        if not self.model:
            logging.error("Gemini model not initialized. Cannot draft follow-up")
            return None

        try:
            prompt = f"""You are an expert copywriter specializing in friendly, professional, and non-pushy follow-up emails.
Your goal is to gently remind the recipient of the previous email without being annoying.

Draft a concise, friendly follow-up email for the following lead:
- Name: {lead['firstName']}
- Company: {lead['company']}

Instructions:
1. Keep the entire email under 60 words.
2. Reference the quality of our work or our showreel.
3. Gently "bump" the original idea of a potential collaboration.
4. Do not include a subject line or any introduction like "Here's the draft:". Just provide the raw body text."""

            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                logging.error("Empty response from Gemini API")
                return None
                
            follow_up_body = response.text.strip()
            subject = f"Re: A Partnership in Storytelling for {lead['company']}"

            full_body = f"""{follow_up_body}

All the best,

{config.your_name}"""

            logging.info(f"Drafted follow-up email for {lead['email']}")
            return {"subject": subject, "body": full_body.strip()}

        except Exception as e:
            logging.error(f"Error generating follow-up with Gemini: {e}")
            return None
