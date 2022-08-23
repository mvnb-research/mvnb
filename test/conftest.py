from pytest import fixture


@fixture
def capsys_test(capsys):
    def _capsys_test(text):
        cap = capsys.readouterr()
        assert cap.out == "" or cap.err == ""
        assert (cap.out or cap.err) == text.lstrip()

    return _capsys_test
