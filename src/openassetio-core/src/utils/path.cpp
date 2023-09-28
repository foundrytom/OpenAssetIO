// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#include <openassetio/utils/path.hpp>
#include "openassetio/errors/exceptions.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace utils {

Str pathToFileURL(StrView absolutePath, PathType pathType) {
  throw errors::NotImplementedException("pathToFileURL not yet implemented");
}

Str pathFromFileURL(StrView fileURL, PathType pathType) {
  throw errors::NotImplementedException("pathFromFileURL not yet implemented");
}

}  // namespace utils
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
