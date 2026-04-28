from dataclasses import dataclass
from datetime import datetime, timezone
from modules.shared.domain.aggregate_root import AggregateRoot
from modules.shared.domain.value_object.id_value_object import IdValueObject
from modules.shared.domain.domain_validation_error import DomainValidationError
from modules.shared.domain.value_object.invalid_argument_error import InvalidArgumentError
from .role_name import RoleName

@dataclass
class Role(AggregateRoot):
    id: IdValueObject
    name: RoleName
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, *, id: str, name: str) -> "Role":
        errors = {}
        
        try:
            role_id = IdValueObject(id)
        except InvalidArgumentError as e:
            errors["id"] = [str(e)]
            
        try:
            role_name = RoleName(name)
        except InvalidArgumentError as e:
            errors["name"] = [str(e)]
            
        if errors:
            raise DomainValidationError(errors)
            
        now = datetime.now(timezone.utc)
        return cls(
            id=role_id,
            name=role_name,
            created_at=now,
            updated_at=now
        )
