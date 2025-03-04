// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#pragma once
#include <string>
#include <string_view>
#include <tuple>
#include <type_traits>

#include <pybind11/pybind11.h>

#include <openassetio/export.h>
#include <openassetio/errors/exceptions.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace python::exceptions {
namespace py = pybind11;
using openassetio::errors::BatchElementException;
using openassetio::errors::ConfigurationException;
using openassetio::errors::InputValidationException;
using openassetio::errors::NotImplementedException;
using openassetio::errors::OpenAssetIOException;
using openassetio::errors::UnhandledException;

/**
 * @section list List of exceptions.
 *
 * @{
 */

/**
 * Container for a list of types and their corresponding string
 * identifiers.
 *
 * @tparam Type List of types.
 */
template <class... Type>
struct TypesAndIds {
  static constexpr std::size_t kSize = sizeof...(Type);
  using Types = std::tuple<Type...>;
  const std::array<std::string_view, kSize> ids;
};

/**
 * Exhaustive list of all OpenAssetIO-specific C++ exception types and
 * their corresponding Python class names.
 *
 * Note base classes must come _after_ subclasses (asserted at
 * compile-time, below). This is so that try-catch blocks can be ordered
 * such that more-derived exceptions come before less-derived. See
 * `tryCatch`.
 */
constexpr auto kCppExceptionsAndPyClassNames =
    TypesAndIds<BatchElementException, NotImplementedException, UnhandledException,
                ConfigurationException, InputValidationException, OpenAssetIOException>{
        "BatchElementException",  "NotImplementedException",  "UnhandledException",
        "ConfigurationException", "InputValidationException", "OpenAssetIOException"};

/**
 * Convenience struct deriving compile-time properties from the above
 * list of OpenAssetIO-specific exception class types and names.
 *
 * In particular there are two lists, such that given a single index,
 * the C++ exception class or the Python class name can be queried at
 * compile time.
 */
struct CppExceptionsAndPyClassNames {
  using Type = decltype(kCppExceptionsAndPyClassNames);
  /// "Array" of C++ exception classes.
  template <std::size_t I>
  using Exceptions = std::tuple_element_t<I, typename Type::Types>;
  /// Array of Python exception class names.
  static constexpr std::array kClassNames = kCppExceptionsAndPyClassNames.ids;
  /// Total number of exceptions in the list(s).
  static constexpr std::size_t kSize = Type::kSize;
  /**
   * Convenience for a sequence of indices, used for compile-time
   * iteration over C++ exception classes.
   */
  static constexpr auto kIndices = std::make_index_sequence<kSize>{};
};

/**
 * @}
 */

/**
 * @section tocpp Conversion from Python exception to C++ exception.
 *
 * @{
 */

/**
 * Hybrid of OpenAssetIO and pybind11 exception class.
 *
 * Multiple inheritance means that in C++ we can `catch` this exception
 * as either `error_already_set` or the given OpenAssetIO exception. If
 * (re)thrown, it can be caught further up the stack (again) as either
 * of the two exceptions. In this way we can satisfy the two use-cases:
 * - Catching the exception in C++ as an OpenAssetIO C++ exception.
 * - Allowing the exception to propagate back to Python via pybind11,
 *   which will translate it back into a Python exception (see
 *   registerExceptions).
 *
 * Note that calling `.what()` on this exception is ambiguous and will
 * cause a compiler error. However, this is a good thing, since this
 * exception should never appear in a `catch` (should only be caught as
 * one of the base classes).
 *
 * Generalisation assuming that the given exception type is a simple
 * exception that takes a string message as its only constructor
 * argument.
 *
 * @tparam CppException C++ exception type corresponding to given
 * Python exception.
 */
template <class CppException>
struct HybridException : py::error_already_set, CppException {
  explicit HybridException(const py::error_already_set &pyExc)
      : py::error_already_set{pyExc}, CppException{pyExc.what()} {}
};

/**
 * Hybrid of OpenAssetIO and pybind11 exception class.
 *
 * Specialisation for more complex case of BatchElementException. See
 * generalisation, above, for more details.
 */
