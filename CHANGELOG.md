# What's New

Thanks to all our contributors, users, and the many people that make `fuzz-lightyear` possible!
:heart:

If you love `fuzz-lightyear`, please star our project on GitHub to show your support! :star:

<!--
### A.B.C
##### MMM DD, YYYY

#### :mega: Release Highlights
#### :boom: Breaking Changes
#### :tada: New Features
#### :newspaper: News
#### :sparkles: Usability
#### :performing_arts: Performance
#### :bug: Bug Fixes
#### :snake: Miscellaneous

[#xxxx]: https://github.com/Yelp/detect-secrets-server/pull/xxxx
[@xxxx]: https://github.com/xxxx
-->
### 0.0.9
##### August 19, 2020

- Fix tests by adding a trailing comma

### 0.0.8
##### August 17, 2020

#### :tada: New Features

- Rerun all requests in requests sequences with attacker credentials ([#44])

#### :sparkles: Usability

- Add the `--ignore-non-vulnerable` flag to not include any non-vulnerable
operations in request sequences ([#53])

#### :bug: Bug Fixes

#### :snake: Miscellaneous

- Reduce test noise from third-party libraries ([#46], [#49])
- Disable color printing when not printing to terminal ([#51])

[#44]: https://github.com/Yelp/fuzz-lightyear/pull/44
[#46]: https://github.com/Yelp/fuzz-lightyear/pull/46
[#49]: https://github.com/Yelp/fuzz-lightyear/pull/49
[#51]: https://github.com/Yelp/fuzz-lightyear/pull/51
[#53]: https://github.com/Yelp/fuzz-lightyear/pull/53

### 0.0.7
##### :bug: Bug Fixes

- Prevent side-effects upon argument merging in `FuzzingRequest.send` ([#45])

[#45]: https://github.com/Yelp/fuzz-lightyear/pull/45

### 0.0.6
##### :tada: New Features

- Add the `rerun` parameter to post-fuzz hooks ([#41])

##### :snake: Miscellaneous

- Pin a minimum version for the hypothesis dependency ([#42])

[#41]: https://github.com/Yelp/fuzz-lightyear/pull/41
[#42]: https://github.com/Yelp/fuzz-lightyear/pull/42

### 0.0.5
##### :mega: Release Highlights

- Use a smarter request-sequence generation algorithm using an adjacency list ([#37])

#### :tada: New Features

- Support YAML Swagger schema files ([#39])

[#37]: https://github.com/Yelp/fuzz-lightyear/pull/37
[#39]: https://github.com/Yelp/fuzz-lightyear/pull/39

### 0.0.4
##### :tada: New Features

- Add a setup fixture decorator `@fuzz_lightyear.setup` which is run before fuzzing ([#32])
- Add a `--disable-unicode` flag to only fuzz ASCII strings for Swagger strings ([#34])
- Support post-fuzz hooks, decorated by `@fuzz_lightyear.hooks.post_fuzz(**args)`,
which transform fuzzed input ([#36])

##### :sparkles: Usability

- Fuzzer now respects min and max constraints on Swagger numerics ([#31])

##### :bug: Bug Fixes

- Fix dynamic fixture imports for modules which end in `(\.py)+` ([#33])

[#31]: https://github.com/Yelp/fuzz-lightyear/pull/31
[#32]: https://github.com/Yelp/fuzz-lightyear/pull/32
[#33]: https://github.com/Yelp/fuzz-lightyear/pull/33
[#34]: https://github.com/Yelp/fuzz-lightyear/pull/34

### 0.0.3
##### October 18, 2019

#### :mega: Release Highlights

- You can now specify Swagger tags to include in the fuzzing process, to allow developers
  to enable this tool for a subset of endpoints ([#28])

#### :bug: Bug Fixes

- Path array variables print properly ([#27])
- Fuzzed headers no longer try to include non-ascii characters ([#24])
- Fuzzed headers no longer override user-specified headers ([#24])
- Null data is no longer saved in the request's state ([#24])

[#24]: https://github.com/Yelp/fuzz-lightyear/pull/24
[#27]: https://github.com/Yelp/fuzz-lightyear/pull/27
[#28]: https://github.com/Yelp/fuzz-lightyear/pull/28
