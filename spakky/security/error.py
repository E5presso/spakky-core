from typing import final

from spakky.core.error import SpakkyCoreError


@final
class DecryptionFailedError(SpakkyCoreError):
    message = "Decryption failed. Check secret key or cipher message."


@final
class KeySizeError(SpakkyCoreError):
    message = "Invalid key size."


@final
class PrivateKeyRequiredError(SpakkyCoreError):
    message = "Private key is required to decrypt or sign."


@final
class CannotImportAsymmetricKeyError(SpakkyCoreError):
    message = "Cannot import asymmetric key."


@final
class InvalidJWTFormatError(SpakkyCoreError):
    message = "parameter 'token' is not a valid data (which has 3 separated values.)"


@final
class JWTDecodingError(SpakkyCoreError):
    message = "parameter 'token' is not a valid data (json decoding error.)"


@final
class JWTProcessingError(SpakkyCoreError):
    message = "Something went wrong to process JWT token"
