import sys
import pandas as pd
from sqlalchemy import create_engine

def load_data(messages_filepath, categories_filepath):
    """ load messages and category data from raw csv """
    
    # load messages
    messages = pd.read_csv(messages_filepath)
    
    # load categories
    categories = pd.read_csv(categories_filepath) 

    # merge datasets
    df = pd.merge(messages, categories, on="id")
    
    return df
    

def clean_data(df):
    """ clean raw data """
    
    # create a dataframe of the 36 individual category columns
    categories = df.categories.str.split(pat=";", expand=True)

    # select the first row of the categories dataframe
    row = categories.iloc[[0]]

    # use this row to extract a list of new column names for categories.
    category_colnames = row.apply(lambda x: x.str.slice(0,-2))
    category_colnames = category_colnames.to_numpy()
    
    # rename the columns of `categories`
    categories.columns = category_colnames[0]   
    
    # convert category values to number 0 or 1
    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].str.slice(-1) 
        
        # convert column from string to numeric
        categories[column] = pd.to_numeric(categories[column])
        
        # convert numbers >1 to 1 (e.g. for "related")
        categories.loc[categories[column]>1,[column]] = 1
    
            
    # drop the original categories column from `df`   
    df = df.drop(columns = "categories")
    
    # concatenate the original dataframe with the new `categories` dataframe
    df = pd.concat([df, categories], axis = 1)
    
    # drop duplicates
    df = df.drop_duplicates()
    
    return df

def save_data(df, database_filename):
    """ save cleaned data to database """
    
    # create sqllite db
    engine = create_engine(f"sqlite:///{database_filename}")
    
    #save to db
    df.to_sql('Messages', engine, index=False, if_exists="replace")
    

def main():
    """ clean and save raw data """
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()