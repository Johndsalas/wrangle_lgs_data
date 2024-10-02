'''Contains code for wrangling lgs transaction data'''

import pandas as pd
import regex as re

import os

# created files
import cata_lists.accessories as a
import cata_lists.board_games as b
import cata_lists.concessions as c
import cata_lists.paint_supplies as p
import cata_lists.rpg as r
import cata_lists.table_minis as m
import cata_lists.tcg as t
import cata_lists.other as o


def get_prepared_data():
    '''Check local file for prepared data
       if not found prepare data using csv files in local file
       Return prepared data'''

    if os.path.exists('prepared_store_data.csv'):

        df = pd.read_csv('prepared_store_data.csv')

    else:

        df = wrangle_data()

        df.to_csv('prepared_store_data.csv', index_label=False)

    return df

def wrangle_data():
    '''Generates wrangled store data
       Requiers raw_data file containing store data csv's to run'''

    # combine annual csv files into one dataframe
    df_2021 = pd.read_csv('raw_data/2021-2022.csv').sort_values('Date')
    df_2022 = pd.read_csv('raw_data/2022-2023.csv').sort_values('Date')
    df_2023 = pd.read_csv('raw_data/2023-2024.csv').sort_values('Date')


    df = pd.concat([df_2021, df_2022, df_2023]).sort_values('Date')


    # remake df with only relevant columns
    df = df[['Date',
            'Time',
            'Gross Sales',
            'Discounts',
            'Net Sales',
            'Customer ID', 
            'Description', 
            'Discount Name',
            'Event Type']]
    
    # rename columns
    df = df.rename(columns = {'Date' : 'date',
                              'Time' : 'time',
                              'Gross Sales' : 'gross_sales',
                              'Discounts': 'discount_amount',
                              'Net Sales' : 'net_sales',
                              'Customer ID' : 'cust_id', 
                              'Description' : 'cart', 
                              'Discount Name' : 'discount_type',
                              'Event Type' : 'event_type'})


    # impute values for nulls
    df.cust_id = df.cust_id.fillna('unknown')
    df.discount_type = df.discount_type.fillna('no_discount')

    # drop rows with nulls in cart
    df = df.dropna(subset=['cart'])

    # clean and convert US dollor columns from string to float
    df['net_sales'] = df['net_sales'].str.replace('$', '').str.replace(',', '').astype(float)
    df['gross_sales'] = df['gross_sales'].str.replace('$', '').str.replace(',', '').astype(float)
    df['discount_amount'] = df['discount_amount'].str.replace('$', '').str.replace(',', '').astype(float)

    # create datetime column and set it as the index
    df['datetime'] = df.date + ' ' + df.time
    df['datetime'] = pd.to_datetime(df['datetime'])

    df = df.set_index('datetime').sort_index()

    df = df.drop(columns = ['date', 'time'])

    # get time derivative columns
    df['year'] = df.index.year
    df['month'] = df.index.month
    df['day'] = df.index.day
    df['weekday'] = df.index.day_name()  

    # clean values in cart to remove extra punctuation/wordiness and hyphen seperate words in individual item descriptions
    df['cart'] = df['cart'].apply(clean_text_in_cart)


    # Get string of all values in cart seperated by commas

    items = ''

    for value in df['cart']:
        
        items += ',' + value
        
    # get master list by splitting the string on comma and stripping the resulting values
    master_list = list(set([re.sub(r'\d+_x_', '', item) for item in items.split(',') if item != '']))

    master_list.sort()

    # add item count columns
    for item in master_list:
    
        df[item] = df.cart.apply(get_number_of_items, args=(item,))

    # seperate item count columns by category into different dataframes
    df_acc = df[a.accessory_list]
    df_bg = df[b.board_game_list]
    df_con = df[c.concessions_list]
    df_ps = df[p.paint_supplies_list]
    df_rpg = df[r.rpg_list]
    df_tm = df[m.table_minis_list]
    df_tcg = df[t.tcg_list]
    df_other = df[o.other_list]
    df_room = df[o.game_room_list]
    df_master = df[master_list]

    # get total for each and add them to the original dataframe
    df['accessories'] = df_acc.sum(axis=1)
    df['board_games'] = df_bg.sum(axis=1)
    df['concessions'] = df_con.sum(axis=1)
    df['modeling_supplies'] = df_ps.sum(axis=1)
    df['role_playing_games'] = df_rpg.sum(axis=1)
    df['minis_models'] = df_tm.sum(axis=1)
    df['trading_card_games'] = df_tcg.sum(axis=1)
    df['other'] = df_other.sum(axis=1)
    df['game_room_rental'] = df_room.sum(axis=1)
    df['all_items'] = df_master.sum(axis=1)

    return df


def clean_text_in_cart(value):
    '''Takes in a string value of comma seperated transaction items
       returns string lowercased, with clutter text and symbles removed
       spaces in values are replaced with hyphens'''
    
    clean_items = []

    # get list of items splitting on commas
    items = value.split(',')
    
    # for each item
    for item in items:
    
        # remove unnecessary text
        item = (item.lower()
                    .replace('(regular)', '')
                    .replace('  - too much caffeine', '')
                    .replace('  - carbonated beverage', ''))

        # remove symbles except for underscore    
        item = re.sub(r'[^a-z0-9\s_]', '' , item)
    
        # replace word spaces with underscores
        item = item.strip().replace(' ','_')
    
        # ensure only one underscore between words
        item = re.sub('_+', '_', item)

        # add clean item to empty list
        clean_items.append(item)
    
    # join clean listed items
    value = ','.join(clean_items)
    
    return value


def get_number_of_items(value, item):
    '''Takes in a string value of comma seperated transaction items and values and an item name
       Returns the number of matching items indicated by the string'''
    
    # capture number of 'item' purchased if coded for more than one items purchased
    pattern = rf"(((\d+)_x_)?{re.escape(item)}\b)"

    # find all instances of pattern matches in the string
    matches = re.findall(pattern, value)

    # add all pattern matches together 
    # if pattern match does not contain a digit add 1 for that pattern match
    total = sum([int(match[-1]) if match[-1].isdigit() == True else 1 for match in matches ])

    return total 