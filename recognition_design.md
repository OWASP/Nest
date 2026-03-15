# Contributor Recognition System

## Goal
Create a tier-based recognition system for OWASP Nest contributors.

## Data Source
Use GitHubUser model:
- contributions_count
- contribution_data

## Scoring Logic
Merged PR -> 10 points  
Review -> 5 points  
Issue -> 2 points  
Leadership role -> +50 bonus

## Tier System
Bronze -> 10+
Silver -> 50+
Gold -> 100+

## Output
Each user gets:
- recognition score
- recognition tier