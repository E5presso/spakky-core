from typing import Generic

from spakky.core.mutability import immutable
from spakky.domain.models.value_object import ValueObject
from spakky.domain.usecases.query_option.order_by import OrderBy
from spakky.domain.usecases.query_option.page import PageableT
from spakky.domain.usecases.query_option.where import Where


@immutable
class QueryOption(ValueObject, Generic[PageableT]):
    where: Where
    order_by: OrderBy
    pageable: PageableT
