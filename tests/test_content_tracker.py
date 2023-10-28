CONTENT = "content"

from werd.content_tracker import ContentTracker


def test_create_file(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "hello.txt"
    p.write_text(CONTENT)

    tracker = ContentTracker(d / ".hash")

    assert tracker.has_changed(p)
    tracker.update(p)
    assert not tracker.has_changed(p)

    p.write_text(CONTENT + " something")
    assert tracker.has_changed(p)
    tracker.update(p)
    assert not tracker.has_changed(p)
