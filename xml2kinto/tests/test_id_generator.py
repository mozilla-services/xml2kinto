from xml2kinto.id_generator import create_id


def test_create_id():
    """It should handle strings, list, int and dict."""
    assert create_id({
        "foo": "bar",
        "from": {
            "first_name": "toto",
            "age": 15,
            "children": ["foo", "bar", "foobar"]
        }
    }) == 'ef636b94-97a2-3c5e-5a64-22e23cf28e8f'
