# Data folder structure
Create the folders `preprocessed` and `raw` shown below if they don't exist.

* `📂examples`:  example matches from the steam api
* `📂preprocessed`: preprocessed training data, ready for training
* `📂raw`: raw datasets which can be downloaded from the gdrive [here](https://drive.google.com/drive/u/0/folders/1YUTOAgKdQJRW_rmaCWi3s4Lys1FirbSl)
* `📜heroes.json`: dota2 hero metainfo

```
 📂data
 ┣ 📂examples
 ┃ ┣ 📜example_match_details.json
 ┃ ┗ 📜example_match_history_seq.json
 ┣ 📂preprocessed
 ┃ ┣ 📜test_5148330922-5148330922.npy
 ┃ ┗ ...
 ┣ 📂raw
 ┃ ┣ 📜dota_collection_5146330922-5165330922.tar.gz
 ┃ ┗ 📜test_5146330922-5148330922.gz
 ┣ 📜README.md
 ┗ 📜heroes.json
 ```

 