# Copyright (c) 2020 Nekokatt
# Copyright (c) 2021-present davfsa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Application and entities that are used to describe guild scheduled events on Discord."""

from __future__ import annotations

__all__: typing.Sequence[str] = (
    "EventPrivacyLevel",
    "ScheduledEvent",
    "ScheduledEventStatus",
    "ScheduledEventType",
    "ScheduledEventUser",
    "ScheduledExternalEvent",
    "ScheduledStageEvent",
    "ScheduledVoiceEvent",
)

import typing

import attrs

from hikari import snowflakes
from hikari import undefined
from hikari import urls
from hikari.internal import attrs_extensions
from hikari.internal import deprecation
from hikari.internal import enums
from hikari.internal import routes

if typing.TYPE_CHECKING:
    import datetime

    from hikari import files
    from hikari import guilds
    from hikari import traits
    from hikari import users


class EventPrivacyLevel(int, enums.Enum):
    """Enum of the possible scheduled event privacy levels."""

    GUILD_ONLY = 2
    """The scheduled event is only available to guild members."""


class ScheduledEventType(int, enums.Enum):
    """Enum of the scheduled event types."""

    STAGE_INSTANCE = 1
    """A scheduled stage instance."""

    VOICE = 2
    """A scheduled voice chat event."""

    EXTERNAL = 3
    """A scheduled event which takes part outside of Discord."""


class ScheduledEventStatus(int, enums.Enum):
    """Enum of the scheduled event statuses."""

    SCHEDULED = 1
    """Indicates that the scheduled event hasn't occurred yet."""

    ACTIVE = 2
    """Indicates an event is on-going."""

    COMPLETED = 3
    """Indicates an event has finished."""

    CANCELED = 4
    """Indicates an event has been canceled."""

    CANCELLED = CANCELED
    """Alias of [`hikari.scheduled_events.ScheduledEventStatus.CANCELED`][]."""


