Changelog
=========

Version 1.3.0 (2024/04/17)
--------------------------

* Added: age.[train|dev|test] tables with speaker information
*   consists of randomly selected 20 emotionally neutral samples per speaker
*   all tables being age/gender balanced


Version 1.2.0 (2023/04/06)
--------------------------

* Added: Tables with vote frequencies
* Added: Gold standard tables including `no_agreement` samples
* Added: `files` table to replace `speaker` table with corrupted indicator column
* Changed: Rename emotion tables to default emotion table names
* Changed: Rename scheme `emotion.value` to `emotion.level`
* Changed: Add index `0` to first winning emotion columns
* Removed: Corrupted file with no audio is removed from index in emotion tables
* Removed: `speaker` table
* Removed: `emotion.agreement` column in `emotion.categories.<modality>.<split>`

Version 1.1.1 (2022/03/29)
--------------------------

* Changed: set usage to ``commercial``

Version 1.1.0 (2022/02/17)
--------------------------

* Added: Unofficial speaker-independent train, dev, test splits for each rating modality and the desired emotion
* Removed: Tables `emotion`, `emotion.face`, `emotion.voice`, `emotion.face`

Version 1.0.5 (2021/09/23)
--------------------------

* Added: author and license information

Version 1.0.4 (2021/02/02)
--------------------------

* Added: conversion to new audb format

Version 1.0.3 (2020/09/14)
--------------------------

+ Fixed: speaker table

Version 1.0.2 (2020/09/07)
--------------------------

+ Fixed: speaker scheme

Version 1.0.1 (2020/09/02)
--------------------------

+ Fixed: maven location


Version 1.0.0 (2020/09/02)
--------------------------

+ Initial release
