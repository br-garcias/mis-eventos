import redis
from pymongo import MongoClient

from modules.shared.domain.security.password_hasher import PasswordHasher
from modules.shared.domain.security.token_service import TokenService
from modules.shared.infrastructure.persistence.mongo.mongo_client_factory import MongoClientFactory
from modules.shared.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from modules.shared.infrastructure.security.jwt_token_service import JwtTokenService

from apps.api.config import JWT_SECRET, JWT_ISSUER, MONGO_URL, VALKEY_URL

password_hasher: PasswordHasher = BcryptPasswordHasher()
token_service:   TokenService   = JwtTokenService(secret=JWT_SECRET, issuer=JWT_ISSUER)
mongo_client:    MongoClient    = MongoClientFactory.create_client("shared", MONGO_URL)
valkey_client:   redis.Redis    = redis.Redis.from_url(VALKEY_URL, decode_responses=True)
