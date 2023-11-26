from datetime import datetime
from typing import Iterable, Sequence

from sqlalchemy import Select, func, select  # type: ignore[attr-defined]
from sqlalchemy.orm import Session

from app.common.crud import CRUDBase, SlugMixin
from app.common.schemas import EmptySchema
from app.events.models import Event, Speaker
from app.events.schemas import EventCreate
from app.tickets.models import Ticket, TicketCategory


class CRUDEvent(CRUDBase[Event, EventCreate, EmptySchema], SlugMixin[Event]):
    def get_filtered(
        self,
        db: Session,
        *,
        only_with_available_tickets: bool | None = False,
        filters: Iterable | None = None,
        joins: Iterable | None = None,
        order_by: Iterable | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Event]:
        query = self._get_filter_query(
            only_with_available_tickets=only_with_available_tickets, filters=filters, joins=joins
        )
        if order_by:
            query = query.order_by(*order_by)
        query = query.offset(skip).limit(limit)
        result = db.execute(query)
        return result.scalars().all()

    def get_filtered_count(
        self,
        db: Session,
        *,
        only_with_available_tickets: bool | None = False,
        filters: Iterable | None = None,
        joins: Iterable | None = None,
    ) -> int:
        base_query = self._get_filter_query(
            only_with_available_tickets=only_with_available_tickets, filters=filters, joins=joins
        )
        count_query = select(func.count()).select_from(base_query.subquery())  # pylint: disable=not-callable
        result = db.execute(count_query)
        return result.scalar_one()

    def _get_filter_query(
        self,
        only_with_available_tickets: bool | None = False,
        filters: Iterable | None = None,
        joins: Iterable | None = None,
    ) -> Select:
        if only_with_available_tickets:
            subquery = (
                select(TicketCategory.event_id)  # type: ignore[attr-defined]
                .join(Ticket, isouter=True)  # type: ignore[arg-type]
                .group_by(TicketCategory.id)
                .having(TicketCategory.quota > func.count(Ticket.id))  # pylint: disable=not-callable
            )
            query = select(self.model).where(self.model.id.in_(subquery))
        else:
            query = select(self.model)
        if joins:
            for join in joins:
                query = query.join(join)  # type: ignore[assignment]
        if filters:
            query = query.where(*filters)
        return query

    def speakers(self, event: Event) -> list[Speaker]:
        return event.speakers

    def add_speaker(self, db: Session, *, event: Event, speaker: Speaker) -> None:
        event.speakers.append(speaker)
        db.commit()

    def remove_speaker(self, db: Session, *, event: Event, speaker: Speaker) -> None:
        event.speakers.remove(speaker)
        db.commit()

    def is_active(self, event: Event) -> bool:
        return event.is_active

    def is_expired(self, event: Event) -> bool:
        return datetime.utcnow() > event.held_at