template <>
struct HybridException<BatchElementException> : py::error_already_set, BatchElementException {
  explicit HybridException(const py::error_already_set &pyExc)
      : py::error_already_set{pyExc},
        BatchElementException{
            py::cast<std::size_t>(pyExc.value().attr("index")),
            py::cast<openassetio::errors::BatchElementError>(pyExc.value().attr("error")),
            pyExc.what()} {}
};

/**
 * Throw a HybridException if the given Python class name matches the
 * given expected Python class name corresponding to the given C++
 * exception type.
 *
 * @tparam Exception C++ exception to wrap in a HybridException.
 * @param expectedPyExcName Python exception class name corresponding
 * to @p Exception class.
 * @param thrownPyExc pybind11-wrapped Python exception to potentially
 * wrap in a HybridException.
 * @param thrownPyExcName Python exception class name of @p thrownPyExc
 * to test against @p expectedPyExcName.
 */
template <class Exception>
void throwHybridExceptionIfMatches(const std::string_view expectedPyExcName,
                                   const py::error_already_set &thrownPyExc,
                                   const std::string_view thrownPyExcName) {
  if (thrownPyExcName == expectedPyExcName) {
    throw HybridException<Exception>{thrownPyExc};
  }
}

/// Name of errors module where exceptions will be registered.
constexpr std::string_view kErrorsModuleName = "openassetio._openassetio.errors";

/**
 * Attempt to convert a given Python exception into one of the C++
 * exceptions in the CppExceptionsAndPyClassNames list (looked up by
 * indices) and throw it.
 *
 * A no-op if no exception matches.
 *
 * @tparam I Indices of exceptions in the CppExceptionsAndPyClassNames
 * list to attempt to convert to.
 * @param thrownPyExc pybind11-wrapped Python exception.
 */
template <std::size_t... I>
void convertPyExceptionAndThrow(const py::error_already_set &thrownPyExc,
                                [[maybe_unused]] std::index_sequence<I...> unused) {
  // We need values from the Python exception object, so must hold the
  // GIL. py::error_already_set::what() does this itself, but we need
  // additional attributes too. Note that acquiring the GIL can cause
  // crashes if the Python interpreter is finalizing (i.e. has been
  // destroyed).
  const py::gil_scoped_acquire gil{};
  // Check module name of Python exception.
  if (thrownPyExc.type().attr("__module__").cast<std::string_view>() != kErrorsModuleName) {
    // Just in case another exception is defined by managers/hosts with
    // the same name in a different namespace.
    return;
  }

  // Extract class name of Python exception.
  const std::string thrownPyExcName{py::str{thrownPyExc.type().attr("__name__")}};

  (throwHybridExceptionIfMatches<CppExceptionsAndPyClassNames::Exceptions<I>>(
       CppExceptionsAndPyClassNames::kClassNames[I], thrownPyExc, thrownPyExcName),
   ...);
}

/**
 * Attempt to convert a given Python exception into a C++ exception
 * in the CppExceptionsAndPyClassNames list, and throw it.
 *
 * A no-op if no exception matches.
 *
 * @param thrownPyExc pybind11-wrapped Python exception.
 */
inline void convertPyExceptionAndThrow(const py::error_already_set &thrownPyExc) {
  convertPyExceptionAndThrow(thrownPyExc, CppExceptionsAndPyClassNames::kIndices);
}

/**
 * Decorate a callable with a try-catch that will catch a
 * pybind11-wrapped Python exception and attempt to convert it to a C++
 * exception before re-throwing.
 *
 * @tparam Fn Type of callable to decorate.
 * @param func Callable instance to decorate.
 * @return Return value of callable, if no exception occurs.
 */
template <class Fn>
auto decorateWithExceptionConverter(Fn &&func) {
  try {
    return func();
  } catch (const py::error_already_set &exc) {
    convertPyExceptionAndThrow(exc);
    // Can't convert exception, so rethrow as-is.
    throw;
  }
}
/**
 * @}
 */
}  // namespace python::exceptions
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
