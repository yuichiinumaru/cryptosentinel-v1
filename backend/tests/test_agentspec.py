import unittest
from unittest.mock import Mock, patch
from backend.agentspec.parser import AgentSpecParser
from backend.agentspec.enforcement import AgentSpecEnforcement

class TestAgentSpec(unittest.TestCase):

    def test_parser(self):
        rule_string = """
        rule @test_rule
        trigger
            test_trigger
        check
            is_test_predicate
        enforce
            test_enforcement
        end
        """
        parser = AgentSpecParser()
        parsed_rules = parser.parse(rule_string)

        self.assertEqual(len(parsed_rules), 1)
        rule = parsed_rules[0]
        self.assertEqual(rule['name'], '@test_rule')
        self.assertEqual(rule['trigger'][0]['name'], 'test_trigger')
        self.assertEqual(rule['check'][0]['name'], 'is_test_predicate')
        self.assertEqual(rule['enforce'][0]['name'], 'test_enforcement')

    def test_enforcement_engine(self):
        rules = [
            {
                'name': '@test_rule',
                'trigger': [{'name': 'test_trigger', 'negated': False, 'args': []}],
                'check': [{'name': 'is_test_predicate', 'negated': False, 'args': []}],
                'enforce': [{'name': 'test_enforcement', 'negated': False, 'args': []}]
            }
        ]

        # Mock predicate and enforcement functions
        predicate_map = {'is_test_predicate': Mock(return_value=True)}
        enforcement_map = {'test_enforcement': Mock()}

        engine = AgentSpecEnforcement(rules, predicate_map, enforcement_map)

        # Simulate the agent context with kwargs
        agent_context = {'kwargs': {'amount_in': 1500}}
        engine.enforce('test_trigger', agent_context)

        # Check if the predicate was called with the correct argument
        predicate_map['is_test_predicate'].assert_called_once_with(amount_in=1500)
        # Check if the enforcement function was called
        enforcement_map['test_enforcement'].assert_called_once()

    def test_enforcement_engine_negated_predicate(self):
        rules = [
            {
                'name': '@test_rule',
                'trigger': [{'name': 'test_trigger', 'negated': False, 'args': []}],
                'check': [{'name': 'is_test_predicate', 'negated': True, 'args': []}],
                'enforce': [{'name': 'test_enforcement', 'negated': False, 'args': []}]
            }
        ]

        # Mock predicate and enforcement functions
        predicate_map = {'is_test_predicate': Mock(return_value=False)}
        enforcement_map = {'test_enforcement': Mock()}

        engine = AgentSpecEnforcement(rules, predicate_map, enforcement_map)
        engine.enforce('test_trigger', {})

        # Check if the enforcement function was called
        enforcement_map['test_enforcement'].assert_called_once()

    def test_enforcement_engine_failed_check(self):
        rules = [
            {
                'name': '@test_rule',
                'trigger': [{'name': 'test_trigger', 'negated': False, 'args': []}],
                'check': [{'name': 'is_test_predicate', 'negated': False, 'args': []}],
                'enforce': [{'name': 'test_enforcement', 'negated': False, 'args': []}]
            }
        ]

        # Mock predicate and enforcement functions
        predicate_map = {'is_test_predicate': Mock(return_value=False)}
        enforcement_map = {'test_enforcement': Mock()}

        engine = AgentSpecEnforcement(rules, predicate_map, enforcement_map)
        engine.enforce('test_trigger', {})

        # Check that the enforcement function was NOT called
        enforcement_map['test_enforcement'].assert_not_called()

if __name__ == '__main__':
    unittest.main()
