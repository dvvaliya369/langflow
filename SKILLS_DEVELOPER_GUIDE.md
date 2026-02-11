# Skills Developer Quick Start Guide

**Date:** February 11, 2026  
**Audience:** Skill Developers

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Creating Your First Skill](#creating-your-first-skill)
3. [Skill Types](#skill-types)
4. [Publishing](#publishing)
5. [Best Practices](#best-practices)
6. [Examples](#examples)

---

## Getting Started

### Prerequisites

- Langflow >= 1.0.0
- Python >= 3.10
- Node.js >= 18.0.0 (for frontend skills)
- Git

### Installation

```bash
# Install Langflow CLI
pip install langflow

# Verify installation
langflow skills --version
```

---

## Creating Your First Skill

### Step 1: Initialize Skill

```bash
# Create new skill
langflow skills init my-awesome-skill

# Navigate to skill directory
cd my-awesome-skill
```

This creates the following structure:

```
my-awesome-skill/
├── skill.json          # Skill manifest
├── README.md           # Documentation
├── LICENSE             # License file
├── .gitignore          # Git ignore rules
├── components/         # Component skills
├── prompts/            # Prompt skills
├── workflows/          # Workflow skills
├── utils/              # Utility functions
└── tests/              # Test files
```

### Step 2: Edit Manifest

Edit `skill.json`:

```json
{
  "schema_version": "1.0",
  "skill": {
    "id": "your-org/my-awesome-skill",
    "name": "My Awesome Skill",
    "version": "0.1.0",
    "description": "A brief description of what this skill does",
    "author": {
      "name": "Your Name",
      "email": "you@example.com",
      "url": "https://github.com/your-org"
    },
    "license": "MIT",
    "keywords": ["langflow", "skill", "awesome"],
    "category": "Components"
  },
  "compatibility": {
    "langflow": ">=1.0.0 <2.0.0",
    "python": ">=3.10"
  },
  "exports": {
    "components": []
  }
}
```

### Step 3: Develop Your Skill

Choose a skill type and implement it (see [Skill Types](#skill-types) below).

### Step 4: Test Locally

```bash
# Link skill for local development
langflow skills link .

# Test in Langflow
langflow run

# Run tests
langflow skills test
```

### Step 5: Validate

```bash
# Validate manifest and code
langflow skills validate

# Check for security issues
langflow skills security-scan
```

### Step 6: Publish

```bash
# Publish to registry
langflow skills publish

# Or publish to specific registry
langflow skills publish --registry https://skills.sh
```

---

## Skill Types

### 1. Component Skill

Create reusable Langflow components.

**File:** `components/my_component.py`

```python
from lfx.custom import Component
from lfx.io import MessageTextInput, Output
from lfx.schema import Message

class MyComponent(Component):
    """A custom component that processes text."""
    
    display_name = "My Component"
    description = "Process text with custom logic"
    icon = "sparkles"
    
    inputs = [
        MessageTextInput(
            name="input_text",
            display_name="Input Text",
            info="Text to process",
            tool_mode=True
        )
    ]
    
    outputs = [
        Output(
            name="result",
            display_name="Result",
            method="process"
        )
    ]
    
    def process(self) -> Message:
        """Process the input text."""
        processed = self.input_text.upper()
        return Message(text=f"Processed: {processed}")
```

**Manifest Entry:**

```json
{
  "exports": {
    "components": [
      {
        "name": "MyComponent",
        "type": "component",
        "path": "./components/my_component.py",
        "display_name": "My Component",
        "icon": "sparkles"
      }
    ]
  }
}
```

### 2. Prompt Skill

Create reusable prompt templates.

**File:** `prompts/summarize.md`

```markdown
---
name: summarize
version: 1.0.0
variables:
  - document_type: string
  - depth: enum[shallow, medium, deep]
---

You are an expert at summarizing {{document_type}} documents.

Please provide a {{depth}} summary of the following:

{{content}}

Include:
1. Main points
2. Key takeaways
3. Recommendations
```

**Manifest Entry:**

```json
{
  "exports": {
    "prompts": [
      {
        "name": "summarize",
        "path": "./prompts/summarize.md",
        "variables": ["document_type", "depth", "content"]
      }
    ]
  }
}
```

### 3. Workflow Skill

Create complete flow templates.

**File:** `workflows/rag_pipeline.json`

```json
{
  "workflow": {
    "name": "rag-pipeline",
    "version": "1.0.0",
    "description": "Basic RAG implementation",
    "nodes": [
      {
        "id": "input",
        "type": "ChatInput",
        "position": {"x": 100, "y": 100},
        "config": {}
      },
      {
        "id": "retriever",
        "type": "VectorStoreRetriever",
        "position": {"x": 300, "y": 100},
        "config": {
          "top_k": 5
        }
      },
      {
        "id": "llm",
        "type": "ChatOpenAI",
        "position": {"x": 500, "y": 100},
        "config": {
          "model": "gpt-4"
        }
      },
      {
        "id": "output",
        "type": "ChatOutput",
        "position": {"x": 700, "y": 100},
        "config": {}
      }
    ],
    "edges": [
      {"from": "input", "to": "retriever"},
      {"from": "retriever", "to": "llm"},
      {"from": "llm", "to": "output"}
    ]
  }
}
```

**Manifest Entry:**

```json
{
  "exports": {
    "workflows": [
      {
        "name": "rag-pipeline",
        "path": "./workflows/rag_pipeline.json",
        "description": "Complete RAG implementation"
      }
    ]
  }
}
```

### 4. Utility Skill

Create helper functions and utilities.

**File:** `utils/validators.py`

```python
from typing import Any, Dict
from pydantic import BaseModel, ValidationError

def validate_schema(data: Dict[str, Any], schema: BaseModel) -> bool:
    """
    Validate data against a Pydantic schema.
    
    Args:
        data: Data to validate
        schema: Pydantic model to validate against
        
    Returns:
        True if valid, False otherwise
    """
    try:
        schema(**data)
        return True
    except ValidationError:
        return False

def sanitize_text(text: str) -> str:
    """
    Sanitize text input for safe processing.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    # Remove dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text.strip()
```

**Manifest Entry:**

```json
{
  "exports": {
    "utilities": [
      {
        "name": "validators",
        "path": "./utils/validators.py",
        "exports": ["validate_schema", "sanitize_text"]
      }
    ]
  }
}
```

---

## Publishing

### Pre-publish Checklist

- [ ] Manifest is valid (`langflow skills validate`)
- [ ] Tests pass (`langflow skills test`)
- [ ] Documentation is complete (README.md)
- [ ] License file is present
- [ ] Security scan passes (`langflow skills security-scan`)
- [ ] Version follows semantic versioning
- [ ] Changelog is updated

### Publishing Process

```bash
# 1. Ensure you're on main branch
git checkout main

# 2. Update version in skill.json
# Edit skill.json and increment version

# 3. Commit changes
git add .
git commit -m "Release v1.0.0"

# 4. Tag release
git tag v1.0.0
git push origin v1.0.0

# 5. Publish to registry
langflow skills publish

# 6. Verify publication
langflow skills info your-org/my-awesome-skill
```

### Publishing to Multiple Registries

```bash
# Publish to skills.sh
langflow skills publish --registry https://skills.sh

# Publish to private registry
langflow skills publish --registry https://registry.mycompany.com

# Publish to npm (if applicable)
npm publish
```

---

## Best Practices

### 1. Versioning

**Follow Semantic Versioning:**
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes

```bash
# Bug fix
1.0.0 → 1.0.1

# New feature
1.0.1 → 1.1.0

# Breaking change
1.1.0 → 2.0.0
```

### 2. Dependencies

**Specify Version Ranges:**

```json
{
  "dependencies": {
    "python": {
      "langchain": ">=0.1.0 <0.2.0",
      "pydantic": "^2.0.0"
    },
    "skills": {
      "other-skill": "~1.2.0"
    }
  }
}
```

**Version Constraint Operators:**
- `^1.2.3`: Compatible with 1.x.x (>=1.2.3 <2.0.0)
- `~1.2.3`: Compatible with 1.2.x (>=1.2.3 <1.3.0)
- `>=1.2.3`: Minimum version
- `1.2.3`: Exact version

### 3. Security

**Request Minimal Permissions:**

```json
{
  "security": {
    "permissions": [
      {
        "permission": "network.https",
        "scope": "api.openai.com",
        "reason": "Required to call OpenAI API",
        "required": true
      }
    ],
    "sandbox": true
  }
}
```

**Avoid:**
- Requesting unnecessary permissions
- Using `filesystem.write` without good reason
- Executing arbitrary system commands
- Accessing environment variables unnecessarily

### 4. Testing

**Write Comprehensive Tests:**

```python
# tests/test_my_component.py
import pytest
from components.my_component import MyComponent

def test_process_text():
    """Test text processing."""
    component = MyComponent()
    component.input_text = "hello world"
    
    result = component.process()
    
    assert result.text == "Processed: HELLO WORLD"

def test_empty_input():
    """Test with empty input."""
    component = MyComponent()
    component.input_text = ""
    
    result = component.process()
    
    assert result.text == "Processed: "
```

**Test Coverage:**
- Aim for >80% code coverage
- Test edge cases
- Test error handling
- Test with different input types

### 5. Documentation

**README.md Template:**

```markdown
# My Awesome Skill

Brief description of what this skill does.

## Installation

\`\`\`bash
langflow skills install your-org/my-awesome-skill
\`\`\`

## Usage

### Basic Example

\`\`\`python
from langflow.skills import load_skill

skill = load_skill('your-org/my-awesome-skill')
component = skill.get_component('MyComponent')
result = component.process(input_text="Hello")
\`\`\`

### Advanced Example

[More detailed example]

## Configuration

[Configuration options]

## API Reference

[API documentation]

## Contributing

[Contribution guidelines]

## License

MIT
```

### 6. Error Handling

**Provide Clear Error Messages:**

```python
def process(self) -> Message:
    """Process input with error handling."""
    try:
        if not self.input_text:
            raise ValueError("Input text cannot be empty")
        
        result = self._process_internal(self.input_text)
        return Message(text=result)
        
    except ValueError as e:
        self.log(f"Validation error: {e}")
        raise
    except Exception as e:
        self.log(f"Unexpected error: {e}")
        raise RuntimeError(f"Failed to process text: {e}")
```

### 7. Performance

**Optimize for Performance:**

```python
# Cache expensive operations
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_operation(input_data: str) -> str:
    """Cached expensive operation."""
    # Expensive computation
    return result

# Use async for I/O operations
async def fetch_data(url: str) -> dict:
    """Async data fetching."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

---

## Examples

### Example 1: Simple Text Processor

```python
# components/text_processor.py
from lfx.custom import Component
from lfx.io import MessageTextInput, DropdownInput, Output
from lfx.schema import Message

class TextProcessor(Component):
    display_name = "Text Processor"
    description = "Process text with various operations"
    icon = "type"
    
    inputs = [
        MessageTextInput(
            name="text",
            display_name="Input Text",
            tool_mode=True
        ),
        DropdownInput(
            name="operation",
            display_name="Operation",
            options=["uppercase", "lowercase", "reverse", "count"],
            value="uppercase"
        )
    ]
    
    outputs = [
        Output(name="result", display_name="Result", method="process")
    ]
    
    def process(self) -> Message:
        """Process text based on selected operation."""
        text = self.text or ""
        
        if self.operation == "uppercase":
            result = text.upper()
        elif self.operation == "lowercase":
            result = text.lower()
        elif self.operation == "reverse":
            result = text[::-1]
        elif self.operation == "count":
            result = f"Character count: {len(text)}"
        else:
            result = text
        
        return Message(text=result)
```

### Example 2: API Integration

```python
# components/weather_api.py
from lfx.custom import Component
from lfx.io import MessageTextInput, SecretStrInput, Output
from lfx.schema import Message
import aiohttp

class WeatherAPI(Component):
    display_name = "Weather API"
    description = "Fetch weather data from API"
    icon = "cloud"
    
    inputs = [
        MessageTextInput(
            name="city",
            display_name="City",
            tool_mode=True
        ),
        SecretStrInput(
            name="api_key",
            display_name="API Key",
            load_from_db=True
        )
    ]
    
    outputs = [
        Output(name="weather", display_name="Weather", method="fetch_weather")
    ]
    
    async def fetch_weather(self) -> Message:
        """Fetch weather data."""
        url = f"https://api.weather.com/v1/current"
        params = {
            "city": self.city,
            "apikey": self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    temp = data.get("temperature")
                    conditions = data.get("conditions")
                    
                    result = f"Weather in {self.city}: {temp}°F, {conditions}"
                    return Message(text=result)
                else:
                    raise RuntimeError(f"API error: {response.status}")
```

### Example 3: Data Validator

```python
# components/data_validator.py
from lfx.custom import Component
from lfx.io import HandleInput, TableInput, Output
from lfx.schema import Data, DataFrame
from pydantic import BaseModel, ValidationError
from typing import Any, Dict

class DataValidator(Component):
    display_name = "Data Validator"
    description = "Validate data against schema"
    icon = "check-circle"
    
    inputs = [
        HandleInput(
            name="data",
            display_name="Input Data",
            input_types=["Data", "DataFrame"]
        ),
        TableInput(
            name="schema",
            display_name="Validation Schema",
            table_schema=[
                {"name": "field", "type": "str"},
                {"name": "type", "type": "str"},
                {"name": "required", "type": "bool"}
            ]
        )
    ]
    
    outputs = [
        Output(name="valid_data", display_name="Valid Data", method="validate")
    ]
    
    def validate(self) -> Data:
        """Validate data against schema."""
        # Build Pydantic model from schema
        fields = {}
        for row in self.schema:
            field_name = row["field"]
            field_type = self._get_type(row["type"])
            required = row.get("required", False)
            
            if required:
                fields[field_name] = (field_type, ...)
            else:
                fields[field_name] = (field_type, None)
        
        # Create dynamic model
        ValidationModel = type("ValidationModel", (BaseModel,), {
            "__annotations__": fields
        })
        
        # Validate data
        try:
            if isinstance(self.data, Data):
                validated = ValidationModel(**self.data.data)
                return Data(data=validated.dict())
            else:
                raise ValueError("Unsupported data type")
        except ValidationError as e:
            raise ValueError(f"Validation failed: {e}")
    
    def _get_type(self, type_str: str) -> type:
        """Convert string type to Python type."""
        type_map = {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "dict": dict,
            "list": list
        }
        return type_map.get(type_str, str)
```

---

## CLI Reference

### Installation Commands

```bash
# Install skill
langflow skills install <skill-id>[@version]

# Install from git
langflow skills install github:owner/repo

# Install from local
langflow skills install ./path/to/skill

# Link for development
langflow skills link ./path/to/skill
```

### Management Commands

```bash
# List installed skills
langflow skills list

# Show skill info
langflow skills info <skill-id>

# Update skill
langflow skills update <skill-id>

# Uninstall skill
langflow skills uninstall <skill-id>

# Check for updates
langflow skills outdated
```

### Development Commands

```bash
# Initialize new skill
langflow skills init <name>

# Validate skill
langflow skills validate

# Run tests
langflow skills test

# Security scan
langflow skills security-scan

# Publish skill
langflow skills publish
```

### Search Commands

```bash
# Search skills
langflow skills search <query>

# Search by category
langflow skills search --category Prompts

# Search verified only
langflow skills search --verified
```

---

## Getting Help

### Documentation
- **Full Design**: `SKILLS_ECOSYSTEM_DESIGN.md`
- **API Reference**: https://docs.langflow.org/skills/api
- **Examples**: https://github.com/langflow-ai/skills-examples

### Community
- **Discord**: https://discord.gg/langflow
- **GitHub Discussions**: https://github.com/langflow-ai/langflow/discussions
- **Stack Overflow**: Tag `langflow-skills`

### Support
- **Issues**: https://github.com/langflow-ai/langflow/issues
- **Email**: skills@langflow.org

---

## Next Steps

1. **Create Your First Skill**: Follow the [Creating Your First Skill](#creating-your-first-skill) guide
2. **Explore Examples**: Check out example skills in the repository
3. **Join Community**: Connect with other skill developers
4. **Publish**: Share your skill with the community

---

*Document Version: 1.0*  
*Last Updated: February 11, 2026*  
*For: Skill Developers*
