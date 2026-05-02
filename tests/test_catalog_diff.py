from core.catalog_diff import diff_refs


def test_catalog_diff_same_ref():
    report = diff_refs("HEAD", "HEAD")
    assert report["added"] == []
    assert report["removed"] == []
