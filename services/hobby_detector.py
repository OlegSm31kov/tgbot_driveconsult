from data.user_profiles import HOBBIES


def detect_hobby(text: str):
    text = text.lower()

    for hobby_name, hobby_data in HOBBIES.items():
        for keyword in hobby_data["keywords"]:
            if keyword in text:
                return hobby_name

    return None