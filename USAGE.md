# Usage Guide

## Basic Usage

### Process a Codebase

```bash
# Method 1: Using crewai command
crewai run /path/to/your/codebase

# Method 2: Using Python module
python -m doc_generator.main /path/to/your/codebase

# Method 3: Using installed script
doc_generator /path/to/your/codebase

# If no path provided, processes current directory
crewai run
```

## Input Requirements

- **Folder Path**: Absolute or relative path to the source code directory
- **Valid Directory**: Must be an existing directory (not a file)
- **Readable**: Must have read permissions

## Output

The system generates `technical_documentation.json` in the project root with:

1. **documentation** object containing:
   - Table of contents
   - Architecture overview (summary, components, design patterns, data flow)
   - API reference (organized by module with classes, methods, parameters)
   - Usage examples (with difficulty levels and expected outputs)
   - Getting started guide (prerequisites, installation, quick start, next steps)

2. **metadata** object containing:
   - Files analyzed count
   - Functions and classes documented counts
   - Examples generated count
   - QA issues found
   - Generation timestamp

## Example Workflow

```bash
# 1. Navigate to your project
cd /path/to/doc_generator

# 2. Set up environment (if not done)
export OPENAI_API_KEY=your_key_here
# Or create .env file with OPENAI_API_KEY=your_key_here

# 3. Run on a codebase
crewai run /path/to/another/project

# 4. Check output
cat technical_documentation.json
# Or pretty-print with jq
cat technical_documentation.json | jq .
```

## Supported Languages

### Full Support (AST Parsing)
- **Python**: Complete structural extraction with classes, functions, imports

### Detection Only
- JavaScript/TypeScript
- Java
- Go
- Rust
- C/C++
- C#
- Ruby
- PHP
- Swift
- Kotlin

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_openai_api_key
```

### Customizing Agents

Edit `src/doc_generator/config/agents.yaml` to modify:
- Agent roles
- Goals
- Backstories
- Behavior

### Customizing Tasks

Edit `src/doc_generator/config/tasks.yaml` to modify:
- Task descriptions
- Expected outputs
- Agent assignments

## Advanced Features

### Training

Train the crew for multiple iterations:

```bash
python -m doc_generator.main train 10 training_output.json /path/to/codebase
```

### Testing

Test with evaluation:

```bash
python -m doc_generator.main test 5 gpt-4 /path/to/codebase
```

### Replay

Replay from a specific task:

```bash
python -m doc_generator.main replay task_id_here
```

## Troubleshooting

### Common Issues

1. **"Folder path does not exist"**
   - Verify the path is correct
   - Use absolute paths if relative paths fail
   - Check permissions

2. **"No supported languages detected"**
   - Ensure source files have standard extensions
   - Check that files aren't in ignored directories (.git, node_modules, etc.)

3. **API Key Errors**
   - Verify OPENAI_API_KEY is set
   - Check .env file format
   - Ensure key has sufficient credits

4. **Import Errors**
   - Run `crewai install` to ensure dependencies
   - Check Python version (>=3.10, <3.14)

## Best Practices

1. **Start Small**: Test on a small codebase first
2. **Review Output**: Always review generated documentation
3. **Iterate**: Use training/testing features to improve
4. **Customize**: Adjust agent configs for your needs
5. **Version Control**: Track documentation changes

## Architecture Flow

```
Input: Folder Path
  ↓
[Structural Scanner] → Extract files, modules, classes
  ↓
[Dependency Analyzer] → Map relationships
  ↓
[API Semantics Agent] → Infer meaning
  ↓
[Architecture Agent] → Identify patterns
  ↓
[Documentation Agents] → Generate docs
  ↓
[Evaluation Agent] → Quality check
  ↓
Output: technical_documentation.json
```

## Tips

- **Large Codebases**: May take time - be patient
- **Mixed Languages**: System handles multiple languages
- **Private Code**: System respects visibility (public/private)
- **Test Files**: Automatically detected and handled appropriately
