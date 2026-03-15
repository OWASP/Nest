def calculate_score(merged_prs, reviews, issues, is_leader=False):
    score = 0
    score += merged_prs * 10
    score += reviews * 5
    score += issues * 2
    if is_leader:
        score += 50
    return score

def get_tier(score):
    if score >= 100:
        return "Gold"
    elif score >= 50:
        return "Silver"
    elif score >= 10:
        return "Bronze"
    else:
        return "None"

if __name__ == "__main__":
    score = calculate_score(merged_prs=3, reviews=4, issues=5)
    tier = get_tier(score)

    print("Score:", score)
    print("Tier:", tier)