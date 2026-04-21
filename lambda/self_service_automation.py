"""
Self-Service Automation Lambda Function
Handles automated responses for high-confidence intents

Integrates with Salesforce for data lookup
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any

def lambda_handler(event, context):
    """
    Handle self-service automation
    
    Input:
    {
        "intentName": "CLAIM_STATUS",
        "phoneNumber": "+15551234567",
        "relationship": "owner"
    }
    
    Output:
    {
        "responseMessage": "Your claim #12345 was approved...",
        "success": true
    }
    """
    
    print(f"Received event: {json.dumps(event)}")
    
    params = event.get('Details', {}).get('Parameters', {})
    intent = params.get('intentName', '')
    phone = params.get('phoneNumber', '')
    
    # Route to appropriate handler
    handlers = {
        'CLAIM_STATUS': handle_claim_status,
        'PAYMENT': handle_payment,
        'COVERAGE_INQUIRY': handle_coverage,
        'RATE_INCREASE': handle_rate_increase
    }
    
    handler = handlers.get(intent)
    if not handler:
        return error_response(f"No handler for intent: {intent}")
    
    return handler(phone, params)


def handle_claim_status(phone: str, params: Dict) -> Dict[str, Any]:
    """
    Look up claim status from Salesforce
    """
    # For demo: Mock Salesforce lookup
    # For production: Use Salesforce API
    
    if os.getenv('USE_SALESFORCE') == 'true':
        claim_data = lookup_salesforce_claim(phone)
    else:
        claim_data = mock_claim_lookup(phone)
    
    if not claim_data:
        return {
            'responseMessage': "I don't see any active claims on file. If you recently submitted a claim, it may take 24 to 48 hours to appear in our system. Would you like to speak with an agent?",
            'success': False
        }
    
    # Format response
    claim_num = claim_data.get('claimNumber', 'Unknown')
    status = claim_data.get('status', 'Unknown')
    amount = claim_data.get('amount', 0)
    date = claim_data.get('approvedDate', claim_data.get('submittedDate', 'Unknown'))
    
    if status == 'Approved':
        message = f"Great news! Your claim number {claim_num} was approved on {date} for ${amount:,.2f}. "
        
        if claim_data.get('checkMailed'):
            mail_date = claim_data.get('checkMailedDate', date)
            message += f"Your reimbursement check was mailed on {mail_date} and should arrive within 5 to 7 business days. "
        else:
            message += "Your reimbursement check will be mailed within 2 business days. "
            
    elif status == 'Pending':
        message = f"Your claim number {claim_num} is currently pending review. We received it on {claim_data.get('submittedDate', date)} and you should receive a decision within {claim_data.get('daysRemaining', 10)} business days. "
        
    elif status == 'Denied':
        message = f"I see that claim number {claim_num} was not approved. A detailed explanation was mailed to you on {date}. If you have questions about this decision, I can connect you with a claims specialist. Would you like me to do that?"
        
    else:
        message = f"Your claim number {claim_num} is currently in {status} status. "
    
    return {
        'responseMessage': message,
        'success': True,
        'claimNumber': claim_num,
        'status': status
    }


def handle_payment(phone: str, params: Dict) -> Dict[str, Any]:
    """
    Handle payment inquiry or process payment
    """
    # Mock payment data
    payment_data = mock_payment_lookup(phone)
    
    if not payment_data:
        return error_response("No payment information found")
    
    premium = payment_data['premiumAmount']
    due_date = payment_data['dueDate']
    last_payment = payment_data.get('lastPaymentDate')
    
    # Format dates for speech
    due_date_obj = datetime.strptime(due_date, '%Y-%m-%d')
    due_date_spoken = due_date_obj.strftime('%B %d, %Y')  # e.g., "May 1st, 2026"
    
    message = f"Your monthly premium is ${premium:,.2f}. "
    
    if payment_data['autopay']:
        message += f"You have automatic payments set up. Your next payment of ${premium:,.2f} will be withdrawn on {due_date_spoken}. "
    else:
        days_until_due = (due_date_obj - datetime.now()).days
        
        if days_until_due < 0:
            message += f"Your payment was due on {due_date_spoken}. To avoid a lapse in coverage, please make a payment as soon as possible. "
        elif days_until_due <= 7:
            message += f"Your payment is due on {due_date_spoken}, which is in {days_until_due} days. "
        else:
            message += f"Your next payment of ${premium:,.2f} is due on {due_date_spoken}. "
    
    if last_payment:
        last_payment_obj = datetime.strptime(last_payment, '%Y-%m-%d')
        last_payment_spoken = last_payment_obj.strftime('%B %d, %Y')
        message += f"Your last payment was received on {last_payment_spoken}. "
    
    message += "To make a payment now, I can transfer you to our automated payment system. Would you like to do that?"
    
    return {
        'responseMessage': message,
        'success': True
    }


def handle_coverage(phone: str, params: Dict) -> Dict[str, Any]:
    """
    Provide coverage information
    """
    coverage_data = mock_coverage_lookup(phone)
    
    if not coverage_data:
        return error_response("No policy information found")
    
    daily_benefit = coverage_data['dailyBenefit']
    lifetime_max = coverage_data['lifetimeMax']
    elimination_period = coverage_data['eliminationPeriod']
    
    message = f"Your long-term care policy provides a daily benefit of ${daily_benefit:,.2f} with a lifetime maximum of ${lifetime_max:,.0f}. "
    message += f"Your policy has a {elimination_period}-day elimination period. "
    message += "This means coverage begins after you've been receiving care for that many days. "
    
    if coverage_data['inflationProtection']:
        message += f"You have {coverage_data['inflationRate']}% inflation protection. "
    
    message += "Would you like more detailed information about your benefits?"
    
    return {
        'responseMessage': message,
        'success': True
    }


def handle_rate_increase(phone: str, params: Dict) -> Dict[str, Any]:
    """
    Handle rate increase inquiries
    """
    rate_data = mock_rate_lookup(phone)
    
    if not rate_data:
        return error_response("No policy information found")
    
    current_premium = rate_data['currentPremium']
    has_increase = rate_data.get('hasUpcomingIncrease', False)
    
    message = f"Your current monthly premium is ${current_premium:,.2f}. "
    
    if has_increase:
        new_premium = rate_data['newPremium']
        effective_date = rate_data['effectiveDate']
        increase_pct = rate_data['increasePercentage']
        
        message += f"Your premium will be increasing by {increase_pct}% to ${new_premium:,.2f}, effective {effective_date}. "
        message += "A detailed explanation of this adjustment was mailed to you. "
        message += "If you have questions about this increase, I can connect you with a specialist. Would you like to speak with someone?"
    else:
        message += "You do not have any scheduled rate increases at this time. "
        message += "If you have specific questions about premium rates, I'd be happy to connect you with a specialist."
    
    return {
        'responseMessage': message,
        'success': True
    }


def mock_claim_lookup(phone: str) -> Dict[str, Any]:
    """
    Mock Salesforce claim lookup
    """
    # Simulate different scenarios based on phone number
    last_digit = int(phone[-1]) if phone else 0
    
    if last_digit == 0:
        return None  # No claim found
    
    if last_digit % 2 == 0:
        # Approved claim
        return {
            'claimNumber': f'CLM-{45678 + last_digit}',
            'status': 'Approved',
            'amount': 2800.00,
            'approvedDate': '04/10/2026',
            'checkMailed': True,
            'checkMailedDate': '04/18/2026'
        }
    else:
        # Pending claim
        return {
            'claimNumber': f'CLM-{45678 + last_digit}',
            'status': 'Pending',
            'amount': 0,
            'submittedDate': '04/15/2026',
            'daysRemaining': 5
        }


def mock_payment_lookup(phone: str) -> Dict[str, Any]:
    """
    Mock payment information
    """
    return {
        'premiumAmount': 285.00,
        'dueDate': '2026-05-01',
        'lastPaymentDate': '2026-04-01',
        'autopay': False
    }


def mock_coverage_lookup(phone: str) -> Dict[str, Any]:
    """
    Mock coverage information
    """
    return {
        'dailyBenefit': 200.00,
        'lifetimeMax': 300000,
        'eliminationPeriod': 90,
        'inflationProtection': True,
        'inflationRate': 3
    }


def mock_rate_lookup(phone: str) -> Dict[str, Any]:
    """
    Mock rate increase information
    """
    # Simulate different scenarios based on phone number
    last_digit = int(phone[-1]) if phone else 0
    
    current_premium = 285.00
    
    # Numbers ending in 1-3 have upcoming rate increase
    if last_digit in [1, 2, 3]:
        return {
            'currentPremium': current_premium,
            'hasUpcomingIncrease': True,
            'newPremium': round(current_premium * 1.08, 2),  # 8% increase
            'effectiveDate': 'July 1st, 2026',
            'increasePercentage': 8
        }
    else:
        return {
            'currentPremium': current_premium,
            'hasUpcomingIncrease': False
        }


def lookup_salesforce_claim(phone: str) -> Dict[str, Any]:
    """
    Actual Salesforce API call (for production)
    """
    # Uncomment for production
    """
    from simple_salesforce import Salesforce
    
    sf = Salesforce(
        username=os.getenv('SF_USERNAME'),
        password=os.getenv('SF_PASSWORD'),
        security_token=os.getenv('SF_TOKEN')
    )
    
    # Query for claim
    query = f"SELECT Id, ClaimNumber__c, Status__c, Amount__c FROM Claim__c WHERE Phone__c = '{phone}' ORDER BY CreatedDate DESC LIMIT 1"
    result = sf.query(query)
    
    if not result['records']:
        return None
    
    claim = result['records'][0]
    return {
        'claimNumber': claim['ClaimNumber__c'],
        'status': claim['Status__c'],
        'amount': claim['Amount__c']
    }
    """
    return mock_claim_lookup(phone)


def error_response(message: str) -> Dict[str, Any]:
    """
    Return error response
    """
    return {
        'responseMessage': f"I apologize, but {message}. Let me connect you with an agent who can help.",
        'success': False,
        'error': message
    }


# For local testing
if __name__ == '__main__':
    test_cases = [
        {
            'Details': {
                'Parameters': {
                    'intentName': 'CLAIM_STATUS',
                    'phoneNumber': '+15551234562'
                }
            }
        },
        {
            'Details': {
                'Parameters': {
                    'intentName': 'PAYMENT',
                    'phoneNumber': '+15551234567'
                }
            }
        },
        {
            'Details': {
                'Parameters': {
                    'intentName': 'COVERAGE_INQUIRY',
                    'phoneNumber': '+15551234567'
                }
            }
        },
        {
            'Details': {
                'Parameters': {
                    'intentName': 'RATE_INCREASE',
                    'phoneNumber': '+15551234562'
                }
            }
        }
    ]
    
    for test in test_cases:
        result = lambda_handler(test, None)
        print(f"\n{test['Details']['Parameters']['intentName']}:")
        print(result['responseMessage'])
