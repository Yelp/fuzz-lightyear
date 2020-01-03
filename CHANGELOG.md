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

### 0.0.6
##### :tada: New Features

- Add the `rerun` parameter to post-fuzz hooks ([#41])

##### :snake: Miscellaneous

- Pin a minimum version for the hypothesis dependency ([#42])

### 0.0.5
##### :mega: Release Highlights

- Use a smarter request-sequence generation algorithm using an adjacency list ([#37])

#### :tada: New Features

- Support YAML Swagger schema files ([#39])

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
