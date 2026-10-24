from typing import Any


MOCK_DOCUMENTS: list[dict[str, Any]] = [
    {
        "title": "Kebijakan Pengembalian Dana",
        "source_type": "mock",
        "category": "returns",
        "language": "id",
        "product": "general",
        "region": "global",
        "sensitivity": "public",
        "source_url": "https://example.invalid/help/refunds",
        "content": (
            "Pelanggan dapat mengajukan pengembalian dana dalam 14 hari kalender setelah "
            "pembelian jika produk belum digunakan. Sertakan nomor pesanan saat menghubungi "
            "support. Pengajuan yang memenuhi syarat diproses dalam 5 sampai 7 hari kerja. "
            "Contoh ini adalah data sintetis untuk demo."
        ),
    },
    {
        "title": "Informasi Pengiriman",
        "source_type": "mock",
        "category": "shipping",
        "language": "id",
        "product": "general",
        "region": "global",
        "sensitivity": "public",
        "source_url": "https://example.invalid/help/shipping",
        "content": (
            "Pesanan di kota yang sama biasanya tiba dalam 1 sampai 3 hari kerja. "
            "Pengiriman ke wilayah lain biasanya membutuhkan 3 sampai 5 hari kerja. "
            "Nomor pelacakan dikirim setelah pesanan diserahkan ke kurir. "
            "Contoh ini adalah data sintetis untuk demo."
        ),
    },
    {
        "title": "Cara Menghubungi Customer Support",
        "source_type": "mock",
        "category": "support",
        "language": "id",
        "product": "general",
        "region": "global",
        "sensitivity": "public",
        "source_url": "https://example.invalid/help/contact",
        "content": (
            "Tim customer support tersedia pada hari kerja pukul 09.00 sampai 17.00 WIB. "
            "Pelanggan dapat meminta bantuan agent kapan saja melalui tombol Hubungi Agent. "
            "Contoh ini adalah data sintetis untuk demo."
        ),
    },
    {
        "title": "Refund Policy",
        "source_type": "mock",
        "category": "returns",
        "language": "en",
        "product": "general",
        "region": "global",
        "sensitivity": "public",
        "source_url": "https://example.invalid/en/refunds",
        "content": (
            "Customers may request a refund within 14 calendar days of purchase if the "
            "product has not been used. Eligible requests are processed within 5 to 7 "
            "business days. This is synthetic demo content."
        ),
    },
    {
        "title": "Delivery Information",
        "source_type": "mock",
        "category": "shipping",
        "language": "en",
        "product": "general",
        "region": "global",
        "sensitivity": "public",
        "source_url": "https://example.invalid/en/shipping",
        "content": (
            "Orders in the same city usually arrive within 1 to 3 business days. "
            "Delivery to other regions usually takes 3 to 5 business days. "
            "Tracking details are sent when a parcel is handed to the courier. "
            "This is synthetic demo content."
        ),
    },
]


MOCK_CONNECTORS: dict[str, list[dict[str, Any]]] = {
    "confluence": [
        {
            "title": "Confluence Demo: Account Access",
            "content": "Untuk mengatur ulang kata sandi, gunakan tautan Lupa Kata Sandi pada halaman login. Contoh ini adalah data sintetis.",
            "category": "accounts",
            "language": "id",
            "source_type": "confluence",
        }
    ],
    "google_drive": [
        {
            "title": "Google Drive Demo: Billing FAQ",
            "content": "Invoice tersedia di bagian Riwayat Pembayaran setelah transaksi berhasil. Contoh ini adalah data sintetis.",
            "category": "billing",
            "language": "id",
            "source_type": "google_drive",
        }
    ],
}
