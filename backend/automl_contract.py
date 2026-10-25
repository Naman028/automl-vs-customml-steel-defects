"""Read image normalization from TFLite metadata and apply quantization.

Field positions follow TensorFlow's Model and ModelMetadata FlatBuffer schemas.
Fail closed when the export does not provide an image normalization contract.
"""

import struct
import zipfile
from functools import lru_cache
from pathlib import Path
from typing import Any
from numpy.typing import NDArray
from PIL import Image

import numpy as np
from flatbuffers.table import Table
from flatbuffers.number_types import Uint8Flags


def _tables(table: Table, field: int) -> list[Table]:
    offset = table.Offset(4 + 2 * field)
    if not offset:
        return []
    return [
        Table(table.Bytes, table.Indirect(table.Vector(offset) + 4 * i))
        for i in range(table.VectorLen(offset))
    ]


def _floats(table: Table, field: int) -> list[float]:
    offset = table.Offset(4 + 2 * field)
    if not offset:
        raise ValueError("Missing normalization values")
    return list(
        struct.unpack_from("<" + "f" * table.VectorLen(offset), table.Bytes, table.Vector(offset))
    )


@lru_cache(maxsize=8)
def read_contract(model_path: str) -> dict[str, list[float]]:
    data = Path(model_path).read_bytes()
    model = Table(data, struct.unpack_from("<I", data)[0])
    metadata = None
    buffers = _tables(model, 4)
    for entry in _tables(model, 6):
        name = entry.String(entry.Pos + entry.Offset(4))
        if name == b"TFLITE_METADATA":
            offset = entry.Offset(6)
            buffer_index = struct.unpack_from("<I", data, entry.Pos + offset)[0] if offset else 0
            buffer = buffers[buffer_index]
            vector = buffer.Offset(4)
            metadata = bytes(
                buffer.Bytes[
                    buffer.Vector(vector) : buffer.Vector(vector) + buffer.VectorLen(vector)
                ]
            )
    if metadata is None or metadata[4:8] != b"M001":
        raise ValueError("Missing supported TFLite image metadata")
    root = Table(metadata, struct.unpack_from("<I", metadata)[0])
    subgraphs = _tables(root, 3)
    tensors = _tables(subgraphs[0], 2)
    for unit in _tables(tensors[0], 4):
        offset = unit.Offset(4)
        kind = unit.Get(Uint8Flags, unit.Pos + offset) if offset else 0
        if kind == 1:  # ProcessUnitOptions.NormalizationOptions
            options = unit.Offset(6)
            normalization = Table(metadata, unit.Indirect(unit.Pos + options))
            mean, std = _floats(normalization, 0), _floats(normalization, 1)
            if (
                len(mean) not in (1, 3)
                or len(std) != len(mean)
                or not np.isfinite(mean + std).all()
                or min(std) <= 0
            ):
                raise ValueError("Invalid image normalization metadata")
            return dict(mean=mean, std=std)
    raise ValueError("Missing image normalization process unit")


def embedded_labels(model_path: str | Path) -> list[str]:
    # The checked-in Google AutoML export packages its output labels in dict.txt.
    with zipfile.ZipFile(model_path) as archive:
        return archive.read("dict.txt").decode("utf-8").splitlines()


def prepare_image(
    image: Image.Image, input_details: dict[str, Any], contract: dict[str, list[float]]
) -> NDArray[Any]:
    _, height, width, _ = input_details["shape"]
    values: NDArray[Any] = np.asarray(
        image.convert("RGB").resize((int(width), int(height))), dtype=np.float32
    )
    values = (values - np.asarray(contract["mean"], dtype=np.float32)) / np.asarray(
        contract["std"], dtype=np.float32
    )
    dtype = input_details["dtype"]
    if np.issubdtype(dtype, np.integer):
        scale, zero = input_details.get("quantization", (0, 0))
        if scale <= 0:
            raise ValueError("Missing quantization scale for integer input")
        bounds = np.iinfo(dtype)
        values = np.clip(np.rint(values / scale + zero), bounds.min, bounds.max)
    return values.astype(dtype)[None, ...]
