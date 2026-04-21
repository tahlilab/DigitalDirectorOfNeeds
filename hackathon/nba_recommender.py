"""
Next-Best-Action Recommender Module
Uses GPT-4o to recommend actions for agents based on intent and context
"""

import os
import json
from typing import Dict, List
from openai import AzureOpenAI, OpenAI

class NBARecommender:
    """Recommend next-best-actions for contact center agents"""
    
    def __init__(self):
        use_azure = os.getenv("USE_AZURE", "true").lower() == "true"
        
        if use_azure:
            self.client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            )
            self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NBA", "nba-recommender")
        else:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.deployment_name = "gpt-4o"
            
        self.temperature = 0.7  # Higher temperature for creative recommendations
        
    def recommend(self, intent: str, customer_context: Dict, confidence: float) -> Dict:
        """
        Generate next-best-action recommendations
        
        Args:
            intent: Classified intent category
            customer_context: Customer profile data
            confidence: Classification confidence score
            
        Returns:
            {
                "primary_actions": [...],
                "follow_up_actions": [...],
                "escalation_required": bool,
                "estimated_resolution_time": str,
                "agent_script": str,
                "knowledge_articles": [...]
            }
        """
        
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(intent, customer_context, confidence)
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            # Fallback to mock recommendations
            print(f"API Error: {e}. Using mock recommendations.")
            return self._mock_recommendations(intent, customer_context)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for NBA generation"""
        
        return """You are an expert contact center operations consultant for John Hancock Insurance.

Your role is to recommend the BEST next actions for agents to resolve customer issues quickly and effectively.

Consider:
- Customer satisfaction and retention
- First-call resolution
- SLA compliance
- Cross-sell/upsell opportunities (when appropriate)
- Preventing repeat calls
- Fraud risk mitigation

Return JSON with this structure:
{
    "primary_actions": [
        {
            "action": "Specific action to take immediately",
            "priority": "IMMEDIATE|HIGH|MEDIUM",
            "estimated_time": "X minutes",
            "details": "Step-by-step guidance"
        }
    ],
    "follow_up_actions": [
        {
            "action": "Follow-up action",
            "priority": "HIGH|MEDIUM|LOW",
            "estimated_time": "X minutes",
            "when": "After primary action | Within 24 hours | etc"
        }
    ],
    "escalation_required": false,
    "escalation_reason": "Why escalation needed (if true)",
    "estimated_resolution_time": "15-20 minutes",
    "agent_script": "Suggested opening statement to customer",
    "knowledge_articles": ["KB-1234: Article title", "KB-5678: Article title"],
    "potential_upsell": "Relevant product/service (if applicable)"
}

