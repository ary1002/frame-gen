import hashlib


def compute_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def test_hash_is_deterministic():
    text = "The quick brown fox jumps over the lazy dog."
    h1 = compute_hash(text)
    h2 = compute_hash(text)
    assert h1 == h2


def test_hash_same_text_multiple_calls():
    text = "Hello, world! This is a test slide for hashing."
    hashes = [compute_hash(text) for _ in range(10)]
    assert len(set(hashes)) == 1


def test_hash_changes_on_single_char_change():
    text_a = "The quick brown fox jumps over the lazy dog."
    text_b = "The quick brown fox jumps over the lazy dot."
    assert compute_hash(text_a) != compute_hash(text_b)


def test_hash_changes_on_appended_char():
    text_a = "Hello world."
    text_b = "Hello world.!"
    assert compute_hash(text_a) != compute_hash(text_b)


def test_hash_is_hex_string():
    text = "Some narration text for a slide."
    h = compute_hash(text)
    assert isinstance(h, str)
    assert len(h) == 64
    int(h, 16)  # Should not raise; valid hex


def test_hash_empty_string_is_deterministic():
    h1 = compute_hash("")
    h2 = compute_hash("")
    assert h1 == h2
    assert len(h1) == 64
