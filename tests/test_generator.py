from techpulse.generator import validate_post


def test_validate_post_accepts_normal_post():
    post = "AI is changing IT operations.\n\nH&H IT Solutions sees an opportunity to combine AI and automation.\n\n#AI #ITOperations #Automation"
    assert validate_post(post) == []


def test_validate_post_rejects_missing_hashtags():
    assert "hashtags" in " ".join(validate_post("Short post without tags.")).lower()
