"""
Human-in-the-Loop approval system for document_assembler.

Provides an interrupt mechanism that pauses execution after document assembly
is complete but before saving, allowing human operators to:
1. Approve the document as-is
2. Request edits with specific feedback - triggers agent re-run and direct save

Flow:
- [A]pprove: Save documents as-is
- [E]dit: Collect feedback → re-run agents (except code_analyzer) → save directly
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path


class ApprovalStatus(Enum):
    """Status of human approval."""
    APPROVED = "approved"
    EDIT_REQUESTED = "edit_requested"


@dataclass
class HumanApprovalResult:
    """Result of human approval process."""
    status: ApprovalStatus
    feedback: Optional[str] = None


class HumanInTheLoop:
    """
    Human-in-the-Loop approval system for document generation.
    
    Intercepts the document saving process and presents a CLI interface
    for human operators to approve or request edits to the generated documentation.
    
    When "Edit" is selected:
    1. Collects feedback from the user (once)
    2. The main flow re-runs required agents (all except code_analyzer) with feedback
    3. New output is generated and saved directly (no second approval loop)
    
    Usage:
        hitl = HumanInTheLoop()
        sections = {"README.md": "...", "API_REFERENCE.md": "..."}
        result = hitl.request_approval(sections)
        
        if result.status == ApprovalStatus.APPROVED:
            save_documents(sections)
        elif result.status == ApprovalStatus.EDIT_REQUESTED:
            # Re-run agents with feedback, then save
            feedback = result.feedback
            # ... re-run logic in main.py ...
    """
    
    def __init__(self, auto_approve: bool = False):
        """
        Initialize HumanInTheLoop.
        
        Args:
            auto_approve: If True, automatically approve without human input (for testing).
        """
        self.auto_approve = auto_approve
    
    def request_approval(self, sections: Dict[str, str], raw_output: str = "") -> HumanApprovalResult:
        """
        Request human approval for the generated documentation.
        
        Presents a CLI interface showing document summaries and prompts for:
        - [A]pprove: Save documents as-is
        - [E]dit: Request changes with feedback (triggers agent re-run)
        
        Args:
            sections: Dictionary mapping filenames to content
            raw_output: Raw output from document assembler (optional)
            
        Returns:
            HumanApprovalResult with status and feedback (if edit requested)
        """
        if self.auto_approve:
            return HumanApprovalResult(status=ApprovalStatus.APPROVED)
        
        self._display_header()
        self._display_summary(sections)
        
        while True:
            choice = self._prompt_choice(
                "\nWhat would you like to do?",
                ["[A]pprove and save", "[E]dit - request changes (will re-run agents)"],
                default="A"
            ).upper()
            
            if choice in ("A", "APPROVE"):
                return HumanApprovalResult(status=ApprovalStatus.APPROVED)
            
            elif choice in ("E", "EDIT"):
                return self._handle_edit_request()
            
            else:
                print("Invalid choice. Please try again.")
    
    def _display_header(self):
        """Display the approval header."""
        print("\n" + "=" * 70)
        print("HUMAN-IN-THE-LOOP APPROVAL")
        print("=" * 70)
        print("\nDocumentation assembly is complete.")
        print("Please review the summary below before saving.\n")
    
    def _display_summary(self, sections: Dict[str, str]):
        """Display summary of each document section."""
        print("-" * 70)
        print("DOCUMENT SUMMARY")
        print("-" * 70)
        
        for filename, content in sections.items():
            lines = content.split('\n')
            word_count = len(content.split())
            line_count = len(lines)
            
            # Extract first non-empty line as preview
            preview = ""
            for line in lines[:5]:
                stripped = line.strip()
                if stripped and not stripped.startswith('#') and not stripped.startswith('---'):
                    preview = stripped[:80] + "..." if len(stripped) > 80 else stripped
                    break
            
            print(f"\n📄 {filename}")
            print(f"   Lines: {line_count} | Words: {word_count}")
            if preview:
                print(f"   Preview: {preview}")
    
    def _prompt_choice(self, prompt: str, options: list, default: str = None) -> str:
        """
        Prompt user for a choice from options.
        
        Args:
            prompt: The prompt message
            options: List of option strings to display
            default: default: Default value if user presses Enter
            
        Returns:
            User's choice as string
        """
        print(f"\n{prompt}")
        for option in options:
            print(f"  {option}")
        
        if default:
            user_input = input(f"\nChoice [{default}]: ").strip()
            return user_input if user_input else default
        else:
            return input("\nChoice: ").strip()
    
    def _handle_edit_request(self) -> HumanApprovalResult:
        """
        Handle edit request from user.
        
        Collects feedback once and returns it. The main flow will:
        1. Re-run required agents (except code_analyzer) with the feedback
        2. Generate new output and save directly (no second approval)
        
        Returns:
            HumanApprovalResult with EDIT_REQUESTED status and feedback
        """
        print("\n" + "-" * 70)
        print("EDIT REQUEST")
        print("-" * 70)
        print("\nPlease describe what changes you need.")
        print("The agents will re-run with your feedback and save directly.\n")
        
        # Collect feedback once
        print("Enter your feedback (press Enter twice to finish):")
        feedback_lines = []
        while True:
            try:
                line = input("> ")
                if line.strip() == "" and feedback_lines and feedback_lines[-1].strip() == "":
                    # Double empty line - end input
                    break
                feedback_lines.append(line)
            except EOFError:
                break
        
        feedback = "\n".join(feedback_lines).strip()
        
        if not feedback:
            print("\n⚠️  No feedback provided. Returning to approval menu...")
            # Return to approval flow
            return self.request_approval({}, "")
        
        print(f"\n✓ Feedback captured ({len(feedback)} characters)")
        print("The agents will now re-run with your feedback and save the updated documentation.")
        
        return HumanApprovalResult(
            status=ApprovalStatus.EDIT_REQUESTED,
            feedback=feedback
        )


def apply_human_feedback(
    sections: Dict[str, str],
    approval_result: HumanApprovalResult
) -> Dict[str, str]:
    """
    Apply human feedback to document sections.
    
    Note: This function is kept for backwards compatibility.
    In the new flow, feedback is used to re-run agents rather than
    applying manual edits to sections.
    
    Args:
        sections: Original document sections
        approval_result: Result from human approval process
        
    Returns:
        Updated sections with human edits applied (if any)
    """
    if approval_result.status != ApprovalStatus.EDIT_REQUESTED:
        return sections
    
    updated_sections = dict(sections)
    
    if approval_result.edited_sections:
        for filename, new_content in approval_result.edited_sections.items():
            updated_sections[filename] = new_content
            print(f"  ✓ Applied edits to {filename}")
    
    return updated_sections
