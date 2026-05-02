from core.catalog_signature import sign_catalog, verify_signature


def test_sign_and_verify(tmp_path):
    catalog = tmp_path / "cat.json"
    sig = tmp_path / "cat.sig"
    catalog.write_text('{"a":1}', encoding="utf-8")
    secret = "s3cr3t"
    sig.write_text(sign_catalog(catalog, secret), encoding="utf-8")
    assert verify_signature(catalog, sig, secret) is True
