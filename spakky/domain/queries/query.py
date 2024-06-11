from typing import Generic

from spakky.core.mutability import immutable
from spakky.domain.models.value_object import ValueObject
from spakky.domain.queries.order_by import OrderBy
from spakky.domain.queries.page import PageableT
from spakky.domain.queries.where import Where


@immutable
class Query(ValueObject, Generic[PageableT]):
    where: Where
    order_by: OrderBy
    pageable: PageableT
