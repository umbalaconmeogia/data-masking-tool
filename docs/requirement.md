# Data masking tool

## Overview

I want to create a tool that will change data of some fields (columns) in the database, to hide confidential data so that I can use that database for system development and testing.

For example: To change people's name, address, email, birthday.

Please create a plan to create a tool.

## Requirement

* The tool should run by php, python (so we may need separate tool for each programing language).
* We may have some sample data to create data (for example, set of name in English, Japanese).
* We specify table.column of the column to be masked (change data), its data type (not db datatype), and method to create masking data.
  The rule should be put in a file.

## Propose

This is some of my dieas, but may not the best solution.
* We have a folder name *data-sample*, that have
  * japan-people-name.csv, that have 6 column: lastname, lastname_kana, lastname_romaji, firstname, firstname_kana, firstname_romaji. Notice that lastname and firstname in a row is not a pair, they are separated. Just the sample to get data randomly. Or you can separate lastname and firstname in separated files (see vietnamese data below).
    Please examime sqlite data in this folder, you may file something userful https://github.com/umbalaconmeogia/yii2-test-data-japan/tree/master/demo/data
  * vietnamese peope's name (Refer data-sample/vietnamese-people folder for sample data)
* We have folder name script-php, script-python for each prograaming language.
* We have .env file, that describe information to connect to the DB (in a way that 3 programming can understand). We also have the file .env.example)
* Put the rule in a csv file name *masking-rule.csv* (we also have the file *masking-rule.example.csv*).
* Each rule is a row that describe
  * table_name: Objective table name.
  * column_name: Objective column name.
  * data_type:
    * people_firstname
    * people_firstname_kana
    * people_lastname
    * people_lastname_kana
    * people_fullname: Is the join of lastname and first name.
    * people_fullname_kana
    * email
    * tel: tel or fax
    * address (think later)
  * data_rule: How to make masking data. This depends on data_type.
    * For data_type *people_firstname*
      * japanese, vietnamese
    * For data_type *people_firstname_kana*
      * japanese, vietnamese
    * For data_type *people_lastname*
      * japanese, vietnamese
    * For data_type *people_lastname_kana*
      * japanese, vietnamese
    * For data_type *people_fullname*
      * japanese, vietnamese
    * For data_type *people_fullname_kana*
      * japanese, vietnamese
    * For data_type *email*
    * For data_type *tel*
      * replace_all, replace_last_4: replace digits by random digit.
    * For data_type *address*: Not specify now (the source data is too big, I should think more).
* I also want that data_rule may deal with many pattern:
  * Joint of some column, for example
    * email is joining of <firstname_jomaji>.<lastname_jomaji>@example.com (other column and fixed text)
