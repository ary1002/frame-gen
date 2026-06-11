from app.tts.elevenlabs import collapse_to_words


def test_simple_sentence():
    chars = list("hello world")
    starts = [i * 0.05 for i in range(len(chars))]
    ends = [(i + 1) * 0.05 for i in range(len(chars))]
    result = collapse_to_words(chars, starts, ends)
    assert len(result) == 2
    assert result[0].word == "hello"
    assert result[0].start_s == pytest.approx(0.0)
    assert result[0].end_s == pytest.approx(0.25)
    assert result[1].word == "world"


def test_multiple_spaces():
    """Multiple consecutive spaces should not create empty word entries."""
    chars = list("hi  there")
    starts = [i * 0.1 for i in range(len(chars))]
    ends = [(i + 1) * 0.1 for i in range(len(chars))]
    result = collapse_to_words(chars, starts, ends)
    assert len(result) == 2
    assert result[0].word == "hi"
    assert result[1].word == "there"


def test_empty_input():
    assert collapse_to_words([], [], []) == []


def test_single_word():
    chars = list("python")
    starts = [i * 0.1 for i in range(len(chars))]
    ends = [(i + 1) * 0.1 for i in range(len(chars))]
    result = collapse_to_words(chars, starts, ends)
    assert len(result) == 1
    assert result[0].word == "python"


def test_newline_separator():
    """Newlines should act as word separators."""
    chars = list("foo\nbar")
    starts = [i * 0.1 for i in range(len(chars))]
    ends = [(i + 1) * 0.1 for i in range(len(chars))]
    result = collapse_to_words(chars, starts, ends)
    assert len(result) == 2
    assert result[0].word == "foo"
    assert result[1].word == "bar"


import pytest
