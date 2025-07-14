import pandas as pd
from src.transform.parse_utils import parse_count

def transform_linkedin_data(raw_linkedin_data):
    df = pd.DataFrame(raw_linkedin_data)
    df['platform'] = 'LinkedIn'
    df['replies'] = None
    df['reposts'] = None
    df['likes'] = df['reactions_count'].apply(parse_count)
    df['views'] = None
    df = df.drop(columns=['reactions_count'])
    return df

def transform_twitter_data(raw_twitter_data):
    df = pd.DataFrame(raw_twitter_data)
    df['platform'] = 'Twitter'
    
    interactions_df = df['interactions'].apply(pd.Series)
    df = pd.concat([df.drop(columns=['interactions']), interactions_df], axis=1)

    df['likes'] = df['likes'].apply(parse_count)
    df['replies'] = df['replies'].apply(parse_count)
    df['reposts'] = df['reposts'].apply(parse_count)
    df['views'] = df['views'].apply(parse_count)

    return df

def combine_platform_data(linkedin_df, twitter_df):
    common_columns = ['author_name', 'full_post_content', 'replies', 'reposts', 'likes', 'views', 'platform']
    combined_df = pd.concat([
        linkedin_df[common_columns],
        twitter_df[common_columns]
    ], ignore_index=True)
    return combined_df
