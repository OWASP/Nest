# OWASP Chapter Schema

## Overview

This document describes the JSON schema for OWASP chapters. The schema defines the structure and validation rules for chapter data.

!!! info "Schema Details"
    - **Schema Version**: Draft-07
    - **Schema ID**: `https://raw.githubusercontent.com/OWASP/Nest/main/schema/chapter.json`
    - **Title**: OWASP Chapter

## Required Fields

The following fields are mandatory for all chapter entries:

* `country`: Country where the chapter is located
* `leaders`: At least two chapter leaders
* `name`: Unique chapter name
* `tags`: At least three unique tags

## Schema Properties

### Core Properties

#### name
* **Type**: string
* **Description**: The unique name of the chapter
* **Constraints**: Minimum length of 10 characters
* **Required**: Yes

#### country
* **Type**: string
* **Description**: Country where the chapter is located
* **Required**: Yes

#### region
* **Type**: string
* **Description**: Region where the chapter is located
* **Required**: No

### Online Presence

#### website
* **Type**: string
* **Format**: URL
* **Description**: The official website of the chapter
* **Required**: No

#### blog
* **Type**: string
* **Format**: URI
* **Description**: Chapter's blog URL
* **Required**: No

#### meetup-group
* **Type**: string
* **Description**: Meetup group identifier
* **Required**: No

### Events and Tags

#### events
* **Type**: array of strings
* **Format**: Each item must be a valid URI
* **Constraints**:
    * Minimum 1 item
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

Leaders are individuals who manage the chapter.

!!! note "Leader Requirements"
    Each chapter must have at least two leaders.

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

### Sponsor Object

Sponsors are organizations supporting the chapter.

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

## Example Chapter Entry

```json
{
  "name": "OWASP Example Chapter",
  "country": "United States",
  "region": "North America",
  "website": "https://example.owasp.org",
  "meetup-group": "owasp-example",
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
  "sponsors": [
    {
      "name": "Example Sponsor",
      "url": "https://sponsor.example.com",
      "description": "Supporting web security education",
      "logo": "https://sponsor.example.com/logo.png"
    }
  ],
  "tags": [
    "web-security",
    "education",
    "community"
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

2. Sponsors:
    * If present, must have at least 1 sponsor
    * Each sponsor must have a name and URL

3. Tags:
    * Minimum of 3 tags required
    * All tags must be unique

4. Events:
    * If present, must have at least 1 event
    * All event URLs must be unique and valid URIs

!!! tip "Schema Validation"
    Use a JSON Schema validator to ensure your chapter data complies with these requirements before submission.