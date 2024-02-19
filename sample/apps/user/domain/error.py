from spakky.domain.error import DomainValidationError


class UserAlreadyExistsError(DomainValidationError):
    message = "이미 존재하는 사용자입니다."


class EmailValidationFailedError(DomainValidationError):
    message = "유효하지 않은 이메일 형식입니다."


class AuthenticationFailedError(DomainValidationError):
    message = "알 수 없는 사용자 또는 비밀번호입니다."
