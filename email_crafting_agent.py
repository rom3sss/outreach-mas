# agents/email_crafting_agent.py


import os
import google.generativeai as genai


class EmailCraftingAgent:
    def __init__(self):
        # Configure the Gemini API client
        try:
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            print(f"Error configuring Gemini API: {e}")
            self.model = None


        self.your_name = os.getenv("YOUR_NAME")
        self.your_title = os.getenv("YOUR_TITLE")
        self.portfolio_link = os.getenv("PORTFOLIO_LINK")


    def draft_initial_email(self, lead: dict) -> dict:
        """
        Drafts the initial personalized email using a strict template.
        (This method does not require an LLM and remains unchanged).
        """
        subject = f"A Partnership in Storytelling for {lead['company']}"
        
        body_template = f"""
Hi {lead['firstName']},


I'm {self.your_name} from Reason GTMC. We partner with creators and brands like yours to tell powerful stories through cinematic video.


Our team handles every aspect of production, from initial concept and creative strategy to the final cut, using the industry's best equipment to bring ambitious ideas to life. We believe the best work comes from true collaboration, where we serve as the creative and technical engine for your vision. This means we start by diving deep into your brand's objectives to ensure we're perfectly aligned.


Our in-house process covers everything: storyboarding, scripting, on-location shooting, and meticulous post-production, including cinematic editing, color grading, and sound design.


Whether it's a documentary that captures your brand's ethos, a high-energy brand campaign, or a polished podcast series, we build a process around your goals to ensure the final product is both beautiful and impactful.


Here's a glimpse into our style: {self.portfolio_link}


If you're looking for a dedicated partner for your next project, we'd love to schedule a brief call to learn more about your vision.


All the best,


{self.your_name}
{self.your_title}
Reason GTM&C
"""
        return {"subject": subject.strip(), "body": body_template.strip()}


    def draft_follow_up_email(self, lead: dict) -> dict:
        """
        Uses Google's Gemini model to draft a concise follow-up email.
        """
        if not self.model:
            print("Gemini model not initialized. Cannot draft follow-up.")
            return None


        prompt = f"""
        You are an expert copywriter specializing in friendly, professional, and non-pushy follow-up emails.
        Your goal is to gently remind the recipient of the previous email without being annoying.
        
        Draft a concise, friendly follow-up email for the following lead:
        - Name: {lead['firstName']}
        - Company: {lead['company']}
        
        Instructions:
        1. Keep the entire email under 60 words.
        2. Reference the quality of our work or our showreel.
        3. Gently "bump" the original idea of a potential collaboration.
        4. Do not include a subject line or any introduction like "Here's the draft:". Just provide the raw body text.
        """


        try:
            response = self.model.generate_content(prompt)
            follow_up_body = response.text.strip()
            subject = f"Re: A Partnership in Storytelling for {lead['company']}"


            full_body = f"""
{follow_up_body}


All the best,


{self.your_name}
"""
            return {"subject": subject, "body": full_body.strip()}


        except Exception as e:
            print(f"Error generating follow-up with Gemini: {e}")
            return None