Prioritize actions that:
1. Resolve the immediate customer need
2. Prevent future contacts about the same issue  
3. Demonstrate empathy and professionalism
4. Meet SLA requirements"""
    
    def _build_user_prompt(self, intent: str, customer_context: Dict, confidence: float) -> str:
        """Build user prompt with intent and context"""
        
        prompt = f"Intent Detected: {intent}\n"
        prompt += f"Classification Confidence: {confidence:.2%}\n\n"
        
        prompt += "Customer Profile:\n"
        prompt += f"- Name: {customer_context.get('name', 'Unknown')}\n"
        prompt += f"- Policy: {customer_context.get('policy_type', 'Unknown')}\n"
        prompt += f"- Status: {customer_context.get('policy_status', 'Active')}\n"
        prompt += f"- Lifetime Value: ${customer_context.get('lifetime_value', 0):,}\n"
        prompt += f"- Sentiment: {customer_context.get('sentiment', 'Neutral')}\n"
        prompt += f"- Contact Frequency: {customer_context.get('contact_frequency', 'Normal')}\n"
        prompt += f"- Payment Status: {customer_context.get('payment_status', 'Current')}\n"
        
        if customer_context.get('interaction_history'):
            prompt += f"- Recent Interactions:\n"
            for interaction in customer_context['interaction_history'][:3]:
                prompt += f"  • {interaction}\n"
        
        prompt += "\nRecommend the best next actions for the agent. Return JSON:"
        return prompt
    
    def _mock_recommendations(self, intent: str, customer_context: Dict) -> Dict:
        """Fallback mock recommendations based on intent"""
        
        # Intent-specific mock recommendations
        recommendations_map = {
            "PAYMENT_DISPUTE": {
                "primary_actions": [
                    {
                        "action": "Review payment transaction history in billing system",
                        "priority": "IMMEDIATE",
                        "estimated_time": "2-3 minutes",
                        "details": "Check last 3 months for duplicate charges"
                    },
                    {
                        "action": "Issue credit if duplicate charge confirmed",
                        "priority": "IMMEDIATE",
                        "estimated_time": "5 minutes",
                        "details": "Process refund to original payment method"
                    }
                ],
                "follow_up_actions": [
                    {
                        "action": "Call customer within 24 hours to confirm credit posted",
                        "priority": "HIGH",
                        "estimated_time": "10 minutes",
                        "when": "Within 24 hours"
                    }
                ],
                "escalation_required": False,
                "agent_script": "I understand you were charged twice for your premium. I apologize for this error. Let me review your payment history right now to resolve this.",
                "knowledge_articles": [
                    "KB-1234: Processing Billing Disputes",
                    "KB-5678: Issuing Credits for Duplicate Charges"
                ]
            },
            "CLAIM_STATUS": {
                "primary_actions": [
                    {
                        "action": "Look up claim number in claims system",
                        "priority": "IMMEDIATE",
                        "estimated_time": "1-2 minutes",
                        "details": "Search by customer ID or date submitted"
                    },
                    {
                        "action": "Provide detailed status update to customer",
                        "priority": "IMMEDIATE",
                        "estimated_time": "3 minutes",
                        "details": "Include current stage, expected timeline, any missing documents"
                    }
                ],
                "follow_up_actions": [
                    {
                        "action": "Set up claim status alerts for customer",
                        "priority": "MEDIUM",
                        "estimated_time": "2 minutes",
                        "when": "During call"
                    }
                ],
                "escalation_required": False,
                "agent_script": "I'll check the status of your claim right now. Can you confirm the date you submitted it?",
                "knowledge_articles": [
                    "KB-2345: Claim Processing Timelines",
                    "KB-6789: Setting Up Claim Alerts"
                ]
            },
            "FRAUD_INDICATOR": {
                "primary_actions": [
                    {
                        "action": "Verify customer identity with additional security questions",
                        "priority": "IMMEDIATE",
                        "estimated_time": "5 minutes",
                        "details": "Ask policy number, DOB, last 4 SSN, recent claim details"
                    },
                    {
                        "action": "Flag account for fraud review",
                        "priority": "IMMEDIATE",
                        "estimated_time": "2 minutes",
                        "details": "Submit fraud alert to security team"
                    }
                ],
                "follow_up_actions": [
                    {
                        "action": "Do NOT process transaction until fraud team clears",
                        "priority": "HIGH",
                        "estimated_time": "N/A",
                        "when": "Immediately"
                    }
                ],
                "escalation_required": True,
                "escalation_reason": "High fraud risk detected - requires security team review",
                "agent_script": "I'll be happy to help you with that. First, I need to verify some information for your security.",
                "knowledge_articles": [
                    "KB-9999: Fraud Detection Procedures",
                    "KB-8888: Identity Verification Steps"
                ]
            }
        }
        
        # Return intent-specific or generic recommendations
        if intent in recommendations_map:
            result = recommendations_map[intent]
        else:
            result = {
                "primary_actions": [
                    {
                        "action": f"Address customer's {intent.replace('_', ' ').lower()} request",
                        "priority": "IMMEDIATE",
                        "estimated_time": "5-10 minutes",
                        "details": "Review account and provide resolution"
                    }
                ],
                "follow_up_actions": [],
                "escalation_required": False,
                "agent_script": "I understand your concern. Let me look into this for you right away.",
                "knowledge_articles": [f"KB-0000: Handling {intent.replace('_', ' ').title()}"]
            }
        
        # Add estimated resolution time
        result["estimated_resolution_time"] = "15-20 minutes"
        
        return result

# Initialize global recommender
recommender = NBARecommender()
