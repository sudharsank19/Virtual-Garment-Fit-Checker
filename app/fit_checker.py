def check_fit(user, garment):
    fit_result = {}
    for key in user:
        if key not in garment:
            continue
        diff = garment[key] - user[key]
        if abs(diff) <= 2:
            fit_result[key] = "Good Fit"
        elif diff > 2:
            fit_result[key] = "Loose"
        else:
            fit_result[key] = "Tight"
    return fit_result
