# app/ml/shift_optimizer.py


def optimize_shift(predicted_demand, available_staff):

    required_staff = max(1, predicted_demand // 5)

    sorted_staff = sorted(
        available_staff,
        key=lambda x: x["current_assignments"]
    )

    assigned = []

    for staff in sorted_staff:
        if len(assigned) >= required_staff:
            break

        if staff["current_assignments"] < staff["max_hours"]:
            assigned.append(staff["name"])

    return {
        "predicted_demand": predicted_demand,
        "recommended_staff_count": required_staff,
        "assigned_staff": assigned,
        "recommendation_text": f"Assign {', '.join(assigned)} based on predicted load."
    }