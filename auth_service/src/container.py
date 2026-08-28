from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Factory, Singleton
from infrastructure.databases.postgresql.session_manager import DatabaseSessionManager
from infrastructure.kafka.producer import KafkaEventProducer
from infrastructure.repositories.postgresql.uow import PostgreSQLAuthUnitOfWork
from infrastructure.security.jwt_service import JVTTokenService
from settings import settings


class Container(DeclarativeContainer):
    uow_factory = Factory(PostgreSQLAuthUnitOfWork)

    session_manager = Singleton(DatabaseSessionManager)

    token_service = Singleton(
        JVTTokenService,
        private_key=settings.jwt.get_private_key(),
        public_key=settings.jwt.get_public_key(),
        algorithm=settings.jwt.algorithm,
        access_lifetime=settings.jwt.access_lifetime,
    )

    kafka_producer = Singleton(
        KafkaEventProducer,
        bootstrap_servers=settings.kafka.bootstrap_servers,
    )
