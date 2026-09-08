from uuid import UUID

from domain.task.exceptions import ParticipantNotFound, ParticipantInactive, ParticipantWrongCompany, TaskNotFound
from domain.task.models import CreateTaskDTO, TaskDTO, UpdateTaskDTO, ChangeStatusTaskDTO
from domain.token.models import MemberRoles, TokenDTO
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, Response

from usecases.task.change_status.abstract import AbstractChangeStatusTaskUseCase
from usecases.task.create.abstract import AbstractCreateTaskUseCase
from usecases.task.delete.abstract import AbstractDeleteTaskUseCase
from usecases.task.get.abstract import AbstractGetTaskUseCase
from usecases.task.list.abstract import AbstractListTaskUseCase
from usecases.task.update.abstract import AbstractUpdateTaskUseCase
from ..authorization import require_company_role
from .dependencies import create_task_use_case, get_task_use_case, list_task_use_case, update_task_use_case, \
    change_status_task_use_case, delete_task_use_case
from .models import CreateTaskSchema, TaskSchema, ListTaskSchema, UpdateTaskSchema, ChangeStatusTaskSchema

router = APIRouter(prefix="/companies")


@router.post("/{company_id}/tasks", response_model=TaskSchema)
async def create_task(
    _request: Request,
    company_id: UUID,
    payload: CreateTaskSchema,
    token: TokenDTO = Depends(require_company_role(min_role=MemberRoles.ADMIN)),
    usecase: AbstractCreateTaskUseCase = Depends(create_task_use_case),
) -> JSONResponse:
    dto = CreateTaskDTO(
        author_id=token.subject,
        title=payload.title,
        description=payload.description,
        company_id=company_id,
        responsible_id=payload.responsible_id,
        deadline=payload.deadline,
        estimated_minutes=payload.estimated_minutes,
        watcher_ids=payload.watcher_ids,
        assignee_ids=payload.assignee_ids,
    )

    try:
        task = await usecase.execute(dto=dto)
    except ParticipantNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None
    except ParticipantInactive as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from None
    except ParticipantWrongCompany as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from None

    return JSONResponse(
        _to_schema(task, watcher_ids=payload.watcher_ids, assignee_ids=payload.assignee_ids).model_dump(mode="json"),
        status_code=status.HTTP_201_CREATED,
    )


@router.get("/{company_id}/tasks/{task_id}", response_model=TaskSchema)
async def get_task(
    _request: Request,
    company_id: UUID,
    task_id: UUID,
    usecase: AbstractGetTaskUseCase = Depends(get_task_use_case),
    _token: TokenDTO = Depends(require_company_role(MemberRoles.MEMBER)),
) -> JSONResponse:
    try:
        task = await usecase.execute(company_id=company_id, task_id=task_id)
    except TaskNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None

    return JSONResponse(
        _to_schema(task.task, watcher_ids=task.watcher_ids, assignee_ids=task.assignee_ids).model_dump(mode="json"),
        status_code=status.HTTP_200_OK
    )


@router.get("/{company_id}/tasks", response_model=ListTaskSchema)
async def list_task(
    _request: Request,
    company_id: UUID,
    usecase: AbstractListTaskUseCase = Depends(list_task_use_case),
    _token: TokenDTO = Depends(require_company_role(MemberRoles.MEMBER)),
) -> JSONResponse:
    tasks = await usecase.execute(company_id=company_id)

    content = ListTaskSchema(
        total=len(tasks),
        tasks=[_to_schema(task.task, task.watcher_ids, task.assignee_ids).model_dump(mode="json") for task in tasks]
    )

    return JSONResponse(content.model_dump(mode="json"), status_code=status.HTTP_200_OK)


@router.patch("/{company_id}/tasks/{task_id}", response_model=TaskSchema)
async def update_task(
    _request: Request,
    company_id: UUID,
    task_id: UUID,
    payload: UpdateTaskSchema,
    _token: TokenDTO = Depends(require_company_role(min_role=MemberRoles.ADMIN)),
    usecase: AbstractUpdateTaskUseCase = Depends(update_task_use_case),
) -> JSONResponse:
    dto = UpdateTaskDTO(
        title=payload.title,
        description=payload.description,
        responsible_id=payload.responsible_id,
        deadline=payload.deadline,
        estimated_minutes=payload.estimated_minutes,
        watcher_ids=payload.watcher_ids,
        assignee_ids=payload.assignee_ids,
    )
    try:
        task = await usecase.execute(dto=dto, company_id=company_id, task_id=task_id)
    except ParticipantNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None
    except ParticipantInactive as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from None
    except ParticipantWrongCompany as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from None

    return JSONResponse(
        _to_schema(dto=task.task, watcher_ids=task.watcher_ids, assignee_ids=task.assignee_ids).model_dump(mode="json"),
        status_code=status.HTTP_201_CREATED,
    )



@router.patch("/{company_id}/tasks/{task_id}/change_status", response_model=TaskSchema)
async def change_status_task(
    _request: Request,
    company_id: UUID,
    task_id: UUID,
    payload: ChangeStatusTaskSchema,
    _token: TokenDTO = Depends(require_company_role(min_role=MemberRoles.ADMIN)),
    usecase: AbstractChangeStatusTaskUseCase = Depends(change_status_task_use_case),
) -> JSONResponse:
    dto = ChangeStatusTaskDTO(
        status=payload.status,
    )
    try:
        task = await usecase.execute(dto=dto, company_id=company_id, task_id=task_id)
    except TaskNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None

    return JSONResponse(
        _to_schema(dto=task.task, watcher_ids=task.watcher_ids, assignee_ids=task.assignee_ids).model_dump(mode="json"),
        status_code=status.HTTP_201_CREATED,
    )


@router.delete("/{company_id}/tasks/{task_id}")
async def delete_task(
    _request: Request,
    company_id: UUID,
    task_id: UUID,
    _token: TokenDTO = Depends(require_company_role(min_role=MemberRoles.ADMIN)),
    usecase: AbstractDeleteTaskUseCase = Depends(delete_task_use_case),
) -> Response:
    try:
        await usecase.execute(company_id=company_id, task_id=task_id)
    except TaskNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None

    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _to_schema(dto: TaskDTO, watcher_ids: list[UUID], assignee_ids: list[UUID]) -> TaskSchema:
    return TaskSchema(
        id=dto.id,
        title=dto.title,
        description=dto.description,
        responsible_id=dto.responsible_id,
        deadline=dto.deadline,
        estimated_minutes=dto.estimated_minutes,
        author_id=dto.author_id,
        company_id=dto.company_id,
        status=dto.status,
        deleted_at=dto.deleted_at,
        watcher_ids=watcher_ids,
        assignee_ids=assignee_ids,
    )
