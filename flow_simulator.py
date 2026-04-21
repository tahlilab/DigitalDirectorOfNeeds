"""
Amazon Connect Contact Flow Simulator
Test AI-enhanced flows locally without deploying to AWS

Usage:
    python flow_simulator.py --flow 1_LTC_Retail_Entry_AI_Enhanced.json --utterance "I need to check my claim status"
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Import Lambda functions for local testing
sys.path.append(str(Path(__file__).parent / 'lambda'))
try:
    from gpt4o_intent_classifier import lambda_handler as gpt4o_handler
    from self_service_automation import lambda_handler as selfserve_handler
except ImportError:
    print("Warning: Lambda functions not found. Using mock responses.")
    gpt4o_handler = None
    selfserve_handler = None


class ContactFlowSimulator:
    """
    Simulates Amazon Connect contact flow execution
    """
    
    def __init__(self, flow_json_path: str):
        """Load contact flow JSON"""
        with open(flow_json_path, 'r') as f:
            self.flow = json.load(f)
        
        self.actions = {action['Identifier']: action for action in self.flow['Actions']}
        self.contact_attributes = {}
        self.system_attributes = {
            'CustomerEndpoint': {
                'Address': '+15551234567',
                'Type': 'TELEPHONE_NUMBER'
            }
        }
        self.execution_log = []
        
    def run(self, customer_utterance: str) -> Dict[str, Any]:
        """
        Execute flow with customer utterance
        """
        print("\n" + "="*80)
        print("CONTACT FLOW SIMULATION")
        print("="*80)
        flow_name = self.flow.get('Metadata', {}).get('name', 'Unknown Flow')
        print(f"Flow: {flow_name}")
        print(f"Customer says: '{customer_utterance}'")
        print("="*80 + "\n")
        
        # Start from entry action
        current_action_id = self.flow['StartAction']
        step_count = 0
        max_steps = 50  # Prevent infinite loops
        
        while current_action_id and step_count < max_steps:
            step_count += 1
            
            action = self.actions.get(current_action_id)
            if not action:
                print(f"❌ ERROR: Action not found: {current_action_id}")
                break
            
            # Execute action
            next_action_id = self.execute_action(action, customer_utterance)
            
            # Log execution
            self.execution_log.append({
                'step': step_count,
                'actionId': current_action_id,
                'actionType': action['Type'],
                'nextAction': next_action_id
            })
            
            current_action_id = next_action_id
        
        # Print summary
        self.print_summary()
        
        return {
            'success': True,
            'steps': step_count,
            'attributes': self.contact_attributes,
            'log': self.execution_log
        }
    
    def execute_action(self, action: Dict, utterance: str) -> Optional[str]:
        """
        Execute single action and return next action ID
        """
        action_type = action['Type']
        action_id = action['Identifier']
        
        print(f"Step {len(self.execution_log) + 1}: {action_id} ({action_type})")
        
        # Route to handler
        handlers = {
            'MessageParticipant': self.handle_message,
            'GetParticipantInput': self.handle_get_input,
            'InvokeLambdaFunction': self.handle_lambda,
            'UpdateContactAttributes': self.handle_update_attributes,
            'TransferContactToFlow': self.handle_transfer_flow,
            'TransferParticipantToThirdParty': self.handle_transfer_queue,
            'DisconnectParticipant': self.handle_disconnect,
            'Compare': self.handle_compare
        }
        
        handler = handlers.get(action_type, self.handle_default)
        return handler(action, utterance)
    
    def handle_message(self, action: Dict, utterance: str) -> str:
        """Play message to customer"""
        message = action['Parameters'].get('Text', '')
        print(f"  🔊 Says: {message}")
        return action['Transitions']['NextAction']
    
    def handle_get_input(self, action: Dict, utterance: str) -> str:
        """Get customer input (speech or DTMF)"""
        params = action['Parameters']
        
        # Check if Lex bot configured
        if 'LexV2Bot' in params:
            bot_name = params['LexV2Bot']['Name']
            print(f"  🤖 Lex bot '{bot_name}' listening...")
            print(f"  🎤 Customer says: '{utterance}'")
            
            # Store transcription for Lambda
            self.contact_attributes['transcription'] = utterance
            
            # Success path
            return action['Transitions']['NextAction']
        
        # DTMF menu
        elif 'DTMF' in params:
            print(f"  📞 DTMF menu (simulated press 1)")
            return action['Transitions']['NextAction']
        
        else:
            return action['Transitions']['NextAction']
    
    def handle_lambda(self, action: Dict, utterance: str) -> str:
        """Invoke Lambda function"""
        params = action.get('Parameters', {})
        function_arn = params.get('LambdaFunctionArn', params.get('FunctionArn', 'unknown'))
        function_name = function_arn.split(':')[-1]
        
        print(f"  ⚡ Invoking Lambda: {function_name}")
        
        # Build Lambda event from LambdaInvocationAttributes
        lambda_params = params.get('LambdaInvocationAttributes', {})
        event_params = {}
        
        # Resolve $.Attributes references
        for key, value in lambda_params.items():
            if isinstance(value, str) and value.startswith('$.'):
                # Use contact attributes or utterance
                if 'Lex.InputTranscript' in value or 'transcription' in key:
                    event_params[key] = utterance
                else:
                    attr_name = value.split('.')[-1]
                    event_params[key] = self.contact_attributes.get(attr_name, '')
            else:
                event_params[key] = value
        
        # Build Lambda event
        event = {
            'Details': {
                'Parameters': {
                    **event_params,
                    **self.contact_attributes,
                    'phoneNumber': self.system_attributes['CustomerEndpoint']['Address']
                }
            }
        }
        
        # Route to appropriate Lambda
        if 'gpt4o-intent-classifier' in function_name:
            if gpt4o_handler:
                result = gpt4o_handler(event, None)
                print(f"  ✅ Intent: {result['intentName']} (confidence: {result['confidence']}%)")
                print(f"     Relationship: {result['relationship']}, CallType: {result['callType']}")
                print(f"     Can self-serve: {result['canSelfServe']}")
            else:
                result = {'intentName': 'CLAIM_STATUS', 'confidence': '85', 'canSelfServe': 'true'}
            
        elif 'self-service-automation' in function_name:
            if selfserve_handler:
                result = selfserve_handler(event, None)
                if result.get('success'):
                    print("  ✅ Self-service response:")
                    print(f"     {result['responseMessage'][:150]}...")
                else:
                    print(f"  ⚠️  Self-service failed: {result.get('error', 'Unknown')}")
            else:
                result = {'success': True, 'responseMessage': 'Mock self-service response'}
        
        else:
            print("  ⚠️  Lambda not implemented in simulator")
            result = {'success': 'true'}
        
        # Store Lambda response in attributes (External namespace)
        for key, value in result.items():
            self.contact_attributes[f"External.{key}"] = str(value)
        
        # Success or Error path
        if result.get('success') or result.get('confidence'):
            return action['Transitions']['NextAction']
        else:
            errors = action['Transitions'].get('Errors', [])
            if errors:
                return errors[0].get('NextAction')
            return None
    
    def handle_update_attributes(self, action: Dict, utterance: str) -> str:
        """Update contact attributes"""
        attributes = action['Parameters'].get('Attributes', {})
        
        for key, value in attributes.items():
            # Replace $.Attributes.* or $.External.* references
            if isinstance(value, str) and value.startswith('$.'):
                parts = value.replace('$', '').strip('.').split('.')
                
                if len(parts) >= 2:
                    namespace = parts[0]  # Attributes or External
                    attr_name = parts[1]
                    
                    # Look up value from appropriate namespace
                    if namespace == 'External':
                        lookup_key = f"External.{attr_name}"
                    else:
                        lookup_key = attr_name
                    
                    value = self.contact_attributes.get(lookup_key, value)
            
            self.contact_attributes[key] = value
            print(f"  📝 Set attribute: {key} = {value}")
        
        return action['Transitions']['NextAction']
    
    def handle_compare(self, action: Dict, utterance: str) -> str:
        """Compare values and branch"""
        params = action.get('Parameters', {})
        comparison_ref = params.get('ComparisonValue', '')
        
        # Extract the value to compare
        if isinstance(comparison_ref, str) and comparison_ref.startswith('$.Attributes.'):
            attr_name = comparison_ref.replace('$.Attributes.', '')
            actual_value = self.contact_attributes.get(attr_name, '')
        else:
            actual_value = str(comparison_ref)
        
        print(f"  🔀 Compare: value='{actual_value}'")
        
        # Check conditions in Transitions
        transitions = action.get('Transitions', {})
        conditions = transitions.get('Conditions', [])
        
        # Evaluate each condition
        for cond in conditions:
            condition_def = cond.get('Condition', {})
            operator = condition_def.get('Operator', 'Equals')
            operands = condition_def.get('Operands', [])
            
            if not operands:
                continue
            
            compare_to = operands[0]
            
            # Evaluate
            matched = False
            if operator == 'Equals':
                matched = str(actual_value).lower() == str(compare_to).lower()
                print(f"     Testing: '{actual_value}' == '{compare_to}' → {matched}")
            elif operator == 'NumberLessThan':
                try:
                    matched = float(actual_value) < float(compare_to)
                    print(f"     Testing: {actual_value} < {compare_to} → {matched}")
                except Exception:
                    matched = False
            elif operator == 'NumberGreaterThan':
                try:
                    matched = float(actual_value) > float(compare_to)
                    print(f"     Testing: {actual_value} > {compare_to} → {matched}")
                except Exception:
                    matched = False
            
            if matched:
                print("     ✓ Condition matched!")
                return cond.get('NextAction')
        
        # No match - take default NextAction
        print("     → Taking default path")
        return transitions.get('NextAction')
    
    def handle_transfer_flow(self, action: Dict, utterance: str) -> str:
        """Transfer to another flow"""
        flow_arn = action['Parameters']['ContactFlowId']
        flow_name = flow_arn.split('/')[-1]
        print(f"  📲 Transfer to flow: {flow_name}")
        print(f"  🛑 Flow transfer ends simulation")
        return None
    
    def handle_transfer_queue(self, action: Dict, utterance: str) -> str:
        """Transfer to queue"""
        queue_arn = action['Parameters']['QueueId']
        queue_name = queue_arn.split('/')[-1]
        print(f"  📞 Transfer to queue: {queue_name}")
        print(f"  🛑 Queue transfer ends simulation")
        return None
    
    def handle_disconnect(self, action: Dict, utterance: str) -> str:
        """Disconnect call"""
        print(f"  👋 Call disconnected")
        return None
    
    def handle_default(self, action: Dict, utterance: str) -> str:
        """Default handler for unknown action types"""
        print(f"  ⚠️  Action type not implemented: {action['Type']}")
        return action['Transitions'].get('NextAction')
    
    def print_summary(self):
        """Print execution summary"""
        print("\n" + "="*80)
        print("SIMULATION SUMMARY")
        print("="*80)
        print(f"Total steps: {len(self.execution_log)}")
        print(f"\nFinal Contact Attributes:")
        for key, value in sorted(self.contact_attributes.items()):
            print(f"  • {key}: {value}")
        print("="*80 + "\n")


def run_test_scenarios():
    """
    Run predefined test scenarios
    """
    flow_path = Path(__file__).parent / "1_LTC_Retail_Entry_AI_Enhanced.json"
    
    test_cases = [
        {
            'name': 'Claim Status - Owner - High Confidence',
            'utterance': 'I need to check my claim status'
        },
        {
            'name': 'Payment - Owner',
            'utterance': 'I want to pay my premium'
        },
        {
            'name': 'Claim Status - Third Party',
            'utterance': "I'm calling to check on my mother's claim"
        },
        {
            'name': 'Agent Request',
            'utterance': 'I need to speak to an agent'
        },
        {
            'name': 'Coverage Inquiry',
            'utterance': "What's covered under my policy?"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n\n{'#'*80}")
        print(f"TEST CASE {i}: {test['name']}")
        print(f"{'#'*80}\n")
        
        simulator = ContactFlowSimulator(str(flow_path))
        result = simulator.run(test['utterance'])
        
        input("\nPress Enter to continue to next test...\n")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Simulate Amazon Connect contact flow')
    parser.add_argument('--flow', default='1_LTC_Retail_Entry_AI_Enhanced.json', help='Contact flow JSON file')
    parser.add_argument('--utterance', help='Customer utterance to test')
    parser.add_argument('--test-all', action='store_true', help='Run all test scenarios')
    
    args = parser.parse_args()
    
    if args.test_all:
        run_test_scenarios()
    elif args.utterance:
        simulator = ContactFlowSimulator(args.flow)
        simulator.run(args.utterance)
    else:
        print("Please provide --utterance or use --test-all")
        print("\nExample: python flow_simulator.py --utterance 'I need to check my claim status'")
