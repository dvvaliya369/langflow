# Langflow Integration Patterns and Best Practices

**Date:** February 11, 2026  
**Version:** 1.0  
**Status:** Technical Guide

---

## Table of Contents

1. [Overview](#overview)
2. [Component Integration Patterns](#component-integration-patterns)
3. [Skill Integration Patterns](#skill-integration-patterns)
4. [API Integration Patterns](#api-integration-patterns)
5. [Data Integration Patterns](#data-integration-patterns)
6. [Event-Driven Patterns](#event-driven-patterns)
7. [Security Best Practices](#security-best-practices)
8. [Performance Best Practices](#performance-best-practices)
9. [Testing Best Practices](#testing-best-practices)
10. [Deployment Best Practices](#deployment-best-practices)

---

## Overview

This guide provides proven patterns and best practices for integrating with and extending the Langflow ecosystem. Following these patterns ensures reliability, maintainability, and scalability.

### Design Principles

1. **Loose Coupling**: Components should be independent and interchangeable
2. **High Cohesion**: Related functionality should be grouped together
3. **Single Responsibility**: Each component should have one clear purpose
4. **Open/Closed**: Open for extension, closed for modification
5. **Dependency Inversion**: Depend on abstractions, not concretions

---

## Component Integration Patterns

### Pattern 1: Plugin Architecture

**Use Case:** Extend Langflow with custom components without modifying core code

**Implementation:**

```python
# Base component interface
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class ComponentPlugin(ABC):
    """Base class for all component plugins."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Component name."""
        pass
    
    @property
    @abstractmethod
    def category(self) -> str:
        """Component category."""
        pass
    
    @abstractmethod
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute component logic."""
        pass
    
    @abstractmethod
    def validate(self, config: Dict[str, Any]) -> bool:
        """Validate component configuration."""
        pass

# Custom component implementation
class CustomRAGComponent(ComponentPlugin):
    """Custom RAG component implementation."""
    
    @property
    def name(self) -> str:
        return "Custom RAG"
    
    @property
    def category(self) -> str:
        return "Retrieval"
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        query = inputs.get("query")
        # RAG implementation
        return {"result": f"RAG result for: {query}"}
    
    def validate(self, config: Dict[str, Any]) -> bool:
        required_fields = ["vector_store", "llm"]
        return all(field in config for field in required_fields)

# Plugin registration
from langflow.plugins import register_component

register_component(CustomRAGComponent)
```

**Benefits:**
- No core code modification
- Easy to add/remove components
- Clear separation of concerns
- Testable in isolation

### Pattern 2: Decorator Pattern

**Use Case:** Add functionality to existing components without modifying them

**Implementation:**

```python
from functools import wraps
from typing import Callable, Any
import time
import logging

# Logging decorator
def log_execution(func: Callable) -> Callable:
    """Log component execution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__name__)
        logger.info(f"Executing {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            logger.info(f"Completed {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise
    
    return wrapper

# Performance monitoring decorator
def monitor_performance(func: Callable) -> Callable:
    """Monitor component performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        # Send metrics
        metrics.record("component.execution_time", duration, {
            "component": func.__name__
        })
        
        return result
    
    return wrapper

# Caching decorator
def cache_result(ttl: int = 3600):
    """Cache component results."""
    def decorator(func: Callable) -> Callable:
        cache = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = f"{func.__name__}:{args}:{kwargs}"
            
            # Check cache
            if key in cache:
                cached_value, timestamp = cache[key]
                if time.time() - timestamp < ttl:
                    return cached_value
            
            # Execute and cache
            result = func(*args, **kwargs)
            cache[key] = (result, time.time())
            return result
        
        return wrapper
    return decorator

# Usage
class MyComponent(Component):
    @log_execution
    @monitor_performance
    @cache_result(ttl=1800)
    def process(self, input_data: str) -> str:
        # Component logic
        return f"Processed: {input_data}"
```

**Benefits:**
- Add cross-cutting concerns
- Reusable decorators
- Clean separation
- Easy to enable/disable

### Pattern 3: Factory Pattern

**Use Case:** Create components dynamically based on configuration

**Implementation:**

```python
from typing import Dict, Type
from enum import Enum

class ComponentType(Enum):
    LLM = "llm"
    VECTOR_STORE = "vector_store"
    RETRIEVER = "retriever"
    AGENT = "agent"

class ComponentFactory:
    """Factory for creating components."""
    
    _registry: Dict[ComponentType, Type[Component]] = {}
    
    @classmethod
    def register(cls, component_type: ComponentType, component_class: Type[Component]):
        """Register a component class."""
        cls._registry[component_type] = component_class
    
    @classmethod
    def create(cls, component_type: ComponentType, config: Dict[str, Any]) -> Component:
        """Create a component instance."""
        if component_type not in cls._registry:
            raise ValueError(f"Unknown component type: {component_type}")
        
        component_class = cls._registry[component_type]
        return component_class(**config)
    
    @classmethod
    def create_from_config(cls, config: Dict[str, Any]) -> Component:
        """Create component from configuration."""
        component_type = ComponentType(config.get("type"))
        component_config = config.get("config", {})
        return cls.create(component_type, component_config)

# Register components
ComponentFactory.register(ComponentType.LLM, OpenAIComponent)
ComponentFactory.register(ComponentType.VECTOR_STORE, PineconeComponent)
ComponentFactory.register(ComponentType.RETRIEVER, SemanticRetriever)

# Usage
config = {
    "type": "llm",
    "config": {
        "model": "gpt-4",
        "temperature": 0.7
    }
}

component = ComponentFactory.create_from_config(config)
```

**Benefits:**
- Centralized component creation
- Easy to add new types
- Configuration-driven
- Type-safe

### Pattern 4: Chain of Responsibility

**Use Case:** Process data through a series of components

**Implementation:**

```python
from typing import Optional, Any

class Handler(ABC):
    """Base handler in chain."""
    
    def __init__(self):
        self._next_handler: Optional[Handler] = None
    
    def set_next(self, handler: 'Handler') -> 'Handler':
        """Set next handler in chain."""
        self._next_handler = handler
        return handler
    
    @abstractmethod
    def handle(self, request: Any) -> Any:
        """Handle request."""
        pass

class ValidationHandler(Handler):
    """Validate input data."""
    
    def handle(self, request: Any) -> Any:
        # Validate
        if not self._validate(request):
            raise ValueError("Invalid input")
        
        # Pass to next handler
        if self._next_handler:
            return self._next_handler.handle(request)
        return request
    
    def _validate(self, request: Any) -> bool:
        # Validation logic
        return True

class TransformHandler(Handler):
    """Transform data."""
    
    def handle(self, request: Any) -> Any:
        # Transform
        transformed = self._transform(request)
        
        # Pass to next handler
        if self._next_handler:
            return self._next_handler.handle(transformed)
        return transformed
    
    def _transform(self, request: Any) -> Any:
        # Transformation logic
        return request

class EnrichmentHandler(Handler):
    """Enrich data."""
    
    def handle(self, request: Any) -> Any:
        # Enrich
        enriched = self._enrich(request)
        
        # Pass to next handler
        if self._next_handler:
            return self._next_handler.handle(enriched)
        return enriched
    
    def _enrich(self, request: Any) -> Any:
        # Enrichment logic
        return request

# Build chain
validation = ValidationHandler()
transform = TransformHandler()
enrichment = EnrichmentHandler()

validation.set_next(transform).set_next(enrichment)

# Process request
result = validation.handle(input_data)
```

**Benefits:**
- Flexible processing pipeline
- Easy to add/remove steps
- Single responsibility
- Reusable handlers

---

## Skill Integration Patterns

### Pattern 1: Skill Composition

**Use Case:** Combine multiple skills to create complex functionality

**Implementation:**

```typescript
interface Skill {
  id: string;
  execute(input: any): Promise<any>;
}

class CompositeSkill implements Skill {
  id: string;
  private skills: Skill[];
  
  constructor(id: string, skills: Skill[]) {
    this.id = id;
    this.skills = skills;
  }
  
  async execute(input: any): Promise<any> {
    let result = input;
    
    // Execute skills in sequence
    for (const skill of this.skills) {
      result = await skill.execute(result);
    }
    
    return result;
  }
}

// Usage
const ragSkill = await loadSkill('langchain/rag/basic-rag');
const rerankerSkill = await loadSkill('cohere/rerank/rerank-v3');
const summarizerSkill = await loadSkill('openai/summarize/gpt-4');

const compositeSkill = new CompositeSkill('advanced-rag', [
  ragSkill,
  rerankerSkill,
  summarizerSkill
]);

const result = await compositeSkill.execute({ query: "What is Langflow?" });
```

### Pattern 2: Skill Adapter

**Use Case:** Adapt skills to work with different interfaces

**Implementation:**

```typescript
interface LangflowComponent {
  process(inputs: ComponentInputs): Promise<ComponentOutputs>;
}

class SkillAdapter implements LangflowComponent {
  private skill: Skill;
  private inputMapping: Map<string, string>;
  private outputMapping: Map<string, string>;
  
  constructor(
    skill: Skill,
    inputMapping: Map<string, string>,
    outputMapping: Map<string, string>
  ) {
    this.skill = skill;
    this.inputMapping = inputMapping;
    this.outputMapping = outputMapping;
  }
  
  async process(inputs: ComponentInputs): Promise<ComponentOutputs> {
    // Map component inputs to skill inputs
    const skillInputs = this.mapInputs(inputs);
    
    // Execute skill
    const skillOutputs = await this.skill.execute(skillInputs);
    
    // Map skill outputs to component outputs
    return this.mapOutputs(skillOutputs);
  }
  
  private mapInputs(inputs: ComponentInputs): any {
    const mapped: any = {};
    for (const [componentKey, skillKey] of this.inputMapping) {
      mapped[skillKey] = inputs[componentKey];
    }
    return mapped;
  }
  
  private mapOutputs(outputs: any): ComponentOutputs {
    const mapped: ComponentOutputs = {};
    for (const [skillKey, componentKey] of this.outputMapping) {
      mapped[componentKey] = outputs[skillKey];
    }
    return mapped;
  }
}

// Usage
const skill = await loadSkill('custom/skill');
const adapter = new SkillAdapter(
  skill,
  new Map([['text', 'input_text']]),
  new Map([['result', 'output_text']])
);

// Use as Langflow component
const result = await adapter.process({ text: "Hello" });
```

### Pattern 3: Skill Registry

**Use Case:** Centralized skill discovery and management

**Implementation:**

```typescript
class SkillRegistry {
  private skills: Map<string, Skill> = new Map();
  private metadata: Map<string, SkillMetadata> = new Map();
  
  register(skill: Skill, metadata: SkillMetadata): void {
    this.skills.set(skill.id, skill);
    this.metadata.set(skill.id, metadata);
  }
  
  unregister(skillId: string): void {
    this.skills.delete(skillId);
    this.metadata.delete(skillId);
  }
  
  get(skillId: string): Skill | undefined {
    return this.skills.get(skillId);
  }
  
  search(query: SkillQuery): Skill[] {
    const results: Skill[] = [];
    
    for (const [id, metadata] of this.metadata) {
      if (this.matches(metadata, query)) {
        const skill = this.skills.get(id);
        if (skill) results.push(skill);
      }
    }
    
    return results;
  }
  
  private matches(metadata: SkillMetadata, query: SkillQuery): boolean {
    // Match logic
    if (query.category && metadata.category !== query.category) {
      return false;
    }
    if (query.tags && !query.tags.every(tag => metadata.tags.includes(tag))) {
      return false;
    }
    return true;
  }
}

// Global registry
export const skillRegistry = new SkillRegistry();

// Register skills
skillRegistry.register(ragSkill, {
  category: 'retrieval',
  tags: ['rag', 'vector-search'],
  version: '1.0.0'
});

// Search skills
const retrievalSkills = skillRegistry.search({
  category: 'retrieval'
});
```

---

## API Integration Patterns

### Pattern 1: RESTful API Design

**Best Practices:**

```typescript
// Resource-based URLs
GET    /api/v1/flows              // List flows
POST   /api/v1/flows              // Create flow
GET    /api/v1/flows/{id}         // Get flow
PUT    /api/v1/flows/{id}         // Update flow
DELETE /api/v1/flows/{id}         // Delete flow

// Nested resources
GET    /api/v1/flows/{id}/versions
POST   /api/v1/flows/{id}/execute

// Filtering and pagination
GET    /api/v1/flows?category=rag&page=1&limit=20

// Versioning in URL
GET    /api/v1/flows
GET    /api/v2/flows

// Standard response format
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  metadata?: {
    page?: number;
    limit?: number;
    total?: number;
  };
}

// Error handling
class ApiError extends Error {
  constructor(
    public code: string,
    public message: string,
    public statusCode: number,
    public details?: any
  ) {
    super(message);
  }
}

// Middleware for error handling
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  if (err instanceof ApiError) {
    res.status(err.statusCode).json({
      success: false,
      error: {
        code: err.code,
        message: err.message,
        details: err.details
      }
    });
  } else {
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: 'An unexpected error occurred'
      }
    });
  }
});
```

### Pattern 2: GraphQL API Design

**Best Practices:**

```graphql
# Schema definition
type Flow {
  id: ID!
  name: String!
  description: String
  version: String!
  components: [Component!]!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Component {
  id: ID!
  type: String!
  config: JSON!
  inputs: [Input!]!
  outputs: [Output!]!
}

# Queries
type Query {
  # Get single flow
  flow(id: ID!): Flow
  
  # List flows with filtering
  flows(
    category: String
    tags: [String!]
    limit: Int = 20
    offset: Int = 0
  ): FlowConnection!
  
  # Search flows
  searchFlows(query: String!): [Flow!]!
}

# Mutations
type Mutation {
  # Create flow
  createFlow(input: CreateFlowInput!): Flow!
  
  # Update flow
  updateFlow(id: ID!, input: UpdateFlowInput!): Flow!
  
  # Delete flow
  deleteFlow(id: ID!): Boolean!
  
  # Execute flow
  executeFlow(id: ID!, inputs: JSON!): ExecutionResult!
}

# Subscriptions
type Subscription {
  # Subscribe to flow changes
  flowUpdated(id: ID!): Flow!
  
  # Subscribe to execution updates
  executionUpdated(executionId: ID!): ExecutionStatus!
}

# Pagination
type FlowConnection {
  edges: [FlowEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type FlowEdge {
  node: Flow!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

### Pattern 3: Webhook Integration

**Implementation:**

```typescript
interface WebhookConfig {
  url: string;
  events: string[];
  secret: string;
  headers?: Record<string, string>;
  retryPolicy?: RetryPolicy;
}

interface RetryPolicy {
  maxRetries: number;
  backoff: 'linear' | 'exponential';
  initialDelay: number;
}

class WebhookService {
  async sendWebhook(
    config: WebhookConfig,
    event: string,
    payload: any
  ): Promise<void> {
    // Create signature
    const signature = this.createSignature(payload, config.secret);
    
    // Prepare request
    const headers = {
      'Content-Type': 'application/json',
      'X-Langflow-Event': event,
      'X-Langflow-Signature': signature,
      ...config.headers
    };
    
    // Send with retry
    await this.sendWithRetry(
      config.url,
      payload,
      headers,
      config.retryPolicy
    );
  }
  
  private createSignature(payload: any, secret: string): string {
    const crypto = require('crypto');
    const hmac = crypto.createHmac('sha256', secret);
    hmac.update(JSON.stringify(payload));
    return hmac.digest('hex');
  }
  
  private async sendWithRetry(
    url: string,
    payload: any,
    headers: Record<string, string>,
    retryPolicy?: RetryPolicy
  ): Promise<void> {
    const maxRetries = retryPolicy?.maxRetries || 3;
    let attempt = 0;
    
    while (attempt < maxRetries) {
      try {
        const response = await fetch(url, {
          method: 'POST',
          headers,
          body: JSON.stringify(payload)
        });
        
        if (response.ok) {
          return;
        }
        
        throw new Error(`HTTP ${response.status}`);
      } catch (error) {
        attempt++;
        
        if (attempt >= maxRetries) {
          throw error;
        }
        
        // Calculate delay
        const delay = this.calculateDelay(
          attempt,
          retryPolicy?.backoff || 'exponential',
          retryPolicy?.initialDelay || 1000
        );
        
        await this.sleep(delay);
      }
    }
  }
  
  private calculateDelay(
    attempt: number,
    backoff: 'linear' | 'exponential',
    initialDelay: number
  ): number {
    if (backoff === 'linear') {
      return initialDelay * attempt;
    } else {
      return initialDelay * Math.pow(2, attempt - 1);
    }
  }
  
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Usage
const webhookService = new WebhookService();

// Send webhook on flow execution
await webhookService.sendWebhook(
  {
    url: 'https://example.com/webhook',
    events: ['flow.executed'],
    secret: process.env.WEBHOOK_SECRET!,
    retryPolicy: {
      maxRetries: 3,
      backoff: 'exponential',
      initialDelay: 1000
    }
  },
  'flow.executed',
  {
    flowId: 'flow-123',
    status: 'success',
    result: { ... }
  }
);
```

---

## Data Integration Patterns

### Pattern 1: Repository Pattern

**Use Case:** Abstract data access logic

**Implementation:**

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Generic, TypeVar

T = TypeVar('T')

class Repository(ABC, Generic[T]):
    """Base repository interface."""
    
    @abstractmethod
    async def get(self, id: str) -> Optional[T]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    async def list(self, filters: dict = None) -> List[T]:
        """List entities with optional filters."""
        pass
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create new entity."""
        pass
    
    @abstractmethod
    async def update(self, id: str, entity: T) -> T:
        """Update existing entity."""
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete entity."""
        pass

class FlowRepository(Repository[Flow]):
    """Flow repository implementation."""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def get(self, id: str) -> Optional[Flow]:
        result = await self.db.query(
            "SELECT * FROM flows WHERE id = $1",
            id
        )
        return Flow(**result) if result else None
    
    async def list(self, filters: dict = None) -> List[Flow]:
        query = "SELECT * FROM flows"
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} = ${len(params) + 1}")
                params.append(value)
            query += " WHERE " + " AND ".join(conditions)
        
        results = await self.db.query(query, *params)
        return [Flow(**r) for r in results]
    
    async def create(self, flow: Flow) -> Flow:
        result = await self.db.query(
            """
            INSERT INTO flows (name, description, definition)
            VALUES ($1, $2, $3)
            RETURNING *
            """,
            flow.name,
            flow.description,
            flow.definition
        )
        return Flow(**result)
    
    async def update(self, id: str, flow: Flow) -> Flow:
        result = await self.db.query(
            """
            UPDATE flows
            SET name = $1, description = $2, definition = $3
            WHERE id = $4
            RETURNING *
            """,
            flow.name,
            flow.description,
            flow.definition,
            id
        )
        return Flow(**result)
    
    async def delete(self, id: str) -> bool:
        result = await self.db.execute(
            "DELETE FROM flows WHERE id = $1",
            id
        )
        return result > 0
```

### Pattern 2: Unit of Work

**Use Case:** Manage transactions across multiple repositories

**Implementation:**

```python
class UnitOfWork:
    """Manage database transactions."""
    
    def __init__(self, db: Database):
        self.db = db
        self.flows = FlowRepository(db)
        self.components = ComponentRepository(db)
        self.skills = SkillRepository(db)
    
    async def __aenter__(self):
        await self.db.begin()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.db.rollback()
        else:
            await self.db.commit()
    
    async def commit(self):
        await self.db.commit()
    
    async def rollback(self):
        await self.db.rollback()

# Usage
async def create_flow_with_components(
    flow_data: dict,
    component_data: List[dict]
):
    async with UnitOfWork(db) as uow:
        # Create flow
        flow = await uow.flows.create(Flow(**flow_data))
        
        # Create components
        for comp_data in component_data:
            comp_data['flow_id'] = flow.id
            await uow.components.create(Component(**comp_data))
        
        # Commit transaction
        await uow.commit()
        
        return flow
```

### Pattern 3: CQRS (Command Query Responsibility Segregation)

**Use Case:** Separate read and write operations

**Implementation:**

```python
# Commands (Write operations)
class CreateFlowCommand:
    def __init__(self, name: str, description: str, definition: dict):
        self.name = name
        self.description = description
        self.definition = definition

class UpdateFlowCommand:
    def __init__(self, id: str, name: str, description: str):
        self.id = id
        self.name = name
        self.description = description

# Command handlers
class FlowCommandHandler:
    def __init__(self, repository: FlowRepository):
        self.repository = repository
    
    async def handle_create(self, command: CreateFlowCommand) -> Flow:
        flow = Flow(
            name=command.name,
            description=command.description,
            definition=command.definition
        )
        return await self.repository.create(flow)
    
    async def handle_update(self, command: UpdateFlowCommand) -> Flow:
        flow = await self.repository.get(command.id)
        if not flow:
            raise ValueError(f"Flow {command.id} not found")
        
        flow.name = command.name
        flow.description = command.description
        return await self.repository.update(command.id, flow)

# Queries (Read operations)
class GetFlowQuery:
    def __init__(self, id: str):
        self.id = id

class ListFlowsQuery:
    def __init__(self, category: str = None, limit: int = 20):
        self.category = category
        self.limit = limit

# Query handlers
class FlowQueryHandler:
    def __init__(self, read_model: FlowReadModel):
        self.read_model = read_model
    
    async def handle_get(self, query: GetFlowQuery) -> Optional[FlowDTO]:
        return await self.read_model.get(query.id)
    
    async def handle_list(self, query: ListFlowsQuery) -> List[FlowDTO]:
        return await self.read_model.list(
            category=query.category,
            limit=query.limit
        )

# Usage
command_handler = FlowCommandHandler(flow_repository)
query_handler = FlowQueryHandler(flow_read_model)

# Create flow (write)
flow = await command_handler.handle_create(
    CreateFlowCommand("My Flow", "Description", {...})
)

# Get flow (read)
flow_dto = await query_handler.handle_get(
    GetFlowQuery(flow.id)
)
```

---

## Event-Driven Patterns

### Pattern 1: Event Sourcing

**Use Case:** Store all changes as events

**Implementation:**

```python
from datetime import datetime
from typing import List
import json

class Event:
    """Base event class."""
    
    def __init__(self, aggregate_id: str, event_type: str, data: dict):
        self.aggregate_id = aggregate_id
        self.event_type = event_type
        self.data = data
        self.timestamp = datetime.utcnow()
        self.version = 1

class FlowCreatedEvent(Event):
    def __init__(self, flow_id: str, name: str, description: str):
        super().__init__(
            aggregate_id=flow_id,
            event_type="FlowCreated",
            data={"name": name, "description": description}
        )

class FlowUpdatedEvent(Event):
    def __init__(self, flow_id: str, changes: dict):
        super().__init__(
            aggregate_id=flow_id,
            event_type="FlowUpdated",
            data=changes
        )

class EventStore:
    """Store and retrieve events."""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def append(self, event: Event):
        """Append event to store."""
        await self.db.execute(
            """
            INSERT INTO events (aggregate_id, event_type, data, timestamp, version)
            VALUES ($1, $2, $3, $4, $5)
            """,
            event.aggregate_id,
            event.event_type,
            json.dumps(event.data),
            event.timestamp,
            event.version
        )
    
    async def get_events(self, aggregate_id: str) -> List[Event]:
        """Get all events for aggregate."""
        results = await self.db.query(
            """
            SELECT * FROM events
            WHERE aggregate_id = $1
            ORDER BY version ASC
            """,
            aggregate_id
        )
        
        return [
            Event(
                aggregate_id=r['aggregate_id'],
                event_type=r['event_type'],
                data=json.loads(r['data'])
            )
            for r in results
        ]

class FlowAggregate:
    """Flow aggregate root."""
    
    def __init__(self, id: str):
        self.id = id
        self.name = None
        self.description = None
        self.version = 0
        self.uncommitted_events: List[Event] = []
    
    def create(self, name: str, description: str):
        """Create flow."""
        event = FlowCreatedEvent(self.id, name, description)
        self.apply(event)
        self.uncommitted_events.append(event)
    
    def update(self, name: str = None, description: str = None):
        """Update flow."""
        changes = {}
        if name:
            changes['name'] = name
        if description:
            changes['description'] = description
        
        event = FlowUpdatedEvent(self.id, changes)
        self.apply(event)
        self.uncommitted_events.append(event)
    
    def apply(self, event: Event):
        """Apply event to aggregate."""
        if event.event_type == "FlowCreated":
            self.name = event.data['name']
            self.description = event.data['description']
        elif event.event_type == "FlowUpdated":
            if 'name' in event.data:
                self.name = event.data['name']
            if 'description' in event.data:
                self.description = event.data['description']
        
        self.version += 1
    
    def load_from_history(self, events: List[Event]):
        """Rebuild state from events."""
        for event in events:
            self.apply(event)
```

### Pattern 2: Pub/Sub

**Use Case:** Decouple event publishers and subscribers

**Implementation:**

```typescript
interface EventHandler<T = any> {
  handle(event: T): Promise<void>;
}

class EventBus {
  private handlers: Map<string, Set<EventHandler>> = new Map();
  
  subscribe<T>(eventType: string, handler: EventHandler<T>): void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, new Set());
    }
    this.handlers.get(eventType)!.add(handler);
  }
  
  unsubscribe<T>(eventType: string, handler: EventHandler<T>): void {
    const handlers = this.handlers.get(eventType);
    if (handlers) {
      handlers.delete(handler);
    }
  }
  
  async publish<T>(eventType: string, event: T): Promise<void> {
    const handlers = this.handlers.get(eventType);
    if (!handlers) return;
    
    // Execute handlers in parallel
    await Promise.all(
      Array.from(handlers).map(handler => handler.handle(event))
    );
  }
}

// Event handlers
class FlowExecutedHandler implements EventHandler<FlowExecutedEvent> {
  async handle(event: FlowExecutedEvent): Promise<void> {
    console.log(`Flow ${event.flowId} executed`);
    // Send notification, update metrics, etc.
  }
}

class FlowExecutedMetricsHandler implements EventHandler<FlowExecutedEvent> {
  async handle(event: FlowExecutedEvent): Promise<void> {
    // Record metrics
    await metrics.record('flow.execution', {
      flowId: event.flowId,
      duration: event.duration,
      status: event.status
    });
  }
}

// Usage
const eventBus = new EventBus();

eventBus.subscribe('flow.executed', new FlowExecutedHandler());
eventBus.subscribe('flow.executed', new FlowExecutedMetricsHandler());

// Publish event
await eventBus.publish('flow.executed', {
  flowId: 'flow-123',
  duration: 1500,
  status: 'success'
});
```

---

## Security Best Practices

### 1. Input Validation

```python
from pydantic import BaseModel, validator, Field
from typing import Optional

class FlowInput(BaseModel):
    """Validated flow input."""
    
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    definition: dict
    
    @validator('name')
    def validate_name(cls, v):
        # No special characters
        if not v.replace(' ', '').replace('-', '').replace('_', '').isalnum():
            raise ValueError('Name contains invalid characters')
        return v
    
    @validator('definition')
    def validate_definition(cls, v):
        # Required fields
        if 'nodes' not in v or 'edges' not in v:
            raise ValueError('Definition must contain nodes and edges')
        
        # Validate nodes
        if not isinstance(v['nodes'], list):
            raise ValueError('Nodes must be a list')
        
        return v

# Usage
try:
    flow_input = FlowInput(**request_data)
except ValidationError as e:
    return {"error": str(e)}, 400
```

### 2. Authentication & Authorization

```python
from functools import wraps
from typing import Callable

def require_auth(func: Callable) -> Callable:
    """Require authentication."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Get token from request
        token = request.headers.get('Authorization')
        if not token:
            raise Unauthorized("Missing authentication token")
        
        # Verify token
        user = await auth_service.verify_token(token)
        if not user:
            raise Unauthorized("Invalid token")
        
        # Add user to request context
        request.user = user
        
        return await func(*args, **kwargs)
    
    return wrapper

def require_permission(permission: str):
    """Require specific permission."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Check permission
            if not await auth_service.has_permission(request.user, permission):
                raise Forbidden(f"Missing permission: {permission}")
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

# Usage
@app.post("/api/v1/flows")
@require_auth
@require_permission("flows:create")
async def create_flow(data: FlowInput):
    # Create flow
    pass
```

### 3. Rate Limiting

```python
from datetime import datetime, timedelta
from typing import Optional

class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, rate: int, per: int):
        self.rate = rate  # Number of requests
        self.per = per    # Time period in seconds
        self.buckets: dict = {}
    
    async def is_allowed(self, key: str) -> bool:
        """Check if request is allowed."""
        now = datetime.utcnow()
        
        if key not in self.buckets:
            self.buckets[key] = {
                'tokens': self.rate,
                'last_update': now
            }
        
        bucket = self.buckets[key]
        
        # Refill tokens
        time_passed = (now - bucket['last_update']).total_seconds()
        tokens_to_add = (time_passed / self.per) * self.rate
        bucket['tokens'] = min(self.rate, bucket['tokens'] + tokens_to_add)
        bucket['last_update'] = now
        
        # Check if request allowed
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            return True
        
        return False

# Middleware
rate_limiter = RateLimiter(rate=100, per=60)  # 100 requests per minute

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Get client identifier
    client_id = request.client.host
    
    # Check rate limit
    if not await rate_limiter.is_allowed(client_id):
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded"}
        )
    
    return await call_next(request)
```

---

## Performance Best Practices

### 1. Caching Strategy

```python
from functools import lru_cache
import redis
import pickle

class CacheService:
    """Multi-level caching service."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    @lru_cache(maxsize=1000)
    def get_from_memory(self, key: str) -> Optional[any]:
        """L1 cache: In-memory."""
        # Handled by lru_cache decorator
        pass
    
    async def get_from_redis(self, key: str) -> Optional[any]:
        """L2 cache: Redis."""
        value = await self.redis.get(key)
        if value:
            return pickle.loads(value)
        return None
    
    async def get(self, key: str) -> Optional[any]:
        """Get from cache with fallback."""
        # Try memory cache
        value = self.get_from_memory(key)
        if value:
            return value
        
        # Try Redis cache
        value = await self.get_from_redis(key)
        if value:
            # Populate memory cache
            self.get_from_memory.cache_info()
            return value
        
        return None
    
    async def set(self, key: str, value: any, ttl: int = 3600):
        """Set in cache."""
        # Set in Redis
        await self.redis.setex(
            key,
            ttl,
            pickle.dumps(value)
        )
        
        # Set in memory
        self.get_from_memory(key)
```

### 2. Database Optimization

```python
# Use connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)

# Use batch operations
async def batch_insert(items: List[dict]):
    """Insert multiple items in single query."""
    await db.execute_many(
        "INSERT INTO items (name, value) VALUES ($1, $2)",
        [(item['name'], item['value']) for item in items]
    )

# Use indexes
CREATE INDEX idx_flows_user_id ON flows(user_id);
CREATE INDEX idx_flows_created_at ON flows(created_at DESC);

# Use query optimization
# Bad: N+1 query problem
flows = await db.query("SELECT * FROM flows")
for flow in flows:
    components = await db.query(
        "SELECT * FROM components WHERE flow_id = $1",
        flow.id
    )

# Good: Join query
flows_with_components = await db.query("""
    SELECT f.*, json_agg(c.*) as components
    FROM flows f
    LEFT JOIN components c ON c.flow_id = f.id
    GROUP BY f.id
""")
```

### 3. Async/Await

```python
import asyncio
from typing import List

# Bad: Sequential execution
async def process_flows_sequential(flow_ids: List[str]):
    results = []
    for flow_id in flow_ids:
        result = await process_flow(flow_id)
        results.append(result)
    return results

# Good: Parallel execution
async def process_flows_parallel(flow_ids: List[str]):
    tasks = [process_flow(flow_id) for flow_id in flow_ids]
    results = await asyncio.gather(*tasks)
    return results

# With error handling
async def process_flows_with_errors(flow_ids: List[str]):
    tasks = [process_flow(flow_id) for flow_id in flow_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle errors
    successful = []
    failed = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            failed.append((flow_ids[i], result))
        else:
            successful.append(result)
    
    return successful, failed
```

---

## Testing Best Practices

### 1. Unit Testing

```python
import pytest
from unittest.mock import Mock, patch

class TestFlowService:
    """Test flow service."""
    
    @pytest.fixture
    def flow_service(self):
        """Create flow service instance."""
        repository = Mock()
        return FlowService(repository)
    
    @pytest.mark.asyncio
    async def test_create_flow(self, flow_service):
        """Test flow creation."""
        # Arrange
        flow_data = {
            "name": "Test Flow",
            "description": "Test description"
        }
        
        # Act
        flow = await flow_service.create(flow_data)
        
        # Assert
        assert flow.name == "Test Flow"
        assert flow.description == "Test description"
        flow_service.repository.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_flow_validation_error(self, flow_service):
        """Test flow creation with invalid data."""
        # Arrange
        flow_data = {"name": ""}  # Invalid: empty name
        
        # Act & Assert
        with pytest.raises(ValidationError):
            await flow_service.create(flow_data)
```

### 2. Integration Testing

```python
@pytest.mark.integration
class TestFlowAPI:
    """Test flow API endpoints."""
    
    @pytest.fixture
    async def client(self):
        """Create test client."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_create_flow_endpoint(self, client):
        """Test create flow endpoint."""
        # Arrange
        flow_data = {
            "name": "Test Flow",
            "description": "Test description",
            "definition": {"nodes": [], "edges": []}
        }
        
        # Act
        response = await client.post("/api/v1/flows", json=flow_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data['name'] == "Test Flow"
        assert 'id' in data
```

### 3. End-to-End Testing

```python
@pytest.mark.e2e
class TestFlowExecution:
    """Test complete flow execution."""
    
    @pytest.mark.asyncio
    async def test_rag_flow_execution(self):
        """Test RAG flow end-to-end."""
        # Create flow
        flow = await create_rag_flow()
        
        # Execute flow
        result = await execute_flow(flow.id, {
            "query": "What is Langflow?"
        })
        
        # Verify result
        assert result.status == "success"
        assert result.output is not None
        assert "Langflow" in result.output
```

---

## Deployment Best Practices

### 1. Environment Configuration

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "Langflow"
    debug: bool = False
    
    # Database
    database_url: str
    database_pool_size: int = 20
    
    # Redis
    redis_url: str
    redis_max_connections: int = 50
    
    # Security
    secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600
    
    # API
    api_rate_limit: int = 100
    api_rate_period: int = 60
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Load settings
settings = Settings()
```

### 2. Health Checks

```python
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "storage": await check_storage()
    }
    
    all_healthy = all(checks.values())
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "checks": checks
    }

async def check_database() -> bool:
    """Check database connection."""
    try:
        await db.execute("SELECT 1")
        return True
    except Exception:
        return False
```

### 3. Graceful Shutdown

```python
import signal
import asyncio

class Application:
    """Application with graceful shutdown."""
    
    def __init__(self):
        self.running = True
        self.tasks = []
    
    def setup_signals(self):
        """Setup signal handlers."""
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        signal.signal(signal.SIGINT, self.handle_shutdown)
    
    def handle_shutdown(self, signum, frame):
        """Handle shutdown signal."""
        print("Shutting down gracefully...")
        self.running = False
    
    async def run(self):
        """Run application."""
        self.setup_signals()
        
        # Start background tasks
        self.tasks = [
            asyncio.create_task(self.process_queue()),
            asyncio.create_task(self.cleanup_old_data())
        ]
        
        # Wait for shutdown
        while self.running:
            await asyncio.sleep(1)
        
        # Cancel tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)
        
        # Cleanup
        await self.cleanup()
    
    async def cleanup(self):
        """Cleanup resources."""
        await db.close()
        await redis.close()
```

---

## Conclusion

Following these integration patterns and best practices ensures that your Langflow integrations are:

- **Reliable**: Robust error handling and testing
- **Scalable**: Efficient resource usage and caching
- **Secure**: Proper authentication and validation
- **Maintainable**: Clean code and clear patterns
- **Performant**: Optimized queries and async operations

---

*Document Version: 1.0*  
*Last Updated: February 11, 2026*  
*Authors: Langflow Architecture Team*
