"""
Generates a self-signed SSL cert on first run, caches it in the user's temp dir.
"""

import os
import tempfile


def generate_self_signed_cert() -> tuple[str, str]:
    """
    Returns (cert_path, key_path).
    Reuses existing files if already generated this session.
    """
    tmp = tempfile.gettempdir()
    cert = os.path.join(tmp, "voxbridge.crt")
    key = os.path.join(tmp, "voxbridge.key")

    if os.path.exists(cert) and os.path.exists(key):
        return cert, key

    import datetime
    import ipaddress

    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID

    # Generate key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend(),
    )

    # Build cert
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, "voxbridge.local"),
        ]
    )

    cert_obj = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=3650))
        .add_extension(
            x509.SubjectAlternativeName(
                [
                    x509.DNSName("localhost"),
                    x509.DNSName("voxbridge.local"),
                    x509.IPAddress(ipaddress.IPv4Address("0.0.0.0")),
                ]
            ),
            critical=False,
        )
        .sign(private_key, hashes.SHA256(), default_backend())
    )

    # Write files
    with open(key, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    with open(cert, "wb") as f:
        f.write(cert_obj.public_bytes(serialization.Encoding.PEM))

    print(f"[SSL] Certificate generated: {cert}")
    return cert, key
