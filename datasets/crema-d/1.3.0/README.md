This creates new age and gender train, dev and test sets from the database,
for neutral and emotional samples.

The following files are included:
* *create.py* generate a new database with splits
* *publish.py* publish the new database to with audb
* *split_utils.py* utilities to stratify slits
* *trainDevTestSplit.py* helper functions for split_utils
* *util.py* general helper functions
* *requirements.txt* collection of packages that are needed

To generate the new database, you 
* set up a new environment
* install the packages
* call python create.py
* inspect the result folder
* call python publish.py


The names of the new splits are

```
  age.dev:
    type: filewise
    description: Table selected for age and binary gender balance from the emotionally
      neutral samples,  limited to 20 samples per speaker.
    columns:
      speaker: {scheme_id: speaker}
  age.emotional.dev:
    type: filewise
    description: Table selected for age and binary gender balance from all samples,
      limited to 20 samples per speaker.
    columns:
      speaker: {scheme_id: speaker}
  age.emotional.test:
    type: filewise
    description: Table selected for age and binary gender balance from all samples,
      limited to 20 samples per speaker.
    columns:
      speaker: {scheme_id: speaker}
  age.emotional.train:
    type: filewise
    description: Table selected for age and binary gender balance from all samples,
      limited to 20 samples per speaker.
    columns:
      speaker: {scheme_id: speaker}
  age.test:
    type: filewise
    description: Table selected for age and binary gender balance from the emotionally
      neutral samples,  limited to 20 samples per speaker.
    columns:
      speaker: {scheme_id: speaker}
  age.train:
    type: filewise
    description: Table selected for age and binary gender balance from the emotionally
      neutral samples,  limited to 20 samples per speaker.
    columns:
      speaker: {scheme_id: speaker}
```
To access the age and gender of the train split samples with emotional texts you could do
```
df = db["age.emotional.train"].get()
df["gender"] = db["files"]["speaker"].get(map="sex")
df["age"] = db["files"]["speaker"].get(map="age").astype("int")
```