@attrs_extensions.with_copy
@attrs.define(unsafe_hash=True, kw_only=True, weakref_slot=False)
class ScheduledEvent(snowflakes.Unique):
    """Base class for scheduled events."""

    # entity_id is ignored right now due to always being null
    # creator_id is ignored as it just dupes creator.id

    app: traits.RESTAware = attrs.field(
        repr=False, eq=False, hash=False, metadata={attrs_extensions.SKIP_DEEP_COPY: True}
    )
    """Client application that models may use for procedures."""

    id: snowflakes.Snowflake = attrs.field(hash=True, repr=True)
    """ID of the scheduled event."""

    guild_id: snowflakes.Snowflake = attrs.field(hash=False, repr=True)
    """ID of the guild this scheduled event belongs to."""

    name: str = attrs.field(hash=False, repr=True)
    """Name of the scheduled event."""

    description: str | None = attrs.field(hash=False, repr=False)
    """Description of the scheduled event."""

    start_time: datetime.datetime = attrs.field(hash=False, repr=False)
    """When the event is scheduled to start."""

    end_time: datetime.datetime | None = attrs.field(hash=False, repr=False)
    """When the event is scheduled to end, if set."""

    privacy_level: EventPrivacyLevel = attrs.field(hash=False, repr=False)
    """Privacy level of the scheduled event.

    This restricts who can view and join the scheduled event.
    """

    status: ScheduledEventStatus = attrs.field(hash=False, repr=True)
    """Status of the scheduled event."""

    entity_type: ScheduledEventType = attrs.field(hash=False, repr=True)
    """The type of entity this scheduled event is associated with."""

    creator: users.User | None = attrs.field(hash=False, repr=False)
    """The user who created the scheduled event.

    This will only be set for event created after 2021-10-25.
    """

    user_count: int | None = attrs.field(hash=False, repr=False)
    """The number of users that have subscribed to the event.

    This will be [`None`][] on gateway events when creating and
    editing a scheduled event.
    """

    image_hash: str | None = attrs.field(hash=False, repr=False)
    """Hash of the image used for the scheduled event, if set."""

    @property
    @deprecation.deprecated("Use 'make_image_url' instead.")
    def image_url(self) -> files.URL | None:
        """Cover image for this scheduled event, if set."""
        deprecation.warn_deprecated(
            "image_url", removal_version="2.5.0", additional_info="Use 'make_image_url' instead."
        )
        return self.make_image_url()

    def make_image_url(
        self,
        *,
        file_format: typing.Literal["PNG", "JPEG", "JPG", "WEBP"] = "PNG",
        size: int = 4096,
        lossless: bool = True,
        ext: str | None | undefined.UndefinedType = undefined.UNDEFINED,
    ) -> files.URL | None:
        """Generate the cover image URL for this scheduled event, if set.

        If no cover image is set, this returns [`None`][].

        Parameters
        ----------
        file_format
            The format to use for this URL.

            Supports `PNG`, `JPEG`, `JPG`, and `WEBP`.

            If not specified, the format will be `PNG`.
        size
            The size to set for the URL;
            Can be any power of two between `16` and `4096`;
        lossless
            Whether to return a lossless or compressed WEBP image;
            This is ignored if `file_format` is not `WEBP`.
        ext
            The extension to use for this URL.
            Supports `png`, `jpeg`, `jpg` and `webp`.

            !!! deprecated 2.4.0
                This has been replaced with the `file_format` argument.

        Returns
        -------
        typing.Optional[hikari.files.URL]
            The URL, or [`None`][] if no cover image is set.

        Raises
        ------
        TypeError
            If an invalid format is passed for `file_format`.
        ValueError
            If `size` is specified but is not a power of two or not between 16 and 4096.
        """
        if self.image_hash is None:
            return None

        if ext:
            deprecation.warn_deprecated(
                "ext", removal_version="2.5.0", additional_info="Use 'file_format' argument instead."
            )
            file_format = ext.upper()  # type: ignore[assignment]

        return routes.SCHEDULED_EVENT_COVER.compile_to_file(
            urls.CDN_URL,
            scheduled_event_id=self.id,
            hash=self.image_hash,
            size=size,
            file_format=file_format,
            lossless=lossless,
        )


@attrs_extensions.with_copy
@attrs.define(unsafe_hash=True, kw_only=True, weakref_slot=False)
class ScheduledExternalEvent(ScheduledEvent):
    """A scheduled event that takes place outside of Discord."""

    location: str = attrs.field(hash=False, repr=False)
    """The location of the scheduled event.

    !!! note
        There is no strict format for this field, and it will likely be a user
        friendly string.
    """

    end_time: datetime.datetime = attrs.field(hash=False, repr=False)
    """When the event is scheduled to end."""


@attrs_extensions.with_copy
@attrs.define(unsafe_hash=True, kw_only=True, weakref_slot=False)
class ScheduledStageEvent(ScheduledEvent):
    """A scheduled event that takes place in a stage channel."""

    channel_id: snowflakes.Snowflake = attrs.field(hash=False, repr=False)
    """ID of the stage channel this event is scheduled in."""


@attrs_extensions.with_copy
@attrs.define(unsafe_hash=True, kw_only=True, weakref_slot=False)
class ScheduledVoiceEvent(ScheduledEvent):
    """A scheduled event that takes place in a voice channel."""

    channel_id: snowflakes.Snowflake = attrs.field(hash=False, repr=False)
    """ID of the voice channel this scheduled event is in."""


@attrs_extensions.with_copy
@attrs.define(kw_only=True, weakref_slot=False)
class ScheduledEventUser:
    """A user who is subscribed to a scheduled event."""

    event_id: snowflakes.Snowflake = attrs.field(hash=False, repr=True)
    """ID of the scheduled event they're subscribed to."""

    user: users.User = attrs.field(hash=True, repr=True)
    """Object representing the user."""

    member: guilds.Member | None = attrs.field(hash=False, repr=False)
    """Their guild member object if they're in the event's guild."""
