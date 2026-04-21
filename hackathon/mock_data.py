"""
Mock Customer Data Generator
Simulates 15-20 customer profiles with realistic scenarios for hackathon demo
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict

class MockDataGenerator:
    """Generate realistic customer profiles and messages for demo"""
    
    # 20 Intent categories
    INTENT_CATEGORIES = [
        "PAYMENT_INQUIRY",
        "PAYMENT_DISPUTE", 
        "PAYMENT_SETUP",
        "CLAIM_SUBMISSION",
        "CLAIM_STATUS",
        "POLICY_CHANGE",
        "POLICY_CANCELLATION",
        "POLICY_REINSTATEMENT",
        "COVERAGE_QUESTION",
        "BENEFITS_INQUIRY",
        "PROVIDER_REFERRAL",
        "ACCOUNT_UPDATE",
        "DOCUMENT_REQUEST",
        "PREMIUM_QUESTION",
        "FRAUD_INDICATOR",
        "COMPLAINT_ESCALATION",
        "GENERAL_INQUIRY",
        "TECHNICAL_SUPPORT",
        "LAPSE_WARNING",
        "BENEFICIARY_CHANGE"
    ]
    
    def __init__(self):
        self.customers = self._generate_customers()
        self.sample_messages = self._generate_sample_messages()
        
    def _generate_customers(self) -> List[Dict]:
        """Generate 20 realistic customer profiles"""
        
        names = [
            "Sarah Johnson", "Michael Chen", "Patricia Rodriguez", "James Williams",
            "Maria Garcia", "Robert Taylor", "Jennifer Martinez", "David Anderson",
            "Lisa Thompson", "Christopher Lee", "Nancy White", "Daniel Harris",
            "Karen Martin", "Matthew Jackson", "Betty Thomas", "Anthony Moore",
            "Sandra Jackson", "Mark Wilson", "Ashley Brown", "Joshua Davis"
        ]
        
        policy_types = [
            "Health Insurance - Gold Plan",
            "Life Insurance - Term 20",
            "Long-Term Care Insurance",
            "Disability Insurance - Premium",
            "Health Insurance - Silver Plan",
            "Life Insurance - Whole Life",
            "Health Insurance - Bronze Plan",
            "Critical Illness Insurance"
        ]
        
        customers = []
        for i, name in enumerate(names):
            customer = {
                "customer_id": f"CUST_{str(i+1).zfill(3)}",
                "name": name,
                "policy_type": random.choice(policy_types),
                "policy_number": f"POL-{random.choice(['HG', 'LT', 'DI', 'CI'])}-{random.randint(100000, 999999)}",
                "policy_status": random.choice(["Active", "Active", "Active", "Pending", "Lapsed"]),
                "lifetime_value": random.randint(5000, 75000),
                "account_age_days": random.randint(30, 3650),
                "interaction_history": self._generate_interaction_history(),
                "sentiment": random.choice(["Satisfied", "Satisfied", "Neutral", "Frustrated"]),
                "repeat_caller": random.choice([True, False]),
                "contact_frequency": random.choice(["Low (1-2/month)", "Medium (3-5/month)", "High (6+/month)"]),
                "fraud_risk_score": random.randint(5, 95),
                "payment_status": random.choice(["Current", "Current", "Current", "Past Due 15 days"]),
                "last_contact_date": self._random_date(30),
                "preferred_language": "English",
                "email": f"{name.lower().replace(' ', '.')}@email.com",
                "phone": f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
            }
            customers.append(customer)
            
        return customers
    
    def _generate_interaction_history(self) -> List[str]:
        """Generate realistic interaction history"""
        
        interactions = [
            "Payment inquiry (3 days ago)",
            "Billing dispute (1 week ago)",
            "Coverage question (2 weeks ago)",
            "Claim status check (5 days ago)",
            "Policy change request (10 days ago)",
            "Premium inquiry (1 month ago)",
            "Provider referral (2 weeks ago)",
            "Account update (3 days ago)"
        ]
        
        num_interactions = random.randint(0, 5)
        return random.sample(interactions, num_interactions)
    
    def _random_date(self, days_back: int) -> str:
        """Generate random date within last N days"""
        days_ago = random.randint(0, days_back)
        date = datetime.now() - timedelta(days=days_ago)
        return date.strftime("%Y-%m-%d")
    
    def _generate_sample_messages(self) -> List[Dict]:
        """Generate sample customer messages for each intent category"""
        
        return [
            {
                "intent": "PAYMENT_DISPUTE",
                "message": "I was charged twice for my premium this month. I see two charges of $250 on my credit card but should only have one.",
                "expected_confidence": 0.94
            },
            {
                "intent": "CLAIM_STATUS", 
                "message": "I submitted a claim two weeks ago for my doctor visit and haven't heard anything back. Can you tell me the status?",
                "expected_confidence": 0.91
            },
            {
                "intent": "PROVIDER_REFERRAL",
                "message": "I need to find a cardiologist in my network. Can you help me locate one near zip code 02108?",
                "expected_confidence": 0.88
            },
            {
                "intent": "FRAUD_INDICATOR",
                "message": "I need to cash out my policy immediately. It's urgent and I need the money wired to my new bank account today.",
                "expected_confidence": 0.85
            },
            {
                "intent": "COMPLAINT_ESCALATION",
                "message": "This is the third time I've called about this issue and no one has helped me! I want to speak to a supervisor right now.",
                "expected_confidence": 0.92
            },
            {
                "intent": "COVERAGE_QUESTION",
                "message": "Does my plan cover physical therapy? I injured my knee and my doctor recommended 8 weeks of treatment.",
                "expected_confidence": 0.89
            },
            {
                "intent": "PAYMENT_INQUIRY",
                "message": "When is my next premium payment due? I want to make sure I don't miss it.",
                "expected_confidence": 0.87
            },
            {
                "intent": "POLICY_CHANGE",
                "message": "I just had a baby and need to add her to my health insurance policy. What do I need to do?",
                "expected_confidence": 0.90
            },
            {
                "intent": "TECHNICAL_SUPPORT",
                "message": "I can't log into my online account. I keep getting an error message when I try to reset my password.",
                "expected_confidence": 0.86
            },
            {
                "intent": "BENEFICIARY_CHANGE",
                "message": "I recently got divorced and need to update my life insurance beneficiary from my ex-spouse to my children.",
                "expected_confidence": 0.93
            },
            {
                "intent": "CLAIM_SUBMISSION",
                "message": "How do I submit a claim for my recent surgery? I have all my medical bills ready.",
                "expected_confidence": 0.88
            },
            {
                "intent": "PREMIUM_QUESTION",
                "message": "Why did my premium increase by $50 this month? I didn't make any changes to my policy.",
                "expected_confidence": 0.85
            },
            {
                "intent": "PAYMENT_SETUP",
                "message": "I want to set up automatic payments from my checking account. Can you help me with that?",
                "expected_confidence": 0.87
            },
            {
                "intent": "DOCUMENT_REQUEST",
                "message": "I need a copy of my policy documents for a mortgage application. Can you email those to me?",
                "expected_confidence": 0.84
            },
            {
                "intent": "LAPSE_WARNING",
                "message": "I received a notice that my policy is going to lapse. I thought I paid last month - what happened?",
                "expected_confidence": 0.89
            },
            {
                "intent": "BENEFITS_INQUIRY",
                "message": "What dental benefits are included in my health plan? Do I have coverage for orthodontics?",
                "expected_confidence": 0.86
            },
            {
                "intent": "ACCOUNT_UPDATE",
                "message": "I moved to a new address last month. I need to update my contact information on file.",
                "expected_confidence": 0.83
            },
            {
                "intent": "POLICY_CANCELLATION",
                "message": "I got a new job with better benefits, so I need to cancel my individual health insurance policy.",
                "expected_confidence": 0.90
            },
            {
                "intent": "POLICY_REINSTATEMENT",
                "message": "My policy lapsed because I missed a payment. Can I reinstate it? I want to keep my coverage.",
                "expected_confidence": 0.88
            },
            {
                "intent": "GENERAL_INQUIRY",
                "message": "Do you offer long-term care insurance? I'm interested in learning more about your products.",
                "expected_confidence": 0.82
            }
        ]
    
    def get_customer_by_id(self, customer_id: str) -> Dict:
        """Retrieve specific customer profile"""
        for customer in self.customers:
            if customer["customer_id"] == customer_id:
                return customer
        return None
    
    def get_all_customers(self) -> List[Dict]:
        """Return all mock customers"""
        return self.customers
    
    def get_sample_messages(self) -> List[Dict]:
        """Return all sample messages"""
        return self.sample_messages
    
    def get_message_by_intent(self, intent: str) -> Dict:
        """Get sample message for specific intent"""
        for msg in self.sample_messages:
            if msg["intent"] == intent:
                return msg
        return None

# Initialize global data generator
data_generator = MockDataGenerator()
