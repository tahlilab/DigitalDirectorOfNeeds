"""
Fraud Detection Module
Analyzes messages and customer context for fraud patterns
"""

import os
import json
from typing import Dict, List
from openai import AzureOpenAI, OpenAI

class FraudDetector:
    """Detect fraud patterns using multi-layer analysis"""
    
    FRAUD_PATTERNS = {
        "urgency": ["urgent", "immediately", "right now", "asap", "today", "emergency"],
        "financial_requests": ["cash out", "wire", "transfer", "withdraw", "payout"],
        "account_changes": ["change bank", "new account", "update routing", "different account"],
        "identity_issues": ["can't verify", "forgot", "don't remember", "lost"],
        "unusual_requests": ["send to", "mail to", "new address", "different address"]
    }
    
    def __init__(self):
        use_azure = os.getenv("USE_AZURE", "true").lower() == "true"
        
        if use_azure:
            self.client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            )
            self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_FRAUD", "fraud-analyzer")
        else:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.deployment_name = "gpt-4o"
            
        self.temperature = 0.2  # Very low temperature for consistent fraud detection
        
    def analyze(self, message: str, intent: str, customer_context: Dict) -> Dict:
        """
        Analyze message for fraud indicators
        
        Args:
            message: Customer message text
            intent: Classified intent
            customer_context: Customer profile and history
            
        Returns:
            {
                "fraud_score": 0-100,
                "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
                "indicators": [...],
                "recommended_actions": [...],
                "verification_required": bool
            }
        """
        
        # Layer 1: Pattern matching
        pattern_score = self._pattern_matching(message, customer_context)
        
        # Layer 2: LLM-based analysis
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(message, intent, customer_context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=600,
                response_format={"type": "json_object"}
            )
            
            llm_result = json.loads(response.choices[0].message.content)
            
            # Combine pattern score with LLM assessment
            final_score = int((pattern_score + llm_result.get("fraud_score", 0)) / 2)
            
            return {
                "fraud_score": final_score,
                "risk_level": self._get_risk_level(final_score),
                "indicators": llm_result.get("indicators", []),
                "recommended_actions": self._get_fraud_actions(final_score),
                "verification_required": final_score > 50,
                "suspicious_patterns": llm_result.get("suspicious_patterns", []),
                "reasoning": llm_result.get("reasoning", "")
            }
            
        except Exception as e:
            # Fallback to pattern-only analysis
            print(f"API Error: {e}. Using pattern-based analysis.")
            return self._mock_analysis(message, pattern_score, customer_context)
    
    def _pattern_matching(self, message: str, customer_context: Dict) -> int:
        """Calculate fraud score based on pattern matching"""
        
        score = 0
        message_lower = message.lower()
        
        # Check for urgency language (+25 points)
        if any(word in message_lower for word in self.FRAUD_PATTERNS["urgency"]):
            score += 25
        
        # Check for financial requests (+30 points)
        if any(word in message_lower for word in self.FRAUD_PATTERNS["financial_requests"]):
            score += 30
        
        # Check for account changes (+20 points)
        if any(word in message_lower for word in self.FRAUD_PATTERNS["account_changes"]):
            score += 20
        
        # Check for identity issues (+15 points)
        if any(word in message_lower for word in self.FRAUD_PATTERNS["identity_issues"]):
            score += 15
        
        # Check customer context
        account_age = customer_context.get("account_age_days", 365)
        if account_age < 90:  # New account (+15 points)
            score += 15
        
        # Baseline fraud risk from profile
        baseline_risk = customer_context.get("fraud_risk_score", 0)
        score = int((score + baseline_risk) / 2)
        
        return min(score, 100)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for fraud analysis"""
        
        return """You are an expert fraud detection specialist for insurance companies.

Analyze customer interactions for potential fraud indicators including:

RED FLAGS:
- Urgency language ("need it now", "emergency", "immediately")
- Unusual financial requests (policy loans, cash withdrawals)
- Recent account changes before transaction requests
- Inconsistent information with profile
- Multiple failed verification attempts
- Requests to change beneficiary + cash out together
- High-value transactions on new accounts
- Suspicious timing (just after policy issue, before lapse)

