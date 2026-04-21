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
    Look up claim status with proactive next steps
    Enhanced to provide complete information and prevent escalation
    Includes elimination period tracking and invoice status
    """
    # For demo: Mock Salesforce lookup
    # For production: Use Salesforce API
    
    if os.getenv('USE_SALESFORCE') == 'true':
        claim_data = lookup_salesforce_claim(phone)
    else:
        claim_data = mock_claim_lookup(phone)
    
    if not claim_data:
        return {
            'responseMessage': "Hmm, I'm not seeing any claims in the system right now. "
                             "If you just filed one, it might take a day or two to pop up. "
                             "Need to file a new one? I can get you to the right folks who'll help you out. "
                             "Want me to connect you?",
            'success': False
        }
    
    # Format response
    claim_num = claim_data.get('claimNumber', 'Unknown')
    status = claim_data.get('status', 'Unknown')
    amount = claim_data.get('amount', 0)
    date = claim_data.get('approvedDate', claim_data.get('submittedDate', 'Unknown'))
    
    # Elimination period tracking
    days_submitted = claim_data.get('daysSubmitted', 0)
    elimination_period = claim_data.get('eliminationPeriod', 90)
    days_remaining_elim = max(0, elimination_period - days_submitted)
    invoices_needed = claim_data.get('invoicesNeeded', False)
    invoices_received = claim_data.get('invoicesReceived', 0)
    invoices_total = claim_data.get('invoicesTotal', 0)
    
    if status == 'Approved':
        message = f"Great news! Claim {claim_num} got approved on {date} for ${amount:,.2f}. "
        
        if claim_data.get('checkMailed'):
            mail_date = claim_data.get('checkMailedDate', date)
            message += f"We sent your check on {mail_date}, so it should land in your mailbox in about 5 to 7 days. "
            message += "If it doesn't show up by then, just holler and we'll send another one. "
        else:
            message += "Your check's going out in the next day or two. "
            message += "Oh, and if you want faster payments down the road, ask about direct deposit sometime. "
            
    elif status == 'Pending':
        days_remaining = claim_data.get('daysRemaining', 10)
        message = f"Alright, so claim {claim_num} is still being reviewed. We got it on {claim_data.get('submittedDate', date)}. "
        
        # Add elimination period info if applicable
        if days_remaining_elim > 0:
            message += f"You're at {days_submitted} days toward your {elimination_period} day elimination period. "
            message += f"So you'll need about {days_remaining_elim} more days before benefits start. "
        elif days_submitted >= elimination_period:
            message += f"Good news, you're past your {elimination_period} day elimination period. "
        
        # Add invoice status if needed
        if invoices_needed:
            if invoices_received < invoices_total:
                message += f"We've got {invoices_received} of the {invoices_total} invoices we need. "
                message += "If you can send the rest over, that'll speed things up. Fax to 1-800-555-9999 or toss them on our website. "
            else:
                message += "We've got all your invoices and the team's going through everything. "
        
        message += f"Should have an answer for you in about {days_remaining} business days. "
        message += "If we need anything else, we'll reach out. "
        message += "You can check anytime on the website too. "
        
    elif status == 'Denied':
        message = f"So claim {claim_num} didn't get approved. We sent you a letter on {date} explaining everything. "
        message += "Got questions or want to talk it through? I can get you to someone who knows the details. "
        message += "Want me to transfer you?"
        
    else:
        message = f"Looks like claim {claim_num} is showing as {status}. "
        message += "Want to talk to someone from claims about it? "
    
    return {
        'responseMessage': message,
        'success': True,
        'claimNumber': claim_num,
        'status': status
    }


def handle_payment(phone: str, params: Dict) -> Dict[str, Any]:
    """
    Handle payment inquiry with proactive options
    Enhanced to prevent customer drop-off
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
    
    message = f"So your monthly premium is ${premium:,.2f}. "
    
    if payment_data['autopay']:
        message += f"You've got autopay set up, so we'll pull ${premium:,.2f} on {due_date_spoken}. "
        message += "Need to change anything with that? I can connect you with billing. "
    else:
        days_until_due = (due_date_obj - datetime.now()).days
        
        if days_until_due < 0:
            message += f"Heads up, your payment was due {due_date_spoken}. "
            message += "Let's get that taken care of so your coverage stays good. "
            message += "Want to pay now? "
        elif days_until_due <= 7:
            message += f"Your payment's coming up {due_date_spoken}, that's in {days_until_due} days. "
            message += "Wanna knock it out now so you don't gotta think about it? "
        else:
            message += f"Next payment of ${premium:,.2f} is due {due_date_spoken}. "
            message += "Ever think about autopay? Makes life way easier. "
    
    if last_payment:
        last_payment_obj = datetime.strptime(last_payment, '%Y-%m-%d')
        last_payment_spoken = last_payment_obj.strftime('%B %d, %Y')
        message += f"Last one we got from you was {last_payment_spoken}. "
    
    # Provide payment options proactively
    if not payment_data['autopay']:
        message += "You can pay by phone, mail, or online, whatever works. "
    
    return {
        'responseMessage': message,
        'success': True,
        'premium': premium,
        'dueDate': due_date,
        'autopay': payment_data['autopay']
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
    
    message = f"Alright, so your policy gives you ${daily_benefit:,.2f} a day, with a lifetime max of ${lifetime_max:,.0f}. "
    message += f"There's a {elimination_period} day elimination period, "
    message += "basically meaning coverage starts after you've been in care that many days. "
    
    if coverage_data['inflationProtection']:
        message += f"And you've got {coverage_data['inflationRate']}% inflation protection, which is nice. "
    
    message += "Need more detail on any of that?"
    
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
    
    message = f"So right now you're paying ${current_premium:,.2f} a month. "
    
    if has_increase:
        new_premium = rate_data['newPremium']
        effective_date = rate_data['effectiveDate']
        increase_pct = rate_data['increasePercentage']
        
        message += f"Heads up, it's going up {increase_pct}% to ${new_premium:,.2f} starting {effective_date}. "
        message += "We sent you a letter with the whole story. "
        message += "Wanna talk to someone about it?"
    else:
        message += "No rate increases coming your way. "
        message += "Got other questions about your premium? I can get you to the right person."
    
    return {
        'responseMessage': message,
        'success': True
    }


def mock_claim_lookup(phone: str) -> Dict[str, Any]:
    """
    Mock Salesforce claim lookup
    Enhanced with elimination period and invoice tracking
    """
    # Simulate different scenarios based on phone number
    last_digit = int(phone[-1]) if phone else 0
    
    if last_digit == 0:
        return None  # No claim found
    
    if last_digit % 2 == 0:
        # Approved claim - elimination period completed
        return {
            'claimNumber': f'CLM-{45678 + last_digit}',
            'status': 'Approved',
            'amount': 2800.00,
            'approvedDate': '04/10/2026',
            'checkMailed': True,
            'checkMailedDate': '04/18/2026',
            'daysSubmitted': 95,
            'eliminationPeriod': 90,
            'invoicesNeeded': True,
            'invoicesReceived': 3,
            'invoicesTotal': 3
        }
    else:
        # Pending claim - still in elimination period or waiting for invoices
        if last_digit in [1, 3]:
            # Still in elimination period
            return {
                'claimNumber': f'CLM-{45678 + last_digit}',
                'status': 'Pending',
                'amount': 0,
                'submittedDate': '04/15/2026',
                'daysRemaining': 5,
                'daysSubmitted': 45,
                'eliminationPeriod': 90,
                'invoicesNeeded': True,
                'invoicesReceived': 2,
                'invoicesTotal': 2
            }
        else:
            # Elimination period complete, waiting for invoices
            return {
                'claimNumber': f'CLM-{45678 + last_digit}',
                'status': 'Pending',
                'amount': 0,
                'submittedDate': '04/01/2026',
                'daysRemaining': 3,
                'daysSubmitted': 95,
                'eliminationPeriod': 90,
                'invoicesNeeded': True,
                'invoicesReceived': 1,
                'invoicesTotal': 3
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
