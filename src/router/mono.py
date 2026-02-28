from uuid import UUID

from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.dependencies.auth import get_current_user_id
from src.repositories.mono import MonoRepository
from src.repositories.user import UserRepository
from src.schemas.user import UserSaveMonoToken, UserResponseMonoToken
from src.schemas.mono import MonoAccountsResponse, MonoTransactionResponse
from src.services.mono import MonoService

router = APIRouter(prefix="/mono", tags=["mono"])


@router.post("/savetoken", response_model=UserResponseMonoToken)
async def save_mono_token(
    data: UserSaveMonoToken,
    session: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    repository = UserRepository(session)
    mono_repository = MonoRepository(session)
    service = MonoService(repository, mono_repository)

    service.save_token(user_id, data.mono_token)
    return UserResponseMonoToken(response="Successfully saved token")


@router.get("/verifytoken", response_model=UserResponseMonoToken)
async def verify_token(
        session: Session = Depends(get_db),
        user_id: UUID = Depends(get_current_user_id),
):
    try:
        repository = UserRepository(session)
        mono_repository = MonoRepository(session)
        service = MonoService(repository, mono_repository)
        has_token = service.verify_token(user_id)

        if not has_token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"The user with id: {user_id} does not have a mono token"
            )

        return UserResponseMonoToken(response=f"The user with id: {user_id} has mono token")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/save-mono-cards", response_model=UserResponseMonoToken)
async def save_mono_cards(
        session: Session = Depends(get_db),
        user_id: UUID = Depends(get_current_user_id),
):
    try:
        repository = UserRepository(session)
        mono_repository = MonoRepository(session)
        service = MonoService(repository, mono_repository)

        connection = service.save_cards_info(user_id)
        return UserResponseMonoToken(response=f"The Mono Bank was successfully connected for user id {user_id}")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/cards-info", response_model=MonoAccountsResponse)
async def get_cards_info(
        session: Session = Depends(get_db),
        user_id: UUID = Depends(get_current_user_id),
):
    try:
        repository = UserRepository(session)
        mono_repository = MonoRepository(session)
        service = MonoService(repository, mono_repository)

        cards_info = service.get_card_info(user_id)
        return MonoAccountsResponse(response=cards_info)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/delete-mono-card", response_model=UserResponseMonoToken)
async def delete_mono_card(
        card_id: str,
        session: Session = Depends(get_db),
        user_id: UUID = Depends(get_current_user_id)
):
    try:
        repository = UserRepository(session)
        mono_repository = MonoRepository(session)
        service = MonoService(repository, mono_repository)

        service.delete_card(card_id)
        return UserResponseMonoToken(response=f"The card with id: {card_id} was successfully deleted")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/save-transaction", response_model=UserResponseMonoToken)
async def add_transaction(
    card_id: str,
    session: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    try:
        repository = UserRepository(session)
        mono_repository = MonoRepository(session)
        service = MonoService(repository, mono_repository)

        result = service.save_transaction(card_id, user_id)
        return UserResponseMonoToken(response=result)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/get-transaction", response_model=MonoTransactionResponse)
async def get_transaction(
    card_id: str,
    session: Session = Depends(get_db)
):
    try:
        repository = UserRepository(session)
        mono_repository = MonoRepository(session)
        service = MonoService(repository, mono_repository)

        transaction = service.get_transactions_by_card_id(card_id)
        return MonoTransactionResponse(response=transaction)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