Return JSON:
{
    "fraud_score": 0-100,
    "indicators": ["Specific red flag found", "Another indicator"],
    "suspicious_patterns": ["Pattern description"],
    "reasoning": "Detailed explanation of risk assessment"
}

Be thorough but not paranoid. Legitimate urgent requests do exist.
Consider customer history and context."""
    
    def _build_user_prompt(self, message: str, intent: str, customer_context: Dict) -> str:
        """Build user prompt for fraud analysis"""
        
        prompt = f"Customer Message: {message}\n\n"
        prompt += f"Detected Intent: {intent}\n\n"
        prompt += "Customer Profile:\n"
        prompt += f"- Account Age: {customer_context.get('account_age_days', 0)} days\n"
        prompt += f"- Policy Status: {customer_context.get('policy_status', 'Unknown')}\n"
        prompt += f"- Payment Status: {customer_context.get('payment_status', 'Unknown')}\n"
        prompt += f"- Contact Frequency: {customer_context.get('contact_frequency', 'Unknown')}\n"
        prompt += f"- Lifetime Value: ${customer_context.get('lifetime_value', 0):,}\n"
        
        if customer_context.get('interaction_history'):
            prompt += "- Recent Interactions:\n"
            for interaction in customer_context['interaction_history'][:3]:
                prompt += f"  • {interaction}\n"
        
        prompt += "\nAnalyze for fraud risk. Return JSON:"
        return prompt
    
    def _get_risk_level(self, fraud_score: int) -> str:
        """Convert score to risk level"""
        if fraud_score >= 75:
            return "CRITICAL"
        elif fraud_score >= 50:
            return "HIGH"
        elif fraud_score >= 25:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_fraud_actions(self, fraud_score: int) -> List[Dict]:
        """Get recommended actions based on fraud score"""
        
        if fraud_score >= 75:
            return [
                {"action": "⛔ STOP - Do NOT process any transactions", "priority": "CRITICAL"},
                {"action": "Immediately escalate to fraud investigation team", "priority": "CRITICAL"},
                {"action": "Require in-person verification with photo ID", "priority": "CRITICAL"},
                {"action": "Place temporary hold on account", "priority": "CRITICAL"}
            ]
        elif fraud_score >= 50:
            return [
                {"action": "Verify identity with additional security questions", "priority": "HIGH"},
                {"action": "Flag account for fraud team review", "priority": "HIGH"},
                {"action": "Do not process high-value transactions", "priority": "HIGH"},
                {"action": "Require call-back to number on file", "priority": "MEDIUM"}
            ]
        elif fraud_score >= 25:
            return [
                {"action": "Complete standard identity verification", "priority": "MEDIUM"},
                {"action": "Document any unusual requests in case notes", "priority": "MEDIUM"}
            ]
        else:
            return [
                {"action": "Proceed with normal processing", "priority": "NORMAL"}
            ]
    
    def _mock_analysis(self, message: str, pattern_score: int, customer_context: Dict) -> Dict:
        """Fallback mock fraud analysis"""
        
        indicators = []
        
        # Identify specific indicators
        message_lower = message.lower()
        if any(word in message_lower for word in self.FRAUD_PATTERNS["urgency"]):
            indicators.append("Urgent language detected")
        if any(word in message_lower for word in self.FRAUD_PATTERNS["financial_requests"]):
            indicators.append("High-value financial request")
        if any(word in message_lower for word in self.FRAUD_PATTERNS["account_changes"]):
            indicators.append("Bank account change requested")
        
        if customer_context.get("account_age_days", 365) < 90:
            indicators.append("Recent account (less than 90 days)")
        
        if not indicators:
            indicators.append("No significant fraud indicators detected")
        
        return {
            "fraud_score": pattern_score,
            "risk_level": self._get_risk_level(pattern_score),
            "indicators": indicators,
            "recommended_actions": self._get_fraud_actions(pattern_score),
            "verification_required": pattern_score > 50,
            "suspicious_patterns": [],
            "reasoning": f"Pattern-based analysis score: {pattern_score}/100"
        }

# Initialize global fraud detector
detector = FraudDetector()
