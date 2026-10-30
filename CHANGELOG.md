# CHANGELOG

<!-- version list -->

## v1.1.0 (2026-10-30)

### Bug Fixes

- Add plotly as dependency
  ([`f4417e5`](https://github.com/quantumbeam/bborclient/commit/f4417e5959ac987115371fd279671c9b13d072a4))

- Apiアドレスの修正
  ([`2b8921c`](https://github.com/quantumbeam/bborclient/commit/2b8921c43f79af5cd8a618665483f077c56867e0))

- Change the type of references from Link to Link | DBRef of bson. This is because these Models also
  used in the app.
  ([`397eeab`](https://github.com/quantumbeam/bborclient/commit/397eeabb182f0ef523fe8b0910401cad1dda9781))

- Fraction calculation
  ([`39fd947`](https://github.com/quantumbeam/bborclient/commit/39fd9473cdbe24b734f12ba7c17ae99254c4df88))

- Minor improvements
  ([`03aca91`](https://github.com/quantumbeam/bborclient/commit/03aca91eda44dc671e961896f7b6531acdb1bb58))

- Send the password of create_user in the JSON body instead of the query string
  ([`ab18267`](https://github.com/quantumbeam/bborclient/commit/ab182673e927fc4cb0707e77da4106560c7e5900))

- Send the password of create_user in the JSON body instead of the query string
  ([`579bbe0`](https://github.com/quantumbeam/bborclient/commit/579bbe06f48f24aeeb29a56a99456dbb7330bcde))

- Status and exception fields are missing
  ([`2a3594a`](https://github.com/quantumbeam/bborclient/commit/2a3594ab4fa8223377538592eab37ed934c56eee))

- Supports tab separator
  ([`2d862d1`](https://github.com/quantumbeam/bborclient/commit/2d862d1ed2c5b3db147bc729a87449e7555b1bb7))

- The measurement file parser now covers .dat files by treating them as .csv files
  ([`61019c7`](https://github.com/quantumbeam/bborclient/commit/61019c7d9eba83570b9bdb9b5b37593dfd158d71))

- 入力の組み合わせの誤りをKeyErrorではなく検証エラーにし、テストを足す
  ([`7fef311`](https://github.com/quantumbeam/bborclient/commit/7fef311efbbac8aecf67cdaa06b1ccb6a3477cda))

### Build System

- Add dependencies for GSAS-II
  ([`84ca8ec`](https://github.com/quantumbeam/bborclient/commit/84ca8ec2381d5e88ec034e9fc172c319dc9fe848))

- Add pymongo to dependencies for bson.DBRef, but practically not used. Remove pymongo if possible.
  ([`d48a3b3`](https://github.com/quantumbeam/bborclient/commit/d48a3b3ff6cfb08a057d1c6ff9d34e11a2b70a0f))

- Build backendの変更とGSAS-IIインストールの整備
  ([`01f95ef`](https://github.com/quantumbeam/bborclient/commit/01f95efdebe15025bd9feed32066d58325be438b))

- Change pandas from required to optional
  ([`830c9b8`](https://github.com/quantumbeam/bborclient/commit/830c9b83fb7ef43c20d86a155fd61762fcf53fd1))

- Required python version from >=3.9 to >=3.11 for GSAS-II compatibility
  ([`de61392`](https://github.com/quantumbeam/bborclient/commit/de61392634d1af2441548c1e8cbd056f8ed9bddc))

- Uv.lockをpyproject.tomlのGSAS-IIの依存に合わせる
  ([`a36414f`](https://github.com/quantumbeam/bborclient/commit/a36414f5b874720d8af8d74755c95d7ec9062c32))

### Chores

- CLAUDE.mdを削除
  ([`8307776`](https://github.com/quantumbeam/bborclient/commit/8307776a8309e8f5ea1c4d23c71adfdf95eae4aa))

### Continuous Integration

- リリースのworkflowをworkflows/に移して動くようにする
  ([`215319f`](https://github.com/quantumbeam/bborclient/commit/215319fbe966af336f354542586f0677c71a0c1d))

### Documentation

- Pythonバージョンと表記揺れとライセンスを修正
  ([`08f0046`](https://github.com/quantumbeam/bborclient/commit/08f0046073133d8a3daacdad5beb411fd5ddd8c1))

- README updated for finding results
  ([`1676210`](https://github.com/quantumbeam/bborclient/commit/16762103a445ef6b0be0f15e0e03c79e161bc77d))

- ライセンス整備MIT
  ([`a1e40ee`](https://github.com/quantumbeam/bborclient/commit/a1e40ee74439e7d070d8c3530642c74ee6945f35))

### Features

- Add parser for 2ta
  ([`480b888`](https://github.com/quantumbeam/bborclient/commit/480b888f956dd831ef33f4d1e4ae5f4cce526b3c))

- Add the method gpxview.linear_absorption_coefficient
  ([`ded15dd`](https://github.com/quantumbeam/bborclient/commit/ded15dd42a124dd5a480f60bc18a82ff089d1bbe))

- Implement the post finishing task method
  ([`21bd805`](https://github.com/quantumbeam/bborclient/commit/21bd8051e15ef4003f880463ede806dc2457e40a))

- Many improvements and refactors in task models and methods
  ([`75c5827`](https://github.com/quantumbeam/bborclient/commit/75c58277071b0bc5824708c86dca058ea47795e2))

- Support client models of study, trial, and refine for usage from app/data and downloads features.
  ObjectId and DBRefs (Link) are redefied so that they can be used without extra dependencies in the
  user environement and serialized to json from the server environment.
  ([`7d641ce`](https://github.com/quantumbeam/bborclient/commit/7d641ceb2ed4918eb6edececcc57dbb036bc4447))

- Updates in gpxview
  ([`4da17f0`](https://github.com/quantumbeam/bborclient/commit/4da17f0562d85b53edd5955b610d087cd0fcda0c))

- Urlで渡せるようにし、devを削除
  ([`c0cdf8a`](https://github.com/quantumbeam/bborclient/commit/c0cdf8a6fa193465c2cc6b2d829a182286efd805))


## v1.0.0 (2025-11-21)

- Initial Release
