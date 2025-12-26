"""
Envelope Encryption Utility

Implements envelope encryption where each data record has its own ephemeral DEK:
- DEK (Data Encryption Key): Unique per record, AES-256-GCM
- KEK (Key Encryption Key): Master key in Cloud KMS
- E(data, DEK) = ciphertext
- E(DEK, KEK) = wrapped_DEK
"""

import os
import json
import base64
from typing import Dict, Any, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from google.cloud import kms_v1


class EnvelopeEncryption:
    """
    Envelope Encryption with Cloud KMS
    
    Mathematical Properties:
    - Cipher: AES-256-GCM (authenticated encryption)
    - Key size: 256 bits = 32 bytes
    - Nonce size: 96 bits = 12 bytes (recommended for GCM)
    - Tag size: 128 bits = 16 bytes
    - Security level: 2^256 against brute force
    """
    
    def __init__(
        self, 
        kms_client: kms_v1.KeyManagementServiceClient,
        project: str,
        location: str,
        key_ring: str,
        crypto_key: str
    ):
        self.kms_client = kms_client
        self.kek_name = (
            f"projects/{project}/locations/{location}/"
            f"keyRings/{key_ring}/cryptoKeys/{crypto_key}"
        )
    
    def encrypt(self, plaintext: Any) -> Tuple[str, str]:
        """
        Encrypt data with envelope encryption
        
        Process:
        1. Generate ephemeral DEK (256-bit random)
        2. Encrypt plaintext with DEK using AES-256-GCM
        3. Encrypt DEK with KEK using Cloud KMS
        4. Return (ciphertext, wrapped_DEK)
        
        Args:
            plaintext: Data to encrypt (will be JSON-serialized)
        
        Returns:
            Tuple of (base64_ciphertext, base64_wrapped_dek)
        """
        # Generate ephemeral DEK (256 bits = 32 bytes)
        dek = AESGCM.generate_key(bit_length=256)
        
        # Serialize plaintext to JSON bytes
        plaintext_bytes = json.dumps(plaintext).encode('utf-8')
        
        # Encrypt plaintext with DEK using AES-256-GCM
        aesgcm = AESGCM(dek)
        nonce = os.urandom(12)  # 96-bit nonce (recommended for GCM)
        ciphertext = aesgcm.encrypt(nonce, plaintext_bytes, None)
        
        # Combine nonce + ciphertext for storage
        ciphertext_with_nonce = nonce + ciphertext
        
        # Encrypt DEK with KEK using Cloud KMS
        encrypt_response = self.kms_client.encrypt(
            request={
                "name": self.kek_name,
                "plaintext": dek
            }
        )
        wrapped_dek = encrypt_response.ciphertext
        
        # Base64 encode for storage
        ciphertext_b64 = base64.b64encode(ciphertext_with_nonce).decode('utf-8')
        wrapped_dek_b64 = base64.b64encode(wrapped_dek).decode('utf-8')
        
        return ciphertext_b64, wrapped_dek_b64
    
    def decrypt(self, ciphertext_b64: str, wrapped_dek_b64: str) -> Any:
        """
        Decrypt data with envelope encryption
        
        Process:
        1. Decrypt wrapped_DEK with KEK using Cloud KMS
        2. Decrypt ciphertext with DEK using AES-256-GCM
        3. Parse and return plaintext
        
        Args:
            ciphertext_b64: Base64-encoded ciphertext
            wrapped_dek_b64: Base64-encoded wrapped DEK
        
        Returns:
            Decrypted plaintext (JSON-parsed)
        """
        # Decode from base64
        ciphertext_with_nonce = base64.b64decode(ciphertext_b64)
        wrapped_dek = base64.b64decode(wrapped_dek_b64)
        
        # Decrypt DEK with KEK using Cloud KMS
        decrypt_response = self.kms_client.decrypt(
            request={
                "name": self.kek_name,
                "ciphertext": wrapped_dek
            }
        )
        dek = decrypt_response.plaintext
        
        # Extract nonce and ciphertext
        nonce = ciphertext_with_nonce[:12]
        ciphertext = ciphertext_with_nonce[12:]
        
        # Decrypt ciphertext with DEK using AES-256-GCM
        aesgcm = AESGCM(dek)
        plaintext_bytes = aesgcm.decrypt(nonce, ciphertext, None)
        
        # Parse JSON and return
        return json.loads(plaintext_bytes.decode('utf-8'))
