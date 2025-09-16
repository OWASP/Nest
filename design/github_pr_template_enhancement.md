# GitHub PR Template Enhancement Design Document

## Overview
Extend the `github_create_pr.py` Django management command to use Jinja templates for generating standardized PR bodies for OWASP Schema implementation initiative.

## Requirements

### Functional Requirements
1. **Template-based PR Bodies**: Use Jinja2 templates to generate PR body content
2. **OWASP Schema Context**: All PRs should indicate they're part of the OWASP Schema implementation
3. **Entity Flexibility**: Template should work for projects, chapters, and committees
4. **Contact Information**: Include references to #project-nest Slack channel and Arkadii Yakovets (@arkid15r)
5. **Customization**: Allow entity-specific values (name, repository path, etc.)

### Non-Functional Requirements
1. **Maintainability**: Template should be easily editable without code changes
2. **Extensibility**: Easy to add new entity types or modify content
3. **Consistency**: All automated PRs should have consistent formatting and information

## Technical Design

### File Structure
```
backend/apps/owasp/templates/schema/
├── pr_body.jinja          # Main PR body template
└── (future entity-specific templates)
```

### Template Variables
- `entity_type`: Type of OWASP entity (project, chapter, committee)
- `entity_name`: Name of the specific entity
- `repository_path`: Full repository path (e.g., "OWASP/example-project")
- `schema_version`: OWASP Schema version being used
- `generated_date`: Date when PR was generated
- `additional_context`: Any additional context specific to the entity

### Command Extensions
1. Add `--template` argument to specify template path
2. Add `--template-vars` argument for custom template variables
3. Integrate Jinja2 template rendering into the command
4. Maintain backward compatibility with existing `--body` argument

### Template Content Structure
1. **Header**: Clear indication of automated generation
2. **Context**: OWASP Schema implementation initiative
3. **Entity Information**: Specific details about the entity
4. **Changes**: Description of what's being updated
5. **Contact**: Support information and channels
6. **Footer**: Additional context and links

## Implementation Plan

### Phase 1: Template Creation
1. Create directory structure for templates
2. Implement base PR body template
3. Add Jinja2 dependency if not present

### Phase 2: Command Extension
1. Add template-related command arguments
2. Implement template rendering logic
3. Add template variable parsing
4. Maintain backward compatibility

### Phase 3: Testing and Validation
1. Test with different entity types
2. Validate template rendering
3. Ensure proper error handling

## Dependencies
- Jinja2 (for template rendering)
- Existing GitHub API integration
- Django management command framework

## Future Enhancements
- Entity-specific template variants
- Template validation
- Dynamic template selection based on entity type
- Template versioning
