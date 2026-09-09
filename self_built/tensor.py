from __future__ import annotations

from numbers import Real
from typing import Any, Sequence

Number = int | float

class Tensor:
    """Store numeric data in a flat buffer with an explicit tensor shape."""

    def __init__(self, data: Any, shape: Sequence[int] | None = None) -> None:
        if isinstance(data, Tensor):
            values = list(data._data)
            inferred_shape = data.shape
        else:
            values, inferred_shape = self._flatten(data)

        final_shape = tuple(shape) if shape is not None else inferred_shape
        self._validate_shape(final_shape)

        expected_size = self._product(final_shape)
        if expected_size != len(values):
            raise ValueError(
                f"Data size {len(values)} does not match shape {final_shape}."
            )
        self._data = values
        self._shape = final_shape
        self._dtype = self._infer_dtype(values)

    @staticmethod
    def _flatten(data: Any) -> tuple[list[Number], tuple[int, ...]]:
        if isinstance(data, Tensor):
            return list(data._data), data.shape
        if isinstance(data, Real) and not isinstance(data, bool):
            return [data], ()
        if not isinstance(data, (list, tuple)):
            raise TypeError(
                "Tensor data must be numeric or a nested list/tuple."
            )
        if len(data) == 0:
            return [], (0,)
        child_values: list[list[Number]] = []
        child_shapes: list[tuple[int, ...]] = []

        for item in data:
            values, item_shape = Tensor._flatten(item)
            child_values.append(values)
            child_shapes.append(item_shape)
        first_shape = child_shapes[0]

        if any(item_shape != first_shape for item_shape in child_shapes[1:]):
            raise ValueError("Tensor data must form a rectangular shape.")

        values = [value for group in child_values for value in group]
        return values, (len(data),) + first_shape

    @staticmethod
    def _validate_shape(shape: Sequence[int]) -> None:
        for dimension in shape:
            if not isinstance(dimension, int) or isinstance(dimension, bool):
                raise TypeError("Tensor dimensions must be integers.")
            if dimension < 0:
                raise ValueError("Tensor dimensions cannot be negative.")

    @staticmethod
    def _product(shape: Sequence[int]) -> int:
        result = 1
        for dimension in shape:
            result *= dimension
        return result

    @staticmethod
    def _infer_dtype(values: Sequence[Number]) -> type:
        if not values:
            return float
        if any(isinstance(value, float) for value in values):
            return float
        return int

    @property
    def shape(self) -> tuple[int, ...]:
        return self._shape

    @property
    def ndim(self) -> int:
        return len(self._shape)

    @property
    def size(self) -> int:
        return len(self._data)

    @property
    def dtype(self) -> type:
        return self._dtype

    def tolist(self) -> Any:
        if self.ndim == 0:
            return self._data[0]
        return self._build_nested(self._data, self._shape)

    @staticmethod
    def _build_nested(
        data: Sequence[Number],
        shape: tuple[int, ...],
    ) -> Any:
        if len(shape) == 1:
            return list(data)
        step = Tensor._product(shape[1:])

        return [
            Tensor._build_nested(
                data[i : i + step],
                shape[1:],
            )
            for i in range(0, len(data), step)
        ]

    def _flat_index(self, index: int | tuple[int, ...]) -> int:
        if self.ndim == 0:
            if index == () or index == 0:
                return 0

            raise IndexError(
                "A scalar Tensor can only be indexed by 0."
            )

        indices = (index,) if isinstance(index, int) else index

        if len(indices) != self.ndim:
            raise IndexError(
                f"Expected {self.ndim} indices, "
                f"received {len(indices)}."
            )
        flat = 0

        for dimension, current in zip(self._shape, indices):
            if not isinstance(current, int):
                raise TypeError(
                    "Tensor indices must be integers."
                )
            if current < 0:
                current += dimension
            if current < 0 or current >= dimension:
                raise IndexError("Tensor index out of range.")
            flat = flat * dimension + current
        return flat

    def __getitem__(self, index: int | tuple[int, ...]) -> Number:
        return self._data[self._flat_index(index)]

    def __setitem__(self, index: int | tuple[int, ...], value: Number) -> None:
        if not isinstance(value, Real) or isinstance(value, bool):
            raise TypeError("Tensor values must be numeric.")
        
        self._data[self._flat_index(index)] = value
        self._dtype = self._infer_dtype(self._data)

    def reshape(self, *shape: int | Sequence[int]) -> Tensor:
        if len(shape) == 1 and isinstance(shape[0], (list, tuple)):
            new_shape = tuple(shape[0])
        else:
            new_shape = tuple(shape)

        self._validate_shape(new_shape)
        if self._product(new_shape) != self.size:
            raise ValueError(
                f"Cannot reshape tensor of size {self.size} "
                f"into {new_shape}."
            )
        return Tensor(self._data, shape=new_shape)

    def transpose(self) -> Tensor:
        if self.ndim < 2:
            return Tensor(self._data, self.shape)
        new_shape = (
            self._shape[:-2]
            + (self._shape[-1], self._shape[-2])
        )
        result = [0] * self.size
        outer = self._product(self._shape[:-2])
        rows, cols = self._shape[-2:]
        block = rows * cols

        for base in range(outer):
            source_base = base * block
            target_base = base * block
            for row in range(rows):
                for col in range(cols):
                    result[
                        target_base + col * rows + row
                    ] = self._data[
                        source_base + row * cols + col
                    ]
        return Tensor(result, new_shape)

    def sum(self) -> Number:
        return sum(self._data)

    def mean(self) -> float:
        if self.size == 0:
            raise ValueError("Mean of an empty Tensor is undefined.")
        return self.sum() / self.size

    def _binary_op(self, other: Number | Tensor, operation: str) -> Tensor:
        if isinstance(other, Tensor):
            if self.shape != other.shape:
                raise ValueError(
                    f"Tensor shapes must match: "
                    f"{self.shape} != {other.shape}."
                )
            right = other._data
        elif isinstance(other, Real) and not isinstance(other, bool):
            right = [other] * self.size
        else:
            raise TypeError("Operation requires a Tensor or numeric scalar.")
       
        result: list[Number] = []

        for left_value, right_value in zip(self._data, right):
            if operation == "add":
                result.append(left_value + right_value)
            elif operation == "sub":
                result.append(left_value - right_value)
            elif operation == "mul":
                result.append(left_value * right_value)
            elif operation == "div":
                if right_value == 0:
                    raise ZeroDivisionError("Tensor division by zero.")
                result.append(left_value / right_value)
            else:
                raise ValueError(f"Unknown operation: {operation}")
        return Tensor(result, self.shape)

    def __add__(self, other: Number | Tensor) -> Tensor:
        return self._binary_op(other, "add")

    def __radd__(self, other: Number | Tensor) -> Tensor:
        return self.__add__(other)

    def __sub__(self, other: Number | Tensor) -> Tensor:
        return self._binary_op(other, "sub")

    def __rsub__(self, other: Number | Tensor) -> Tensor:
        if isinstance(other, Tensor):
            return other.__sub__(self)
        return Tensor([other] * self.size, self.shape).__sub__(self)

    def __mul__(self, other: Number | Tensor) -> Tensor:
        return self._binary_op(other, "mul")

    def __rmul__(self, other: Number | Tensor) -> Tensor:
        return self.__mul__(other)

    def __truediv__(self, other: Number | Tensor) -> Tensor:
        return self._binary_op(other, "div")

    def __matmul__(self, other: Tensor) -> Tensor:
        if not isinstance(other, Tensor):
            raise TypeError("Matrix multiplication requires another Tensor.")
        
        if self.ndim != 2 or other.ndim != 2:
            raise ValueError(
                "Matrix multiplication currently requires "
                "2-D tensors."
            )
        
        rows_a, cols_a = self.shape
        rows_b, cols_b = other.shape
        if cols_a != rows_b:
            raise ValueError(
                f"Cannot multiply shapes "
                f"{self.shape} and {other.shape}."
            )
        result: list[Number] = []

        for row in range(rows_a):
            for col in range(cols_b):
                value = 0
                for inner in range(cols_a):
                    value += (self[row, inner] * other[inner, col])
                result.append(value)
        return Tensor(result, (rows_a, cols_b))

    def __repr__(self) -> str:
        return (f"Tensor(data={self.tolist()!r}, " f"shape={self.shape})")

def zeros(*shape: int | Sequence[int]) -> Tensor:
    """Create a Tensor filled with zeros."""

    resolved = _resolve_shape(shape)
    return Tensor([0] * Tensor._product(resolved), resolved)

def ones(*shape: int | Sequence[int]) -> Tensor:
    """Create a Tensor filled with ones."""

    resolved = _resolve_shape(shape)
    return Tensor([1] * Tensor._product(resolved), resolved)


def _resolve_shape(shape: tuple[int | Sequence[int], ...]) -> tuple[int, ...]:
    if len(shape) == 1 and isinstance(shape[0], (list, tuple)):
        resolved = tuple(shape[0])
    else:
        resolved = tuple(shape)
    Tensor._validate_shape(resolved)
    return resolved
