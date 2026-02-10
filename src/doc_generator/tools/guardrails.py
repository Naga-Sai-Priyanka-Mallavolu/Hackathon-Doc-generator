"""
Guardrails Tool for Documentation Generator

Provides safety checks, redaction, validation, and quality gates.
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class GuardrailResult(BaseModel):
    """Result of guardrail checks."""
    passed: bool = True
    issues: List[str] = Field(default_factory=list)
    redacted_content: Optional[str] = None
    confidence_score: float = 1.0
    warnings: List[str] = Field(default_factory=list)


class Guardrails:
    """
    Comprehensive guardrails for documentation generation.
    
    Features:
    - Content redaction (API keys, passwords, tokens, PII)
    - Hallucination prevention (confidence scoring)
    - Output validation (JSON/Markdown syntax)
    - Quality gates (coverage, completeness)
    - Uncertainty handling
    """

    # Patterns for sensitive data detection
    SENSITIVE_PATTERNS = [
        # API Keys
        r'(?i)(api[_-]?key|apikey|secret|password|token|auth[_-]?token)[\s]*[:=][\s]*["\']?([a-zA-Z0-9_\-]{16,})["\']?',
        r'(?i)(Bearer\s+)[a-zA-Z0-9_\-\.]+',
        r'(?i)(sk[_-]?live|sk[_-]?test)[a-zA-Z0-9]{20,}',
        # JWT Tokens
        r'(?i)eyJ[a-zA-Z0-9]*\.eyJ[a-zA-Z0-9]*\.[a-zA-Z0-9_\-]*',
        # Database URLs
        r'(?i)(mongodb(\+srv)?|postgres|postgresql|mysql)://[^\s<>"]+',
        r'(?i)redis://[^\s<>"]+',
        # AWS Keys
        r'(?i)AKIA[0-9A-Z]{16}',
        r'(?i)aws[_-]?secret[_-]?key[=][^\s<>"]+',
        # Generic secrets
        r'(?i)secret[=][^\s<>"]+',
        r'(?i)private[_-]?key[=][^\s<>"]+',
    ]

    # Patterns for PII detection
    PII_PATTERNS = [
        # Email addresses
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        # Phone numbers
        r'(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
        # SSN pattern
        r'\d{3}[-\s]?\d{2}[-\s]?\d{4}',
        # Credit card pattern
        r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}',
    ]

    def __init__(self):
        """Initialize guardrails with compiled patterns."""
        self.sensitive_regex = [re.compile(p) for p in self.SENSITIVE_PATTERNS]
        self.pii_regex = [re.compile(p) for p in self.PII_PATTERNS]

    def redact_sensitive_data(self, content: str) -> Tuple[str, List[str]]:
        """
        Redact sensitive data from content.
        
        Returns:
            Tuple of (redacted_content, list_of_redactions)
        """
        redactions = []
        redacted = content

        # Redact sensitive patterns
        for regex in self.sensitive_regex:
            matches = regex.findall(redacted)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[-1]  # Get the actual secret value
                if len(match) >= 8:  # Only redact meaningful secrets
                    placeholder = f"[REDACTED_{len(match)}chars]"
                    redacted = redacted.replace(match, placeholder)
                    redactions.append(f"Redacted sensitive pattern: {match[:8]}...")

        # Redact PII
        for regex in self.pii_regex:
            matches = regex.findall(redacted)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                if '@' in match:  # Email
                    redacted = redacted.replace(match, "[EMAIL_REDACTED]")
                    redactions.append("Redacted email address")
                elif match.replace('-', '').replace(' ', '').isdigit():  # Phone/SSN/CC
                    redacted = redacted.replace(match, "[PII_REDACTED]")
                    redactions.append("Redacted PII")

        return redacted, redactions

    def validate_json(self, content: str) -> GuardrailResult:
        """Validate JSON syntax."""
        import json
        
        issues = []
        warnings = []
        
        try:
            # Try to parse as JSON
            json.loads(content)
            return GuardrailResult(passed=True, issues=[], confidence_score=1.0)
        except json.JSONDecodeError as e:
            # Check if it's meant to be JSON
            if content.strip().startswith('{') or content.strip().startswith('['):
                issues.append(f"Invalid JSON: {str(e)}")
                return GuardrailResult(
                    passed=False,
                    issues=issues,
                    confidence_score=0.5,
                    warnings=["JSON validation failed - content may be malformed"]
                )
        
        return GuardrailResult(passed=True, issues=[], confidence_score=1.0)

    def validate_markdown(self, content: str) -> GuardrailResult:
        """Validate Markdown syntax."""
        issues = []
        warnings = []
        
        # Check for balanced code blocks
        code_block_count = content.count('```')
        if code_block_count % 2 != 0:
            issues.append("Unbalanced code blocks (```)")
        
        # Check for balanced headers
        header_lines = re.findall(r'^(#{1,6})\s', content, re.MULTILINE)
        if header_lines:
            # Check header hierarchy
            prev_level = 0
            for header in header_lines:
                level = len(header)
                if level > prev_level + 1:
                    warnings.append(f"Header level jump from H{prev_level} to H{level}")
                prev_level = level
        
        # Check for empty sections
        sections = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        for section in sections:
            section_name = section[1]
            # Look for content after this section
            section_pattern = rf'^#{{1,6}}\s+{re.escape(section_name)}.*?(?=#{{1,6}}\s+|$)'
            match = re.search(section_pattern, content, re.DOTALL | re.MULTILINE)
            if match:
                section_content = match.group()
                # Check if section has meaningful content
                lines = section_content.split('\n')
                meaningful_lines = [l for l in lines[1:] if l.strip() and not l.strip().startswith('#')]
                if not meaningful_lines:
                    warnings.append(f"Empty section: {section_name}")
        
        passed = len(issues) == 0
        return GuardrailResult(
            passed=passed,
            issues=issues,
            warnings=warnings,
            confidence_score=1.0 if passed else 0.8
        )

    def check_hallucination_risk(self, content: str, source_files: List[str] = None) -> GuardrailResult:
        """
        Check for potential hallucination in content.
        
        Returns:
            GuardrailResult with confidence score and warnings
        """
        issues = []
        warnings = []
        confidence = 1.0
        
        # Check for uncertain phrases
        uncertain_phrases = [
            (r'\bprobably\b', "Use definitive language"),
            (r'\bmight\b', "Use definitive language"),
            (r'\bmaybe\b', "Use definitive language"),
            (r'\bI think\b', "Avoid subjective language"),
            (r'\bseems to\b', "Be more definitive"),
            (r'\bappears to\b', "Be more definitive"),
            (r'\bpossibly\b', "Use definitive language"),
        ]
        
        for pattern, suggestion in uncertain_phrases:
            if re.search(pattern, content, re.IGNORECASE):
                warnings.append(f"Uncertain language: {suggestion}")
                confidence -= 0.05
        
        # Check for invented details
        invented_patterns = [
            (r'\bexample\.com\b', "Generic example domain is acceptable"),
            (r'\bplaceholder\b', "Consider using realistic examples"),
        ]
        
        for pattern, note in invented_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                warnings.append(f"Note: {note}")
        
        # Check for undocumented endpoints
        if re.search(r'(GET|POST|PUT|DELETE|PATCH)\s+/api/', content, re.IGNORECASE):
            if not re.search(r'\(source:', content, re.IGNORECASE):
                warnings.append("API endpoints should reference source locations")
                confidence -= 0.1
        
        passed = confidence >= 0.7
        return GuardrailResult(
            passed=passed,
            issues=issues,
            warnings=warnings,
            confidence_score=confidence
        )

    def check_quality_gates(self, content: str, expected_sections: List[str] = None) -> GuardrailResult:
        """Check quality gates for documentation."""
        issues = []
        warnings = []
        score = 1.0
        
        # Check for required sections
        if expected_sections:
            for section in expected_sections:
                if section.lower() not in content.lower():
                    issues.append(f"Missing section: {section}")
                    score -= 0.1
        
        # Check for empty API descriptions
        api_pattern = r'(\w+)\s+(GET|POST|PUT|DELETE|PATCH)\s+([^\n]+)'
        apis = re.findall(api_pattern, content)
        for api in apis:
            if len(api[2].strip()) < 5:
                warnings.append(f"Short API description: {api[0]} {api[1]}")
                score -= 0.02
        
        # Check for missing parameters
        if 'parameters' in content.lower():
            param_pattern = r'parameter[s]?[:\s]+(none|empty|—|-)'
            if re.search(param_pattern, content, re.IGNORECASE):
                warnings.append("Some endpoints have no parameters documented")
                score -= 0.05
        
        # Check for security annotations
        if 'security' in content.lower() or 'auth' in content.lower():
            if not re.search(r'(role|permission|token|jwt)', content, re.IGNORECASE):
                warnings.append("Security section may need more detail")
                score -= 0.05
        
        passed = score >= 0.7
        return GuardrailResult(
            passed=passed,
            issues=issues,
            warnings=warnings,
            confidence_score=score
        )

    def check_uncertainty_handling(self, content: str) -> GuardrailResult:
        """Check for proper uncertainty handling."""
        issues = []
        warnings = []
        
        # Check if uncertain items are properly marked
        uncertain_markers = ['[unclear]', '[unknown]', '[undocumented]', '[missing]']
        has_uncertain = any(marker in content.lower() for marker in uncertain_markers)
        
        if not has_uncertain:
            # Check if there are any obvious gaps that should be marked
            if re.search(r'\bTODO\b', content, re.IGNORECASE):
                warnings.append("TODO markers found - consider completing these")
        
        # Check for overly confident statements about unclear items
        vague_patterns = [
            (r'\bimplementation\s+details?\s+omitted\b', "Consider documenting implementation details"),
            (r'\bsee\s+source\s+code\b', "Source code reference is acceptable"),
        ]
        
        for pattern, note in vague_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                warnings.append(f"Note: {note}")
        
        return GuardrailResult(
            passed=True,
            issues=issues,
            warnings=warnings,
            confidence_score=0.9
        )

    def validate_output(self, content: str, output_type: str = "markdown") -> GuardrailResult:
        """
        Comprehensive validation of generated output.
        
        Args:
            content: The content to validate
            output_type: Type of output (json, markdown, auto)
        
        Returns:
            GuardrailResult with validation results
        """
        all_issues = []
        all_warnings = []
        confidence_scores = []
        
        # Auto-detect type if needed
        if output_type == "auto":
            stripped = content.strip()
            if stripped.startswith('{') or stripped.startswith('['):
                output_type = "json"
            else:
                output_type = "markdown"
        
        # Redact sensitive data
        redacted_content, redactions = self.redact_sensitive_data(content)
        if redactions:
            all_warnings.extend(redactions)
        
        # Validate format
        if output_type == "json":
            format_result = self.validate_json(content)
        else:
            format_result = self.validate_markdown(content)
        
        all_issues.extend(format_result.issues)
        all_warnings.extend(format_result.warnings)
        confidence_scores.append(format_result.confidence_score)
        
        # Check hallucination risk
        halluc_result = self.check_hallucination_risk(content)
        all_issues.extend(halluc_result.issues)
        all_warnings.extend(halluc_result.warnings)
        confidence_scores.append(halluc_result.confidence_score)
        
        # Check quality gates
        quality_result = self.check_quality_gates(content)
        all_issues.extend(quality_result.issues)
        all_warnings.extend(quality_result.warnings)
        confidence_scores.append(quality_result.confidence_score)
        
        # Check uncertainty handling
        uncertainty_result = self.check_uncertainty_handling(content)
        all_warnings.extend(uncertainty_result.warnings)
        confidence_scores.append(uncertainty_result.confidence_score)
        
        # Calculate overall confidence
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 1.0
        
        # Determine if passed
        passed = len(all_issues) == 0 and overall_confidence >= 0.7
        
        return GuardrailResult(
            passed=passed,
            issues=all_issues,
            redacted_content=redacted_content if redacted_content != content else None,
            confidence_score=overall_confidence,
            warnings=all_warnings
        )

    def filter_code_examples(self, code: str) -> str:
        """Filter and sanitize code examples."""
        # Remove any potential shell injection
        code = re.sub(r'\$\([^\)]+\)', '[COMMAND_REMOVED]', code)
        
        # Remove dangerous patterns
        dangerous = [
            r'import\s+os\s*;?\s*system',
            r'exec\s*\(',
            r'eval\s*\(',
            r'subprocess',
        ]
        
        for pattern in dangerous:
            if re.search(pattern, code, re.IGNORECASE):
                code = re.sub(pattern, '[SAFE_REMOVED]', code, flags=re.IGNORECASE)
        
        return code


# Tool class for CrewAI integration
class GuardrailsTool(BaseTool):
    """CrewAI tool wrapper for Guardrails."""

    name: str = "guardrails"
    description: str = "Safety guardrails for documentation: redaction, validation, quality checks"
    guardrails: Any = None  # Pydantic field

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.guardrails is None:
            object.__setattr__(self, 'guardrails', Guardrails())

    def _run(self, content: str, output_type: str = "markdown") -> str:
        """
        Validate content against guardrails.
        
        Args:
            content: Content to validate
            output_type: Type of output (json, markdown, auto)
        
        Returns:
            JSON string with validation results
        """
        import json
        
        result = self.guardrails.validate_output(content, output_type)
        
        output = {
            "passed": result.passed,
            "confidence_score": result.confidence_score,
            "issues": result.issues,
            "warnings": result.warnings,
            "redacted": result.redacted_content is not None,
        }
        
        return json.dumps(output, indent=2)

    def redact(self, content: str) -> str:
        """Redact sensitive data from content."""
        import json
        
        redacted, redactions = self.guardrails.redact_sensitive_data(content)
        
        output = {
            "redacted_content": redacted,
            "redactions": redactions
        }
        
        return json.dumps(output, indent=2)

    def check_quality(self, content: str, expected_sections: List[str] = None) -> str:
        """Check quality gates."""
        import json
        
        result = self.guardrails.check_quality_gates(content, expected_sections)
        
        output = {
            "passed": result.passed,
            "confidence_score": result.confidence_score,
            "issues": result.issues,
            "warnings": result.warnings,
        }
        
        return json.dumps(output, indent=2)
