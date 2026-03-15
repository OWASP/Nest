# backend/apps/github/recognition.py

PR_POINTS = 10
REVIEW_POINTS = 5
ISSUE_POINTS = 2
LEADERSHIP_BONUS = 50
def calculate_contributor_score(pr_count, review_count, issue_count, leadership=False):
    score = (
        pr_count * PR_POINTS +
        review_count * REVIEW_POINTS +
        issue_count * ISSUE_POINTS
    )

    if leadership:
        score += LEADERSHIP_BONUS

    return score


def get_contributor_tier(score):
    if score >= 100:
        return "Gold"
    elif score >= 50:
        return "Silver"
    elif score >= 10:
        return "Bronze"
    else:
        return "None"