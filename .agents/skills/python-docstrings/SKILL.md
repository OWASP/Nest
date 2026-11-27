---
name: python-docstrings
description: Use when writing or reviewing Python docstrings. Always use when writing python code.
---

# OWASP Nest Docstring Conventions

Docstrings in this project follow the Google Style Guide plus a few phrasing rules of its own.

The rules below are exact, not suggestions.

## 1. Summary Lines (The First Line)

The first line of any docstring is the summary. Its phrasing depends on what is being documented.

### Module (File-level) and Class Docstrings

**Rule:** Use **descriptive noun phrases**.
**Avoid:** Never use action verbs or the command voice for files and classes.
**Avoid:** Do not list internal capabilities or implementation details (e.g., "Manage health checks and containers"). Keep it broad.

- **Correct (Module):** `"""Terraform test runner utilities."""`
- **Incorrect:** `"""Discover and execute Terraform module tests."""`
- **Correct (Class):** `"""LocalStack container manager."""`
- **Incorrect:** `"""Manage LocalStack health checks and container lifecycle."""`

### Method, Function, and Property Docstrings

**Rule:** Use the **imperative mood** (command voice). This applies to standard methods, `@classmethod`, `@staticmethod`, and `@property` getters.
**Avoid:** Never use descriptive noun phrases or third-person verbs (like "Returns" or "Initializes").

- **Correct:** `"""Initialize the Terraform test runner."""`
- **Incorrect:** `"""Initializes the Terraform test runner."""`
- **Correct (Property):** `"""Return the absolute path to a command."""`
- **Incorrect (Property):** `"""Returns the absolute path to a command."""`

### `__init__` Methods

**Rule:** Keep the summary strictly to `"Initialize the [noun phrase]."`
**Rule:** If the method takes parameters, document them in an `Args:` block.
**Rule:** Without parameters, the docstring is one line, plus a `Raises:` block if there is an exception to document.
**Rule:** `__init__` methods must never include a `Returns:` block.
**Avoid:** Do not explain implementation details (e.g., "Wire collaborators together" or "Set up the dictionary mapping").

## 2. Formatting and Spacing

**Rule:** If a docstring contains Google Style blocks (`Args:`, `Returns:`, `Raises:`), there must be exactly one blank line between the summary line and the first block.
**Rule:** There must be exactly one blank line before the closing `"""` if the docstring contains any Google Style blocks. Single-line docstrings do not have blank lines.

- **Correct (Multi-line with blocks):**

  ```python
  def start(self, image: str) -> None:
      """Start a LocalStack container.

      Args:
          image (str): The Docker image reference to start.

      Raises:
          TestRunnerError: If the container fails to start.

      """
  ```

- **Correct (Single-line without blocks):**

  ```python
  def cleanup(self) -> None:
      """Clean up temporary override files."""
  ```

## 3. Google Style Blocks

Include each Google Style block only when it applies: `Args:` for parameters, `Returns:` for documented return values, and `Raises:` for documented exceptions.

### The `Args:` Block

**Rule 1: Format**
Arguments must be formatted as `name (type): Description.`.

**Rule 2: Optional Arguments (`None`)**
If a parameter is typed as `type | None = None`, **do not** use `| None` in the docstring type definition. Instead, use the word `optional` inside the parentheses.

- **Correct:**

  ```python
  Args:
      commands (CommandRunner, optional): Command runner instance.
  ```

- **Incorrect:**

  ```python
  Args:
      commands (CommandRunner | None): Command runner instance.
  ```

**Rule 3: State the default**
If an argument is optional or has a default, end its description with `Defaults to ...`.

- **Correct:**

  ```python
  Args:
      host (str, optional): The host address for LocalStack. Defaults to
          the LOCALSTACK_HOST environment variable or localhost.
  ```

### The `Returns:` Block

**Rule 1: Format**
Return values must be formatted as `type: Description.`.

- **Correct:**

  ```python
  Returns:
      list[str]: A sorted list of matching test filenames.
  ```

**Rule 2: Skip redundant boolean returns**
If a method returns a boolean and its summary starts with `"Return whether..."` or `"Check if..."`, **do not** include a `Returns:` block. It is overly verbose and redundant.
Add the block only when the conditions are too complex for the summary alone.

- **Correct (No Returns block needed):**

  ```python
  def healthy(self) -> bool:
      """Return whether the LocalStack health endpoint responds successfully."""
      # ...
  ```

- **Incorrect (Too verbose):**

  ```python
  def healthy(self) -> bool:
      """Return whether the LocalStack health endpoint responds successfully.

      Returns:
          bool: True if the endpoint responds successfully, False otherwise.
      """
  ```

### The `Raises:` Block

**Rule 1: Format**
Exceptions must be formatted as `ExceptionName: Description.`. The description should usually begin with `"If..."`.

- **Correct:**

  ```python
  Raises:
      TestRunnerError: If the container fails to start.
      MissingAuthTokenError: If the LOCALSTACK_AUTH_TOKEN is not set.
  ```

## 4. General Best Practices

- **No implementation details:** A docstring explains the *contract* (What does it do? What goes in? What comes out?), never *how* the code achieves it.
- **Broad summaries:** Do not write summaries so specific that they break when the function grows (e.g., drop `"for integration tests"` when the tool serves more than one case).
