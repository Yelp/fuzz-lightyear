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
