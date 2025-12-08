# Test-Driven Development (TDD) Guide

## 1. Introduction

This document serves as a general guide for applying the Test-Driven Development (TDD) methodology to the CryptoSentinel project. As the project grows in scope, this document will be important in helping to build more design and project documentation that guides development.

## 2. What is TDD?

Test-Driven Development (TDD) is a software development process that relies on the repetition of a very short development cycle:

1.  **Write a test:** First, the developer writes an (initially failing) automated test case that defines a desired improvement or new function.
2.  **Run the test:** The developer then runs the test and sees it fail.
3.  **Write the code:** The developer then produces the minimum amount of code to pass the test.
4.  **Run the test again:** The developer runs the test again and sees it pass.
5.  **Refactor the code:** The developer then refactors the new code to acceptable standards.

This process is often referred to as the "Red-Green-Refactor" cycle.

## 3. The TDD Cycle: Red-Green-Refactor

*   **Red:** Write a test that fails. This is the "Red" phase. The test should fail because the feature or function it is testing has not yet been implemented.
*   **Green:** Write the minimum amount of code necessary to make the test pass. This is the "Green" phase. The goal is not to write perfect code, but to get the test to pass as quickly as possible.
*   **Refactor:** Improve the code's design and implementation without changing its behavior. This is the "Refactor" phase. The goal is to clean up the code and make it more maintainable.

## 4. TDD in this Project

For the CryptoSentinel project, we will apply TDD to both the backend and the frontend.

### 4.1. Backend TDD

The backend is a multi-agent AI system built with Python and FastAPI. We will use the `pytest` framework for testing.

When adding a new feature to the backend, such as a new tool for an agent, the TDD process would look like this:

1.  **Red:** Write a `pytest` test for the new tool. The test should call the tool with some sample data and assert that it returns the expected output. The test should fail because the tool has not yet been implemented.
2.  **Green:** Implement the new tool with the minimum amount of code necessary to make the test pass.
3.  **Refactor:** Refactor the tool's implementation to improve its design and readability.

### 4.2. Frontend TDD

The frontend is a React/TypeScript application. We will use the Vitest and React Testing Library for testing.

When adding a new feature to the frontend, such as a new component, the TDD process would look like this:

1.  **Red:** Write a test for the new component. The test should render the component and assert that it displays the expected content. The test should fail because the component has not yet been implemented.
2.  **Green:** Implement the new component with the minimum amount of code necessary to make the test pass.
3.  **Refactor:** Refactor the component's implementation to improve its design and readability.

## 5. Examples and Use Cases

### 5.1. Backend Example: A New Tool for the MarketAnalyst Agent

Let's say we want to add a new tool to the `MarketAnalyst` agent that calculates the Simple Moving Average (SMA) of a token's price.

**1. Red: Write the test**

First, we would write a test for the new tool in `backend/tests/test_tools.py`:

```python
from backend.tools.technical_analysis import CalculateSMATool

def test_calculate_sma_tool():
    # Arrange
    tool = CalculateSMATool()
    data = [1, 2, 3, 4, 5]
    window = 3

    # Act
    result = tool.run(data, window)

    # Assert
    assert result == [2.0, 3.0, 4.0]
```

This test would fail because the `CalculateSMATool` has not yet been implemented.

**2. Green: Write the code**

Next, we would implement the `CalculateSMATool` in `backend/tools/technical_analysis.py`:

```python
import numpy as np

class CalculateSMATool:
    def run(self, data, window):
        return np.convolve(data, np.ones(window), 'valid') / window
```
*Note: This is a simplified implementation for the sake of example.*

Now, the test would pass.

**3. Refactor: Refactor the code**

Finally, we would refactor the code to improve its design and add error handling:

```python
import numpy as np
from pydantic import BaseModel, Field
from backend.tools.base import BaseTool

class CalculateSMAInputs(BaseModel):
    data: list[float] = Field(..., description="A list of numbers.")
    window: int = Field(..., description="The window size for the moving average.")

class CalculateSMATool(BaseTool):
    name: str = "Calculate SMA"
    description: str = "Calculates the Simple Moving Average (SMA) of a list of numbers."
    args_schema = CalculateSMAInputs

    def _run(self, data: list[float], window: int) -> list[float]:
        if window > len(data):
            raise ValueError("Window size cannot be greater than the length of the data.")
        return np.convolve(data, np.ones(window), 'valid') / window
```

### 5.2. Frontend Example: A New Component for Displaying Agent Status

Let's say we want to add a new component to the frontend that displays the status of an agent.

**1. Red: Write the test**

First, we would write a test for the new component in `src/components/AgentStatus.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react';
import AgentStatus from './AgentStatus';

test('renders agent status', () => {
  render(<AgentStatus status="active" />);
  const statusElement = screen.getByText(/active/i);
  expect(statusElement).toBeInTheDocument();
});
```

This test would fail because the `AgentStatus` component has not yet been implemented.

**2. Green: Write the code**

Next, we would implement the `AgentStatus` component in `src/components/AgentStatus.tsx`:

```tsx
interface AgentStatusProps {
  status: string;
}

const AgentStatus = ({ status }: AgentStatusProps) => {
  return <div>{status}</div>;
};

export default AgentStatus;
```

Now, the test would pass.

**3. Refactor: Refactor the code**

Finally, we would refactor the component to improve its design and add styling:

```tsx
import { Badge } from '@/components/ui/badge';

interface AgentStatusProps {
  status: 'active' | 'inactive' | 'error';
}

const AgentStatus = ({ status }: AgentStatusProps) => {
  const statusVariant = {
    active: 'success',
    inactive: 'secondary',
    error: 'destructive',
  }[status];

  return <Badge variant={statusVariant}>{status}</Badge>;
};

export default AgentStatus;
```
