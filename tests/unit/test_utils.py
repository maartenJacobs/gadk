from gadk import utils


class TestYamlDump:
    def test_aliases_and_anchors_are_not_added(self):
        """
        Assert that PyYaml does not add aliases and anchors for "large" values.

        Github Actions does not support them.
        """

        needs = ["foo", "bar", "baz", "foobar"]
        value = {"1": {"needs": needs}, "2": {"needs": needs}}
        assert utils.dump_yaml(value) == """
'1':
  needs:
  - foo
  - bar
  - baz
  - foobar
'2':
  needs:
  - foo
  - bar
  - baz
  - foobar
""".lstrip()
