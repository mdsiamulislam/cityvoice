def get_civic_rank(score):
    if score >= 800:
        return "Civic Hero", "Top 2%"
    elif score >= 500:
        return "Active Citizen", "Top 10%"
    else:
        return "New Contributor", "Top 50%"