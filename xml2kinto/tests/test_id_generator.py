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
    }) == '45b1dc14-65c4-fe65-9c4f-b8667fb4266a'
