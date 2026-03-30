from uuid import UUID

from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.dependencies.auth import get_current_user_id
from src.repositories.mono import MonoRepository
from src.repositories.user import UserRepository
from src.repositories.record import RecordRepository
from src.schemas.record import RecordRead, RecordCreate
from src.services.record import RecordService
from src.schemas.user import UserSaveMonoToken, UserResponseMonoToken
from src.schemas.mono import MonoAccountsResponse, MonoTransactionResponse, MonoUpdateInfoResponse, MonoSyncResponse
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

    await service.save_token(user_id, data.mono_token)
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
        has_token = await service.verify_token(user_id)

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

        connection = await service.save_cards_info(user_id)
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

        cards_info = await service.get_card_info(user_id)
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

        await service.delete_card(card_id)
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

        result = await service.save_transaction(card_id, user_id)
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

        transaction = await service.get_transactions_by_card_id(card_id)
        return MonoTransactionResponse(response=transaction)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/sync-transactions", response_model=UserResponseMonoToken)
async def sync_transactions(
        card_id: str,
        session: Session = Depends(get_db),
        user_id: UUID = Depends(get_current_user_id)
):
    """Legacy endpoint — use POST /mono/sync instead."""
    try:
        repository = UserRepository(session)
        mono_repository = MonoRepository(session)
        record_repository = RecordRepository(session)

        service = MonoService(repository, mono_repository)
        transaction = await service.get_transactions_by_card_id(card_id)

        parsed_records = []
        for t in transaction:
            parsed_records.append(RecordCreate(
                amount=t.amount / 100.0,
                type="income" if t.amount >= 0 else "expense",
                currency=str(t.currency),
                description=t.description,
                mono_card_id=card_id,
                created_at=t.time
            ))

        record_service = RecordService(record_repository)
        result = record_service.create_records(user_id, parsed_records, card_id)

        return UserResponseMonoToken(
            response=f"Created {result['records_created']} records, skipped {result['records_skipped']} duplicates"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/update-card-name", response_model=MonoUpdateInfoResponse)
async def update_card_name(
        card_id: str,
        card_name: str,
        session: Session = Depends(get_db),
):
    try:
        repository = UserRepository(session)
        mono_repository = MonoRepository(session)
        service = MonoService(repository, mono_repository)

        await service.update_card_name(card_id, card_name)

        return MonoUpdateInfoResponse(response="Successfully updated card name")

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/sync", response_model=MonoSyncResponse)
async def sync_card(
        card_id: str,
        session: Session = Depends(get_db),
        user_id: UUID = Depends(get_current_user_id)
):
    """
    Unified sync: fetches last 30 days from Mono API,
    deduplicates mono_transactions, creates Records for new ones,
    and updates the card balance.
    """
    try:
        repository = UserRepository(session)
        mono_repository = MonoRepository(session)
        record_repository = RecordRepository(session)

        service = MonoService(repository, mono_repository)

        # Step 1: Fetch + dedup mono transactions
        sync_result = await service.sync_card(card_id, user_id)

        # Step 2: Create Records from NEW mono transactions only
        parsed_records = []
        for tx in sync_result["mono_transactions"]:
            parsed_records.append(RecordCreate(
                amount=tx.amount / 100.0,
                type="income" if tx.amount >= 0 else "expense",
                currency=str(tx.currency),
                description=tx.description,
                mono_card_id=card_id,
                created_at=tx.time
            ))

        records_result = {"records_created": 0, "records_skipped": 0}
        if parsed_records:
            record_service = RecordService(record_repository)
            records_result = record_service.create_records(user_id, parsed_records, card_id)

        return MonoSyncResponse(
            new_transactions=sync_result["new_transactions"],
            skipped_duplicates=sync_result["skipped_duplicates"],
            total_fetched=sync_result["total_fetched"],
            records_created=records_result["records_created"],
            records_skipped=records_result["records_skipped"],
            card_id=card_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
