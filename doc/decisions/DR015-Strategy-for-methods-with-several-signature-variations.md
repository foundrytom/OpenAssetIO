 DR015 Strategy for methods with methods with several signature
 variations

- **Status:** Proposed
- **Impact:** Low
- **Driver:** @foundrytom
- **Approver:** @feltech @elliotcmorris
- **Outcome:**

## Background

Methods within the OpenAssetIO API may serve the same logical purpose,
but have different signatures or return types. An example of this being
callback or return value variations of the `resolve` call.

Some programming languages allow methods to be declared with the same
name and different signatures (e.g Function Overloading in C++). This is
by no means universal though.

We need to determine a strategy for the declaration of such methods
within the API that provides the best developer experience and coherence
with the rest of the project.

## Relevant data

- OpenAssetIO supports multiple languages (currently C, C++, Python),
  each with their own syntax and language rules. It will certainly be
  extended in the future to as yet unknown languages with similarly
  unknown constraints.

- OpenAssetIO strives for coherence between languages as many developers
  have to work in multi-language code bases. There are certainly
  concessions if this leads to idiosyncrasies, but ideally terminology
  and semantic structure is coherent wherever possible.

The examples illustrated in the options below focus on the case of
providing "host conveniences" for the batch-centric API methods. The
OpenAssetIO batch API uses the following canonical from:

```
void someSingularName(inputVector, ..., successCallback, errorCallback)
```

The rationale for this form is covered
[here](./DR009-Batch-method-result-types.md) and
[here](./DR003-ManagerInterface-method-naming.md). The salient points of
the purposes of this discussion are:

- There is no return value.
- The `successCallback` is called for each element of the input vector
  that is processed without error.
- The `errorCallback` is called for any element of the input vector that
  resulted in a processing error.

Though this is flexible, and supports future design patterns, it can add
significantly to the host implementation boilerplate for simple tasks
such as resolving a single reference where any error is considered
exceptional.

We desire to add several host-facing conveniences that simplify common
API interactions. This immediately precipitates the discussion as to how
these should be integrated into the API.

## Options considered

### Option 1

Use function overloading where possible.

```c++
void resolve(vector<T> inputs, F* successCallback, F* errorCallback)
void resolve(vector<T> inputs, vector<variant<Result, Error>> &out)
void resolve(vector<T> inputs, vector<Result> &out)
void resolve(T input, variant<Result, Error> &out)
void resolve(T input, Result &out)

void entityVersions(vector<T> inputs, F* successCallback, F* errorCallback)
void entityVersions(vector<T> inputs, vector<variant<Result, Error>> &out)
void entityVersions(vector<T> inputs, vector<Result> &out)
void entityVersions(T input, variant<Result, Error> &out)
void entityVersions(T input, Result &out)
```

#### Pros

- Low cognitive overhead to determine which high-level API method is
  being invoked as the name contains no other information.
- Avoids awkward compromises in determining method name mutations.

#### Cons

- Not supported in many languages.
- High cognitive overhead in understanding which variation is being used
  as it relies on parameter naming and/or type visibility.
- Forces out-params in C++ as overloading can't be based on return type.

### Option 2

Describe the variation as a continuation of the method name.

```c++
void resolve(vector<T> inputs, F* successCallback, F* errorCallback)
vector<variant<Result, Error>> resolveToErrorOrResultVector(vector<T> inputs)
vector<Result> resolveToResultVector(vector<T> inputs)
variant<Result, Error> resolveOneToErrorOrResult(T input)
Result resolveOneToResult(T input)

void entityVersions(vector<T> inputs, F* successCallback, F* errorCallback)
vector<variant<Result, Error>> entityVersionsAsErrorOrResultVector(vector<T> inputs)
vector<Result> entityVersionsAsResultVectory(vector<T> inputs)
variant<Result, Error> entityVersionsForOneToErrorOrResult(T input)
Result entityVersionsForOneToResult(T input)
```

#### Pros

- Low cognitive overhead in understanding which variation is in use as
  it is clearly described.

#### Cons

- Higher cognitive overhead to determine which high-level API method is
  being invoked, as the boundary between method name and variation is
  variable.
- The variation description is not consistent as grammar requires some
  variation based on the method name.
- Longer method names could cause line length considerations.

### Option 3

Suffix method names to describe variations

- `S` Singular input/output (non-batch).
- `R` Return data.
- `E` Raise an exception on first error.

```c++
void resolve(vector<T> inputs, F* successCallback, F* errorCallback)
vector<variant<Result, Error>> resolve_R(vector<T> inputs)
vector<Result> resolve_RE(vector<T> inputs, vector<Result> &out)
variant<Result, Error> resolve_SR(T input)
Result resolve_SRE(T input)

void entityVersions(vector<T> inputs, F* successCallback, F* errorCallback)
vector<variant<Result, Error>> entityVersions_R(vector<T> inputs)
vector<Result> entityVersions_RE(vector<T> inputs, vector<Result> &out)
variant<Result, Error> entityVersions_SR(T input)
Result entityVersions_SRE(T input)
```

This version could also introduce a `B` batch prefix, to be added to
existing methods.

> **Note:**
> The use of uppercase letters for the suffix over lowercase is to avoid
> ambiguity when multiple letters are present, as they are more likely
> to be read as a word, and will be properly split by a de-camel-case
> operation.

#### Pros

- Lower cognitive overhead to determine which high-level API method is
  being invoked, as the variation is separated from the method name.
- Shorter method names help with overall line length considerations.

#### Cons

- Higher cognitive overhead to determine which variation is in use as
  it follows an opaque convention.

## Outcome

Option 1 has to be immediately excluded as it does not support C, and so
one of other options would need to be selected there.
