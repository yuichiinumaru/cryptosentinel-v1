import re
from typing import List, Dict, Any

class AgentSpecParser:
    def parse(self, rule_string: str) -> List[Dict[str, Any]]:
        rules = []
        # Use a regex to split the rule string into individual rule blocks.
        rule_blocks = re.split(r'^\s*rule\s+', rule_string, flags=re.MULTILINE)
        for block in rule_blocks:
            if not block.strip():
                continue

            lines = [line.strip() for line in block.strip().split('\n')]
            rule_name = lines[0]

            # Find the sections (trigger, check, enforce)
            trigger_section = self._extract_section('trigger', lines)
            check_section = self._extract_section('check', lines)
            enforce_section = self._extract_section('enforce', lines)

            rules.append({
                'name': rule_name,
                'trigger': self._parse_section_lines(trigger_section),
                'check': self._parse_section_lines(check_section),
                'enforce': self._parse_section_lines(enforce_section),
            })
        return rules

    def _extract_section(self, section_name: str, lines: List[str]) -> List[str]:
        try:
            start_index = lines.index(section_name) + 1
            section_lines = []
            for line in lines[start_index:]:
                if line in ['trigger', 'check', 'enforce', 'end']:
                    break
                if line: # Avoid empty lines
                    section_lines.append(line)
            return section_lines
        except ValueError:
            return []

    def _parse_section_lines(self, lines: List[str]) -> List[Dict[str, Any]]:
        parsed_lines = []
        for line in lines:
            # For now, just parse the line as a name and assume no arguments.
            # This can be extended to support arguments with a more complex regex.
            match = re.match(r'(!)?\s*([a-zA-Z_][a-zA-Z0-9_]*)', line)
            if match:
                negated = bool(match.group(1))
                name = match.group(2)
                parsed_lines.append({'name': name, 'negated': negated, 'args': []})
        return parsed_lines

if __name__ == '__main__':
    rule_string = """
    rule @inspect_large_trades
    trigger
        execute_swap
    check
        is_large_trade
    enforce
        user_inspection
    end
    """

    parser = AgentSpecParser()
    parsed_rules = parser.parse(rule_string)
    import json
    print(json.dumps(parsed_rules, indent=2))
