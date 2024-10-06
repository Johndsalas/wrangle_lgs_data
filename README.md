# Wrangle LGS Data

## Purpose:

In this repository I will wrangle, prepare, and document preparation of transaction data from a local game store for use in future projects

## Wrangle Method
* The original CSV's contained annual transaction data for the years 2021, 2022, 2023
* After merging the data in these files there were 19,721 rows each representing one transaction and 51 columns each providing details about those transactions
* Remade the data frame keeping only the 9 columns I was interested in 
* Coumns were then renamed for clarity and ease of use 
    * date
    * time
    * gross_sales
    * discount_amount
    * net_sales
    * cust_id, id number for customer making purchase
    * cart, string containing names of items bought
    * discount_type, type of discount applied to purchase
    * event_type, type of transaction
* Handeled null values
    * 3,445 nulls in cust_id were imputed with 'unknown'
    * 10,236 nulls in discount_type were imputed with 'No Discount'
    * 3 rows were dropped that contained null values in cart and no other useful data
* Converted columns containing dollar ammounts from string to float
* Converted time to datetime and set it as the index
* Added time derivative columns such as year, month and day
* Cleaned strings in cart column and got a master list of all unique items appearing in those strings
* Added a column for each item in master list describing how many of that item was in each transaction
* Added a column for each product category describing the number of products from that category that were in each transaction

Items in master list were manually sorted using the following criteria

|Category|Description|Examples|
|--------|-----------|--------|
|Accessories|Items that enhance game play or are used to store game play items|Binders, Dice, Card Sleeves|
|Board Games|Self contained board games and board game expansions|Terraforming Mars, LOTR Journeys in Middle Earth|
|Concessions|Food and drink items|drinks, candy|
|Minis/Models|Miniature models, customizable "war game" minis, RPG support minis, does not include boardgames that contain minis|Warhammer Minis, D&D Minis|
|Modeling Supplies|Items used to enhance appearance of minis/models|Painting Supplies, Model Bases|
|Role Playing Games|Books and map packs for Role Playing Games|Dungeons and Dragons Books, Pathfinder Books|
|Trading Card Games|Cards for customizable card games|Magic, Pokemon, Yugio|
|Game Room Rental|Items that relate to renting the game room| n/a|
|Other| Items that could not be classified|Custom Amount|
