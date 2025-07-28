/**
 * OWASP Nest - Root Entry Point
 * 
 * This is a monorepo containing:
 * - frontend/: Next.js frontend application
 * - backend/: Django backend application
 * - docs/: Documentation
 * - schema/: JSON schema definitions
 * 
 * For development:
 * - Frontend: cd frontend && npm run dev
 * - Backend: cd backend && python manage.py runserver
 * 
 * This file serves as the main entry point to satisfy package.json requirements.
 */

module.exports = {
  name: 'OWASP Nest',
  description: 'A comprehensive platform for managing OWASP projects, chapters, and community resources',
  structure: {
    frontend: './frontend',
    backend: './backend',
    docs: './docs',
    schema: './schema'
  },
  scripts: {
    frontend: 'cd frontend && npm run dev',
    backend: 'cd backend && python manage.py runserver',
    docs: 'cd docs && mkdocs serve'
  }
}
