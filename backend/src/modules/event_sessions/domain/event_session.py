from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from modules.shared.domain.aggregate_root import AggregateRoot
from modules.shared.domain.domain_validation_error import DomainValidationError
from modules.shared.domain.value_object.id_value_object import IdValueObject
from modules.shared.domain.value_object.invalid_argument_error import InvalidArgumentError

from .errors import SessionTimeOutOfBoundsError
from .session_date_range import SessionDateRange
from .session_description import SessionDescription
from .session_title import SessionTitle


@dataclass
class EventSession(AggregateRoot):
    id: IdValueObject
    event_id: IdValueObject
    title: SessionTitle
    description: SessionDescription
    speaker_name: str
    speaker_bio: str
    time_range: SessionDateRange
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        id: str,
        event_id: str,
        title: str,
        description: str,
        speaker_name: str,
        speaker_bio: str,
        start_at: datetime,
        end_at: datetime,
        event_dates: tuple[datetime, datetime],
    ) -> "EventSession":
        errors: dict[str, list[str]] = {}

        try:
            sid = IdValueObject(id)
        except InvalidArgumentError as e:
            errors["id"] = [str(e)]

        try:
            eid = IdValueObject(event_id)
        except InvalidArgumentError as e:
            errors["event_id"] = [str(e)]

        try:
            stitle = SessionTitle(title)
        except InvalidArgumentError as e:
            errors["title"] = [str(e)]

        try:
            sdesc = SessionDescription(description or "")
        except InvalidArgumentError as e:
            errors["description"] = [str(e)]

        try:
            tr = SessionDateRange(start_at=start_at, end_at=end_at)
        except InvalidArgumentError as e:
            errors["time_range"] = [str(e)]
        else:
            # Check within event bounds
            event_start, event_end = event_dates
            if tr.start_at < event_start or tr.end_at > event_end:
                errors["time_range"] = errors.get("time_range", []) + [
                    "Session must be within event date range"
                ]

        if errors:
            raise DomainValidationError(errors)

        now = datetime.now(timezone.utc)
        return cls(
            id=sid,
            event_id=eid,
            title=stitle,
            description=sdesc,
            speaker_name=speaker_name or "",
            speaker_bio=speaker_bio or "",
            time_range=tr,
            created_at=now,
            updated_at=now,
        )

    def update_details(
        self,
        *,
        title: str | None = None,
        description: str | None = None,
        speaker_name: str | None = None,
        speaker_bio: str | None = None,
    ) -> None:
        errors: dict[str, list[str]] = {}
        if title is not None:
            try:
                self.title = SessionTitle(title)
            except InvalidArgumentError as e:
                errors["title"] = [str(e)]
        if description is not None:
            try:
                self.description = SessionDescription(description)
            except InvalidArgumentError as e:
                errors["description"] = [str(e)]
        if speaker_name is not None:
            self.speaker_name = speaker_name
        if speaker_bio is not None:
            self.speaker_bio = speaker_bio
        if errors:
            raise DomainValidationError(errors)
        self._touch()

    def reschedule(
        self,
        *,
        start_at: datetime,
        end_at: datetime,
        event_dates: tuple[datetime, datetime],
    ) -> None:
        try:
            tr = SessionDateRange(start_at=start_at, end_at=end_at)
        except InvalidArgumentError as e:
            raise DomainValidationError({"time_range": [str(e)]})
        event_start, event_end = event_dates
        if tr.start_at < event_start or tr.end_at > event_end:
            raise SessionTimeOutOfBoundsError("Session must be within event date range")
        self.time_range = tr
        self._touch()

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
