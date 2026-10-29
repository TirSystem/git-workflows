import inspect

from workflow_source import REPO_ROOT, load_script


def test_a_static_lookup_finds_the_attributes_of_the_module():
    view = load_script(REPO_ROOT / "tools" / "english_comments.py", "english_comments_view")
    assert inspect.getattr_static(view, "MAX_FILE_BYTES") == view.MAX_FILE_BYTES


def test_deleting_an_attribute_of_the_view_deletes_it_from_the_module():
    view = load_script(REPO_ROOT / "tools" / "english_comments.py", "english_comments_view")
    view.extra = 1
    del view.extra
    assert not hasattr(view._module, "extra")
