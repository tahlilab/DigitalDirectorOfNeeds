"""
Intent Classification Module
Uses GPT-4o to classify customer messages into 20 intent categories
"""

import os
import json
from typing import Dict
from openai import AzureOpenAI, OpenAI

class IntentClassifier:
    """Classify customer messages using GPT-4o"""
    
    INTENT_DEFINITIONS = {
        "PAYMENT_INQUIRY": "Questions about payment amounts, due dates, or payment methods",
        "PAYMENT_DISPUTE": "Disputed charges, billing errors, duplicate charges",
        "PAYMENT_SETUP": "Setting up autopay, changing payment methods",
        "CLAIM_SUBMISSION": "How to file or submit a claim",
        "CLAIM_STATUS": "Checking status of existing claim",
        "POLICY_CHANGE": "Modifying coverage, adding dependents, changing plan",
        "POLICY_CANCELLATION": "Requesting to cancel policy",
        "POLICY_REINSTATEMENT": "Reinstating lapsed or cancelled policy",
        "COVERAGE_QUESTION": "Questions about what is/isn't covered",
        "BENEFITS_INQUIRY": "Questions about specific benefits (dental, vision, etc)",
        "PROVIDER_REFERRAL": "Finding in-network doctors or specialists",
        "ACCOUNT_UPDATE": "Changing address, phone, email",
        "DOCUMENT_REQUEST": "Requesting policy documents, ID cards, forms",
        "PREMIUM_QUESTION": "Questions about premium costs or increases",
        "FRAUD_INDICATOR": "Suspicious activity, identity verification issues",
        "COMPLAINT_ESCALATION": "Complaints requiring supervisor/manager",
        "GENERAL_INQUIRY": "General questions about products or services",
        "TECHNICAL_SUPPORT": "Website, app, or login issues",
        "LAPSE_WARNING": "Policy about to lapse, payment reminders",
        "BENEFICIARY_CHANGE": "Updating beneficiary information"
    }
    
    def __init__(self):
        use_azure = os.getenv("USE_AZURE", "true").lower() == "true"
        
        if use_azure:
            self.client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            )
            self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_INTENT", "intent-classifier")
        else:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.deployment_name = "gpt-4o"
        
        self.temperature = 0.3  # Low temperature for consistent classification
        
    def classify(self, message: str, customer_context: Dict = None) -> Dict:
        """
        Classify customer message into one of 20 intent categories
        
        Args:
            message: Customer message text
            customer_context: Optional customer profile data
            
        Returns:
            {
                "intent": "PAYMENT_DISPUTE",
                "confidence": 0.94,
                "reasoning": "Customer mentions duplicate charge...",
                "subcategory": "Duplicate Charge",
                "sentiment": "Frustrated"
            }
        """
        
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(message, customer_context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            # Fallback to mock response if API fails
            print(f"API Error: {e}. Using mock response.")
            return self._mock_classification(message)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with complete intent taxonomy"""
        
        intent_list = "\n".join([
            f"{i+1}. {intent}: {desc}" 
            for i, (intent, desc) in enumerate(self.INTENT_DEFINITIONS.items())
        ])
        
        return f"""You are an expert customer service intent classifier for John Hancock Insurance.

Classify customer messages into exactly ONE of these 20 categories:

{intent_list}

Analyze the message and return a JSON response with this exact structure:
{{
    "intent": "INTENT_NAME",
    "confidence": 0.85,
    "reasoning": "Brief explanation of why this intent was chosen",
    "subcategory": "Specific type (e.g., 'Duplicate Charge', 'Coverage Verification')",
    "sentiment": "Satisfied|Neutral|Frustrated|Angry"
}}

Guidelines:
- Confidence should be 0.0-1.0 (higher = more certain)
- Choose the MOST SPECIFIC intent that matches
- If multiple intents apply, pick the PRIMARY one
- Consider urgency and emotional tone for sentiment
- Be consistent and precise in classification"""
    
    def _build_user_prompt(self, message: str, customer_context: Dict = None) -> str:
        """Build user prompt with message and context"""
        
        prompt = f"Customer Message: {message}\n\n"
        
        if customer_context:
            prompt += f"Customer Context:\n"
            prompt += f"- Name: {customer_context.get('name', 'Unknown')}\n"
            prompt += f"- Policy Type: {customer_context.get('policy_type', 'Unknown')}\n"
            prompt += f"- Policy Status: {customer_context.get('policy_status', 'Unknown')}\n"
            prompt += f"- Recent Interactions: {', '.join(customer_context.get('interaction_history', [])[:3])}\n"
            prompt += f"- Sentiment History: {customer_context.get('sentiment', 'Unknown')}\n"
            prompt += f"- Contact Frequency: {customer_context.get('contact_frequency', 'Unknown')}\n\n"
        
        prompt += "Classify this message and return JSON:"
        return prompt
    
    def _mock_classification(self, message: str) -> Dict:
        """Fallback mock classification based on keywords"""
        
        message_lower = message.lower()
        
        # Simple keyword matching
        if any(word in message_lower for word in ["charged twice", "duplicate", "double charge"]):
            intent = "PAYMENT_DISPUTE"
            subcategory = "Duplicate Charge"
            confidence = 0.94
        elif any(word in message_lower for word in ["claim status", "submitted claim", "claim"]):
            intent = "CLAIM_STATUS"
            subcategory = "Status Check"
            confidence = 0.91
        elif any(word in message_lower for word in ["doctor", "specialist", "provider", "network"]):
            intent = "PROVIDER_REFERRAL"
            subcategory = "Find Provider"
            confidence = 0.88
        elif any(word in message_lower for word in ["urgent", "immediately", "wire", "cash out"]):
            intent = "FRAUD_INDICATOR"
            subcategory = "Urgent Request"
            confidence = 0.85
        elif any(word in message_lower for word in ["third time", "supervisor", "manager", "complaint"]):
            intent = "COMPLAINT_ESCALATION"
            subcategory = "Escalation Request"
            confidence = 0.92
        elif any(word in message_lower for word in ["cover", "coverage"]):
            intent = "COVERAGE_QUESTION"
            subcategory = "Coverage Verification"
            confidence = 0.89
        else:
            intent = "GENERAL_INQUIRY"
            subcategory = "General Question"
            confidence = 0.75
        
        sentiment = "Frustrated" if any(word in message_lower for word in ["third time", "no one", "haven't heard"]) else "Neutral"
        
        return {
            "intent": intent,
            "confidence": confidence,
            "reasoning": f"Message contains keywords related to {intent.replace('_', ' ').lower()}",
            "subcategory": subcategory,
            "sentiment": sentiment
        }

# Initialize global classifier
classifier = IntentClassifier()
