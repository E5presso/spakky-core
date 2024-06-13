from typing import Generic
from dataclasses import field

from spakky.core.mutability import immutable
from spakky.domain.models.value_object import ValueObject
from spakky.domain.usecases.criteria.order_by import OrderBy
from spakky.domain.usecases.criteria.page import PageableT
from spakky.domain.usecases.criteria.where import Where


@immutable
class Criteria(ValueObject, Generic[PageableT]):
    where: Where | None = field(default=None)
    order_by: OrderBy | None = field(default=None)
    pageable: PageableT | None = field(default=None)
