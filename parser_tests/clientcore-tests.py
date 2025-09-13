from parser.core.utils import recursive_reassignmnent


def test_recursive_reassignment():         
    src = {
        "name": "Parent",
        "value": 42,
        "child": {
            "name": "Child",
            "value": 100,
            "child": {
                "x":2,
                "y":3
            }
        }
    }

    dst = {}

    flat_assignment = {
        "name": "null",
        "value": "null",
        "x": "new_x",
        "y": "new_y"
    }

    recursive_assignment = {
        "child": "sub",
    }

    print(recursive_reassignmnent(flat_assignment, recursive_assignment, src, dst))


if __name__ == "__main__":
    test_recursive_reassignment()