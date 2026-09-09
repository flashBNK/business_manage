from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Factory, Singleton
from infrastructure.databases.postgresql.session_manager import DatabaseSessionManager
from infrastructure.kafka.consumer.consumer import KafkaEventConsumer
from infrastructure.kafka.producer.producer import KafkaEventProducer
from infrastructure.repositories.postgresql.uow import PostgreSQLTasksUnitOfWork
from infrastructure.security.jwt_verifier import JVTTokenVerifier
from settings import settings


class Container(DeclarativeContainer):
    uow_factory = Factory(PostgreSQLTasksUnitOfWork)

    session_manager = Singleton(DatabaseSessionManager)

    token_verifier = Singleton(
        JVTTokenVerifier,
        public_key=settings.jwt.get_public_key(),
        algorithm=settings.jwt.algorithm,
    )

    kafka_consumer = Singleton(
        KafkaEventConsumer,
        bootstrap_servers=settings.kafka.bootstrap_servers,
        group_id="tasks_service",
        topics=["auth.employee.events"],
    )

    kafka_producer = Singleton(
        KafkaEventProducer,
        bootstrap_servers=settings.kafka.bootstrap_servers,
    )
