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
            'responseMessage': "I'm not seeing any active claims in our system right now. "
                             "If you just submitted one, it can take up to 48 hours to show up. "
                             "If you'd like to file a new claim, I'd be happy to connect you with someone who can walk you through it. "
                             "Would you like me to do that?",
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
        message = f"Good news! Claim {claim_num} was approved on {date} for ${amount:,.2f}. "
        
        if claim_data.get('checkMailed'):
            mail_date = claim_data.get('checkMailedDate', date)
            message += f"We sent your check on {mail_date}, so you should see it in about 5 to 7 business days. "
            message += "If it doesn't arrive by then, just give us a call and we'll send a replacement. "
        else:
            message += "Your check will go out within the next couple days. "
            message += "By the way, if you'd like faster payments going forward, just ask about setting up direct deposit. "
            
    elif status == 'Pending':
        days_remaining = claim_data.get('daysRemaining', 10)
        message = f"I see claim {claim_num} is still under review. We got it on {claim_data.get('submittedDate', date)}. "
        
        # Add elimination period info if applicable
        if days_remaining_elim > 0:
            message += f"So far, you've submitted {days_submitted} days toward your {elimination_period} day elimination period. "
            message += f"You'll need {days_remaining_elim} more days of care before your benefits kick in. "
        elif days_submitted >= elimination_period:
            message += f"You've already met your {elimination_period} day elimination period, which is great. "
        
        # Add invoice status if needed
        if invoices_needed:
            if invoices_received < invoices_total:
                message += f"We have {invoices_received} of the {invoices_total} invoices we need. "
                message += "If you could send us the rest, that'll help us wrap this up. You can fax them to 1-800-555-9999 or upload them on our website. "
            else:
                message += "We've got all the invoices we need and our team is looking everything over. "
        
        message += f"We should have a decision for you in about {days_remaining} business days. "
        message += "If we need anything else from you, we'll reach out. "
        message += "You can always check where things stand on our website too. "
        
    elif status == 'Denied':
        message = f"I see claim {claim_num} wasn't approved. We sent you a letter on {date} explaining why. "
        message += "If you have questions or want to talk about your options, I can get you to someone who can review everything with you. "
        message += "Would you like me to transfer you?"
        
    else:
        message = f"Claim {claim_num} is showing a status of {status}. "
        message += "If you need more details, I can connect you with someone from our claims team. "
    
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
    
    message = f"Your monthly premium is ${premium:,.2f}. "
    
    if payment_data['autopay']:
        message += f"Since you have autopay set up, we'll automatically withdraw ${premium:,.2f} on {due_date_spoken}. "
        message += "If you need to make any changes to that, I can connect you with our billing team. "
    else:
        days_until_due = (due_date_obj - datetime.now()).days
        
        if days_until_due < 0:
            message += f"Just a heads up, your payment was due on {due_date_spoken}. "
            message += "To keep your coverage active, let's get that taken care of as soon as we can. "
            message += "I can help you pay right now if you'd like. "
        elif days_until_due <= 7:
            message += f"Your payment's coming up on {due_date_spoken}, that's in {days_until_due} days. "
            message += "Want to go ahead and take care of it now so you don't have to worry about it? "
        else:
            message += f"Your next payment of ${premium:,.2f} is due {due_date_spoken}. "
            message += "If you're interested, I can tell you about autopay, it makes things a lot easier. "
    
    if last_payment:
        last_payment_obj = datetime.strptime(last_payment, '%Y-%m-%d')
        last_payment_spoken = last_payment_obj.strftime('%B %d, %Y')
        message += f"We got your last payment on {last_payment_spoken}. "
    
    # Provide payment options proactively
    if not payment_data['autopay']:
        message += "You can pay by phone, mail, or online, whichever works best for you. "
    
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
    
    message = f"Your policy gives you ${daily_benefit:,.2f} per day, with a lifetime max of ${lifetime_max:,.0f}. "
    message += f"You have a {elimination_period} day elimination period, "
    message += "which just means coverage starts after you've been getting care for that many days. "
    
    if coverage_data['inflationProtection']:
        message += f"You also have {coverage_data['inflationRate']}% inflation protection built in. "
    
    message += "Want me to go into more detail about any of that?"
    
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
    
    message = f"Right now, your monthly premium is ${current_premium:,.2f}. "
    
    if has_increase:
        new_premium = rate_data['newPremium']
        effective_date = rate_data['effectiveDate']
        increase_pct = rate_data['increasePercentage']
        
        message += f"It's going up {increase_pct}% to ${new_premium:,.2f} starting {effective_date}. "
        message += "We sent you a letter with all the details about why. "
        message += "If you want to talk through it with someone, I can get you connected. Would that help?"
    else:
        message += "You don't have any rate increases coming up. "
        message += "If you have other questions about your premium, I'm happy to get you to the right person."
    
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
