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
"""Events concerning manipulation of members within guilds."""

from __future__ import annotations

__all__: typing.Sequence[str] = ("MemberCreateEvent", "MemberDeleteEvent", "MemberEvent", "MemberUpdateEvent")

import abc
import typing

import attrs

from hikari import intents
from hikari import traits
from hikari.events import base_events
from hikari.events import shard_events
from hikari.internal import attrs_extensions
from hikari.internal import typing_extensions

if typing.TYPE_CHECKING:
    from hikari import guilds
    from hikari import snowflakes
    from hikari import users
    from hikari.api import shard as gateway_shard


@base_events.requires_intents(intents.Intents.GUILD_MEMBERS)
class MemberEvent(shard_events.ShardEvent, abc.ABC):
    """Event base for any events that concern guild members."""

    __slots__: typing.Sequence[str] = ()

    @property
    @typing_extensions.override
    def app(self) -> traits.RESTAware:
        # <<inherited docstring from Event>>.
        return self.user.app

    @property
    @abc.abstractmethod
    def guild_id(self) -> snowflakes.Snowflake:
        """ID of the guild that this event relates to."""

    @property
    @abc.abstractmethod
    def user(self) -> users.User:
        """User object for the member this event concerns."""

    @property
    def user_id(self) -> snowflakes.Snowflake:
        """ID of the user that this event concerns."""
        return self.user.id

    def get_guild(self) -> guilds.GatewayGuild | None:
        """Get the cached view of the guild this member event occurred in.

        If the guild itself is not cached, this will return [`None`][].

        Returns
        -------
        typing.Optional[hikari.guilds.GatewayGuild]
            The guild that this event occurred in, if known, else
            [`None`][].
        """
        if not isinstance(self.app, traits.CacheAware):
            return None

        return self.app.cache.get_available_guild(self.guild_id) or self.app.cache.get_unavailable_guild(self.guild_id)


@attrs_extensions.with_copy
@attrs.define(kw_only=True, weakref_slot=False)
@base_events.requires_intents(intents.Intents.GUILD_MEMBERS)
class MemberCreateEvent(MemberEvent):
    """Event that is fired when a member joins a guild."""

    shard: gateway_shard.GatewayShard = attrs.field(metadata={attrs_extensions.SKIP_DEEP_COPY: True})
    # <<inherited docstring from ShardEvent>>.

    member: guilds.Member = attrs.field()
    """Member object for the member that joined the guild."""

    @property
    @typing_extensions.override
    def guild_id(self) -> snowflakes.Snowflake:
        # <<inherited docstring from MemberEvent>>.
        return self.member.guild_id

    @property
    @typing_extensions.override
    def user(self) -> users.User:
        # <<inherited docstring from MemberEvent>>.
        return self.member.user


@attrs_extensions.with_copy
@attrs.define(kw_only=True, weakref_slot=False)
@base_events.requires_intents(intents.Intents.GUILD_MEMBERS)
class MemberUpdateEvent(MemberEvent):
    """Event that is fired when a member is updated in a guild.

    This may occur if roles are amended, or if the nickname is changed.
    """

    shard: gateway_shard.GatewayShard = attrs.field(metadata={attrs_extensions.SKIP_DEEP_COPY: True})
    # <<inherited docstring from ShardEvent>>.

    old_member: guilds.Member | None = attrs.field()
    """The old member object.

    This will be [`None`][] if the member missing from the cache.
    """

    member: guilds.Member = attrs.field()
    """Member object for the member that was updated."""

    @property
    @typing_extensions.override
    def guild_id(self) -> snowflakes.Snowflake:
        # <<inherited docstring from MemberEvent>>.
        return self.member.guild_id

    @property
    @typing_extensions.override
    def user(self) -> users.User:
        # <<inherited docstring from MemberEvent>>.
        return self.member.user


@attrs_extensions.with_copy
@attrs.define(kw_only=True, weakref_slot=False)
@base_events.requires_intents(intents.Intents.GUILD_MEMBERS)
class MemberDeleteEvent(MemberEvent):
    """Event fired when a member is kicked from or leaves a guild."""

    shard: gateway_shard.GatewayShard = attrs.field(metadata={attrs_extensions.SKIP_DEEP_COPY: True})
    # <<inherited docstring from ShardEvent>>.

    guild_id: snowflakes.Snowflake = attrs.field()
    # <<inherited docstring from MemberEvent>>.

    user: users.User = attrs.field()
    # <<inherited docstring from MemberEvent>>.

    old_member: guilds.Member | None = attrs.field()
    """The old member object.

    This will be [`None`][] if the member was missing from the cache.
    """
