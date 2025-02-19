from typing import final

from spakky.core.error import AbstractSpakkyCoreError


@final
class DecryptionFailedError(AbstractSpakkyCoreError):
    message = "Decryption failed. Check secret key or cipher message."


@final
class KeySizeError(AbstractSpakkyCoreError):
    message = "Invalid key size."


@final
class PrivateKeyRequiredError(AbstractSpakkyCoreError):
    message = "Private key is required to decrypt or sign."


@final
class CannotImportAsymmetricKeyError(AbstractSpakkyCoreError):
    message = "Cannot import asymmetric key."


@final
class InvalidJWTFormatError(AbstractSpakkyCoreError):
    message = "parameter 'token' is not a valid data (which has 3 separated values.)"


@final
class JWTDecodingError(AbstractSpakkyCoreError):
    message = "parameter 'token' is not a valid data (json decoding error.)"


@final
class JWTProcessingError(AbstractSpakkyCoreError):
    message = "Something went wrong to process JWT token"
