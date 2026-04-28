from modules.roles.domain.role_repository import RoleRepository
from modules.roles.infrastructure.persistence.mongo_role_repository import MongoRoleRepository

from .shared_di import mongo_client

role_repository: RoleRepository = MongoRoleRepository(mongo_client)
