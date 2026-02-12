from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class DocumentationOutput(BaseModel):
    """Structured output for documentation generation."""
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.now, description="Timestamp of generation")
    codebase_path: str = Field(description="Path to analyzed codebase")
    language: str = Field(description="Primary programming language detected")
    
    # Core documentation sections
    readme: str = Field(description="Getting Started guide (README.md content)")
    api_reference: str = Field(description="API Reference documentation (API_REFERENCE.md content)")
    architecture: str = Field(description="Architecture documentation (ARCHITECTURE.md content)")
    examples: str = Field(description="API Examples documentation (EXAMPLES.md content)")
    test_documentation: str = Field(description="Test documentation (TEST_DOCUMENTATION.md content)")
    architecture_diagram: str = Field(description="Mermaid diagram for architecture (diagrams/architecture.mermaid content)")
    
    # Optional metadata
    summary: Optional[str] = Field(default=None, description="Brief summary of codebase")
    total_files: Optional[int] = Field(default=None, description="Total files analyzed")
    total_endpoints: Optional[int] = Field(default=None, description="Total API endpoints documented")
    
    class Config:
        json_schema_extra = {
            "example": {
                "generated_at": "2024-06-15T10:30:00",
                "codebase_path": "/path/to/codebase",
                "language": "java",
                "readme": "# Getting Started...",
                "api_reference": "# API Reference...",
                "architecture": "# Architecture...",
                "examples": "# Examples...",
                "test_documentation": "# Test Documentation...",
                "architecture_diagram": "graph TD...",
                "summary": "Spring Boot REST API with JWT auth",
                "total_files": 25,
                "total_endpoints": 18
            }
        }
    
    def save_to_folder(self, output_dir: str) -> None:
        """
        Save documentation to organized folder structure:
        
        output_dir/
        ├── README.md
        ├── API_REFERENCE.md
        ├── ARCHITECTURE.md
        ├── EXAMPLES.md
        ├── TEST_DOCUMENTATION.md
        └── diagrams/
            └── architecture.mermaid
        """
        import os
        from pathlib import Path
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create diagrams subdirectory
        diagrams_path = output_path / "diagrams"
        diagrams_path.mkdir(parents=True, exist_ok=True)
        
        # Save markdown files
        (output_path / "README.md").write_text(self.readme, encoding="utf-8")
        (output_path / "API_REFERENCE.md").write_text(self.api_reference, encoding="utf-8")
        (output_path / "ARCHITECTURE.md").write_text(self.architecture, encoding="utf-8")
        (output_path / "EXAMPLES.md").write_text(self.examples, encoding="utf-8")
        (output_path / "TEST_DOCUMENTATION.md").write_text(self.test_documentation, encoding="utf-8")
        
        # Save mermaid diagram
        (diagrams_path / "architecture.mermaid").write_text(self.architecture_diagram, encoding="utf-8")
        
        print(f"✅ Documentation saved to {output_path}")
        print(f"   - README.md")
        print(f"   - API_REFERENCE.md")
        print(f"   - ARCHITECTURE.md")
        print(f"   - EXAMPLES.md")
        print(f"   - TEST_DOCUMENTATION.md")
        print(f"   - diagrams/architecture.mermaid")
