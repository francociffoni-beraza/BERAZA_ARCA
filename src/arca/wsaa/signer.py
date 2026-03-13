from __future__ import annotations

import base64
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import pkcs7



def sign_tra(tra_xml: bytes, cert_path: Path, key_path: Path) -> str:
    cert_data = cert_path.read_bytes()
    key_data = key_path.read_bytes()

    cert = x509.load_pem_x509_certificate(cert_data)
    private_key = serialization.load_pem_private_key(key_data, password=None)

    builder = pkcs7.PKCS7SignatureBuilder().set_data(tra_xml).add_signer(
        cert,
        private_key,
        hashes.SHA256(),
    )

    cms_der = builder.sign(
        serialization.Encoding.DER,
        [pkcs7.PKCS7Options.Binary],
    )

    return base64.b64encode(cms_der).decode("ascii")
