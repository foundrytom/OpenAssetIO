// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/export.h>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {

namespace utils {

enum class PathType { kSystem = 0, kPOSIX, kWindows };

OPENASSETIO_CORE_EXPORT Str pathToFileURL(StrView absolutePath, PathType pathType = PathType::kSystem);
OPENASSETIO_CORE_EXPORT Str pathFromFileURL(StrView fileURL, PathType pathType = PathType::kSystem);

}  // namespace utils
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
