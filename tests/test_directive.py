from sphinx_dynamic_command.directive import DynamicCommandDirective


def test_directive_registered_importable():
    assert DynamicCommandDirective.has_content is True

