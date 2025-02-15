# OWASP Project Schema

## Overview

This document describes the JSON schema for OWASP projects. The schema defines the structure and validation rules for project data.

!!! info "Schema Details"
    - **Schema Version**: Draft-07
    - **Schema ID**: `https://raw.githubusercontent.com/OWASP/Nest/main/schema/project.json`
    - **Title**: OWASP Project

## Required Fields

The following fields are mandatory for all project entries:

* `audience`: Target audience for the project
* `leaders`: At least two project leaders
* `level`: Project maturity level
* `name`: Unique project name
* `pitch`: Project pitch
* `tags`: At least three unique tags
* `type`: Project type

## Schema Properties

### Core Properties

#### name
* **Type**: string
* **Description**: The unique name of the project
* **Constraints**: Minimum length of 10 characters
* **Required**: Yes

#### pitch
* **Type**: string
* **Description**: The project pitch
* **Required**: Yes

#### level
* **Type**: number
* **Description**: The numeric level of the project
* **Default**: 2
* **Allowed Values**:
    * `2`: Incubator
    * `3`: Lab
    * `3.5`: Production
    * `4`: Flagship
* **Required**: Yes

#### type
* **Type**: string
* **Description**: The type of the project
* **Allowed Values**:
    * `code`: Code projects
    * `documentation`: Documentation, standards, etc.
    * `tool`: Tools
* **Required**: Yes

#### audience
* **Type**: string
* **Description**: The intended audience for the project
* **Allowed Values**:
    * `breaker`: Security testers and ethical hackers
    * `builder`: Developers and engineers
    * `defender`: Security professionals and defenders
* **Required**: Yes

### License and Documentation

#### license
* **Type**: string
* **Description**: The license of the project
* **Allowed Values**:
```text
AGPL-3.0, Apache-2.0, BSD-2-Clause, BSD-3-Clause, CC-BY-4.0,
CC-BY-SA-4.0, CC0-1.0, EUPL-1.2, GPL-2.0, GPL-3.0, LGPL-2.1,
LGPL-3.0, MIT, MPL-2.0, OTHER
```
* **Required**: No

#### documentation
* **Type**: array of strings (URIs)
* **Description**: URLs to project documentation
* **Constraints**:
    * Minimum 1 item if present
    * All items must be unique
* **Required**: No

### Online Presence

#### website
* **Type**: string
* **Format**: URL
* **Description**: The official website of the project
* **Constraints**: Minimum length of 4 characters
* **Required**: No

#### blog
* **Type**: string
* **Format**: URI
* **Description**: Project's blog URL
* **Required**: No

#### demo
* **Type**: string
* **Format**: URI
* **Description**: URL to the project demo
* **Required**: No

#### mailing-list
* **Type**: string
* **Format**: URI
* **Description**: The mailing list associated with the project
* **Required**: No

### Resources

#### downloads
* **Type**: array of strings (URIs)
* **Description**: List of download URLs
* **Constraints**:
    * Minimum 1 item if present
    * All items must be unique
* **Required**: No

#### events
* **Type**: array of strings (URIs)
* **Description**: Event URLs related to the project
* **Constraints**:
    * Minimum 1 item if present
    * All items must be unique
* **Required**: No

#### tags
* **Type**: array of strings
* **Constraints**:
    * Minimum 3 items
    * All items must be unique
* **Required**: Yes

## Complex Types

### Leader Object

Leaders are individuals who manage the project.

!!! note "Leader Requirements"
    Each project must have at least two leaders.

```json
{
  "github": "username",      // Required
  "email": "user@example.com",
  "name": "Full Name",
  "slack": "slackusername"
}
```

#### Properties

| Property | Type | Required | Description | Pattern/Format |
|----------|------|----------|-------------|----------------|
| github | string | Yes | GitHub username | `^[a-zA-Z0-9-]{1,39}$` |
| email | string | No | Email address | email format |
| name | string | No | Leader's full name | - |
| slack | string | No | Slack username | `^[a-zA-Z0-9._-]{1,21}$` |

### Repository Object

Defines a project repository.

!!! note "Repository Requirements"
    If repositories are included, at least one repository must be specified.

```json
{
  "url": "https://github.com/org/repo",  // Required
  "name": "Repository Name",
  "description": "Repository description",
  "changelog": "https://github.com/org/repo/CHANGELOG.md",
  "code_of_conduct": "https://github.com/org/repo/CODE_OF_CONDUCT.md",
  "contribution_guide": "https://github.com/org/repo/CONTRIBUTING.md"
}
```

#### Properties

| Property | Type | Required | Description | Format |
|----------|------|----------|-------------|---------|
| url | string | Yes | Repository URL | URI |
| name | string | No | Repository name | - |
| description | string | No | Repository description | - |
| changelog | string | No | Link to changelog | - |
| code_of_conduct | string | No | Link to code of conduct | - |
| contribution_guide | string | No | Link to contribution guide | - |

### Sponsor Object

Sponsors are organizations supporting the project.

!!! note "Sponsor Requirements"
    If sponsors are included, at least one sponsor must be specified.

```json
{
  "name": "Sponsor Name",    // Required
  "url": "https://sponsor.example.com",  // Required
  "description": "Sponsor description",
  "logo": "https://sponsor.example.com/logo.png"
}
```

#### Properties

| Property | Type | Required | Description | Format |
|----------|------|----------|-------------|---------|
| name | string | Yes | Sponsor name | - |
| url | string | Yes | Sponsor website | URI |
| description | string | No | Brief description | - |
| logo | string | No | Logo URL | URI |

## Example Project Entry

```json
{
  "name": "OWASP Example Project",
  "pitch": "A security tool for web application testing",
  "level": 3,
  "type": "tool",
  "audience": "breaker",
  "license": "Apache-2.0",
  "website": "https://example.owasp.org",
  "leaders": [
    {
      "github": "leader1",
      "email": "leader1@owasp.org",
      "name": "First Leader",
      "slack": "leader1"
    },
    {
      "github": "leader2",
      "email": "leader2@owasp.org",
      "name": "Second Leader",
      "slack": "leader2"
    }
  ],
  "repositories": [
    {
      "url": "https://github.com/OWASP/example-project",
      "name": "Main Repository",
      "description": "Core project repository"
    }
  ],
  "tags": [
    "web-security",
    "testing",
    "automation"
  ]
}
```

## Validation Rules

### General Rules
* No additional properties are allowed beyond those defined in the schema
* All URIs and URLs must be valid
* Arrays must contain unique items where specified

### Specific Constraints
1. Leaders:
    * Minimum of 2 leaders required
    * Each leader must have a valid GitHub username
    * Slack usernames must follow the pattern: `^[a-zA-Z0-9._-]{1,21}$`

2. Repositories:
    * If present, must have at least 1 repository
    * Each repository must have a valid URL

3. Sponsors:
    * If present, must have at least 1 sponsor
    * Each sponsor must have a name and URL

4. Tags:
    * Minimum of 3 tags required
    * All tags must be unique

!!! tip "Schema Validation"
    Use a JSON Schema validator to ensure your project data complies with these requirements before submission.