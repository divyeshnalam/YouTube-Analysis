import streamlit as st
import pandas as pd
from googleapiclient.discovery import build

st.write(""" 

# YouTube Data Collection and Analysis
         """)
st.sidebar.header('User Input Features')

API_KEY = 'AIzaSyAvpnWLKjr0K5ZK68JjMFZQUgKpqUwC8Qk'

results = st.sidebar.slider('Select the number of trending videos to fetch', min_value=10, max_value=200, step=10, value=50)

def get_trending_videos(api_key, max_results=results):
    # build the youtube service
    youtube = build('youtube', 'v3', developerKey=api_key)

    # initialize the list to hold video details
    videos = []

    # fetch the most popular videos
    request = youtube.videos().list(
        part='snippet,contentDetails,statistics',
        chart='mostPopular',
        regionCode='US',  
        maxResults=50
    )

    # paginate through the results if max_results > 50
    while request and len(videos) < max_results:
        response = request.execute()
        for item in response['items']:
            video_details = {
                'video_id': item['id'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'published_at': item['snippet']['publishedAt'],
                'channel_id': item['snippet']['channelId'],
                'channel_title': item['snippet']['channelTitle'],
                'category_id': item['snippet']['categoryId'],
                'tags': item['snippet'].get('tags', []),
                'duration': item['contentDetails']['duration'],
                'definition': item['contentDetails']['definition'],
                'caption': item['contentDetails'].get('caption', 'false'),
                'view_count': item['statistics'].get('viewCount', 0),
                'like_count': item['statistics'].get('likeCount', 0),
                'dislike_count': item['statistics'].get('dislikeCount', 0),
                'favorite_count': item['statistics'].get('favoriteCount', 0),
                'comment_count': item['statistics'].get('commentCount', 0)
            }
            videos.append(video_details)

        # get the next page token
        request = youtube.videos().list_next(request, response)

    return videos[:max_results]
def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

def main():
    trending_videos = get_trending_videos(API_KEY)
    filename = 'trending_videos.csv'
    save_to_csv(trending_videos, filename)
    print(f'Trending videos saved to {filename}')

if __name__ == '__main__':
    main()




st.write(""" 

## Real-Time Data Collected ##
         """)
import pandas as pd
trending_videos = pd.read_csv('trending_videos.csv')
trending_videos



st.write(""" 

## Missing Values and Data Types ##
         """)
# check for missing values
missing_values = trending_videos.isnull().sum()

# display data types
data_types = trending_videos.dtypes

missing_values, data_types




st.write(""" 

## Description Statistics ##
         """)
# fill missing descriptions with "No description"
trending_videos['description'].fillna('No description', inplace=True)

# convert `published_at` to datetime
trending_videos['published_at'] = pd.to_datetime(trending_videos['published_at'])

# convert tags from string representation of list to actual list
trending_videos['tags'] = trending_videos['tags'].apply(lambda x: eval(x) if isinstance(x, str) else x)

descriptive_stats = trending_videos[['view_count', 'like_count', 'dislike_count', 'comment_count']].describe()
descriptive_stats





st.write(""" 

## Statistics of Views, Likes and Comments ##
         """)
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="whitegrid")

selected_distributions = st.sidebar.multiselect(
    'Count Distribution',
    ['View Count', 'Like Count', 'Comment Count'],
    default=['View Count']
)

num_plots = len(selected_distributions)
fig_size = (18, 5) if num_plots > 1 else (8, 5)
fig, axes = plt.subplots(1, num_plots, figsize=fig_size)

if num_plots == 1:
    axes = [axes]

# Plotting the selected distributions
for i, distribution in enumerate(selected_distributions):
    if distribution == 'View Count':
        sns.histplot(trending_videos['view_count'], bins=30, kde=True, ax=axes[i], color='blue')
        axes[i].set_title('View Count Distribution')
        axes[i].set_xlabel('View Count')
        axes[i].set_ylabel('Frequency')
    elif distribution == 'Like Count':
        sns.histplot(trending_videos['like_count'], bins=30, kde=True, ax=axes[i], color='green')
        axes[i].set_title('Like Count Distribution')
        axes[i].set_xlabel('Like Count')
        axes[i].set_ylabel('Frequency')
    elif distribution == 'Comment Count':
        sns.histplot(trending_videos['comment_count'], bins=30, kde=True, ax=axes[i], color='red')
        axes[i].set_title('Comment Count Distribution')
        axes[i].set_xlabel('Comment Count')
        axes[i].set_ylabel('Frequency')

plt.tight_layout()
st.pyplot(fig)




if st.button('Show Correlation Matrix'):
    st.write(""" 

## Correlation of Views, Likes and Comments ##
         """)
# correlation matrix
    correlation_matrix = trending_videos[['view_count', 'like_count', 'comment_count']].corr()

    fig, ax = plt.subplots(figsize=(5, 3))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5, linecolor='black', ax=ax)
    plt.title('Correlation Matrix of Engagement Metrics')
    st.pyplot(fig)






st.write(""" 

## Categories of Videos ##
         """)
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_category_mapping():
    request = youtube.videoCategories().list(
        part='snippet',
        regionCode='US'
    )
    response = request.execute()
    category_mapping = {}
    for item in response['items']:
        category_id = int(item['id'])
        category_name = item['snippet']['title']
        category_mapping[category_id] = category_name
    return category_mapping

# get the category mapping
category_mapping = get_category_mapping()
categories_df = pd.DataFrame(list(category_mapping.items()), columns=['ID', 'Category'])

# Display the DataFrame as a table in Streamlit
st.table(categories_df)






st.write(""" 

## Number of Trending Videos by Category ##
         """)
trending_videos['category_name'] = trending_videos['category_id'].map(category_mapping)

# Bar chart for category counts
fig, ax = plt.subplots(figsize=(12, 8))
sns.countplot(y=trending_videos['category_name'], order=trending_videos['category_name'].value_counts().index, palette='viridis',ax=ax)
plt.title('Number of Trending Videos by Category')
plt.xlabel('Number of Videos')
plt.ylabel('Category')
st.pyplot(fig)






st.write(""" 

## Average Metrics by Category ##
         """)
# average engagement metrics by category
category_engagement = trending_videos.groupby('category_name')[['view_count', 'like_count', 'comment_count']].mean().sort_values(by='view_count', ascending=False)

selected_metrics = st.sidebar.multiselect(
    'Category Metrics',
    ['View Count', 'Like Count', 'Comment Count'],
    default=['View Count']
)

# Determine the number of plots and set figure size accordingly
num_plots = len(selected_metrics)
fig_size = (18, 5) if num_plots > 1 else (8, 5)
fig, axes = plt.subplots(1, num_plots, figsize=fig_size)

# If only one plot is selected, axes won't be an array, so we make it a list
if num_plots == 1:
    axes = [axes]

# Plotting the selected engagement metrics by category
for i, metric in enumerate(selected_metrics):
    if metric == 'View Count':
        sns.barplot(y=category_engagement.index, x=category_engagement['view_count'], ax=axes[i], palette='viridis')
        axes[i].set_title('Average View Count by Category')
        axes[i].set_xlabel('Average View Count')
        axes[i].set_ylabel('Category')
    elif metric == 'Like Count':
        sns.barplot(y=category_engagement.index, x=category_engagement['like_count'], ax=axes[i], palette='viridis')
        axes[i].set_title('Average Like Count by Category')
        axes[i].set_xlabel('Average Like Count')
        axes[i].set_ylabel('')
    elif metric == 'Comment Count':
        sns.barplot(y=category_engagement.index, x=category_engagement['comment_count'], ax=axes[i], palette='viridis')
        axes[i].set_title('Average Comment Count by Category')
        axes[i].set_xlabel('Average Comment Count')
        axes[i].set_ylabel('')

plt.tight_layout()
st.pyplot(fig)






st.write(""" 

## Relation Views and Number of Tags ##
         """)
trending_videos['tag_count'] = trending_videos['tags'].apply(len)
# scatter plot for number of tags vs view count
fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(x='tag_count', y='view_count', data=trending_videos, alpha=0.6, color='orange')
plt.title('Number of Tags vs View Count')
plt.xlabel('Number of Tags')
plt.ylabel('View Count')
st.pyplot(fig)






st.write(""" 

##  Impact of the Time
         """)
# extract hour of publication
trending_videos['publish_hour'] = trending_videos['published_at'].dt.hour

# bar chart for publish hour distribution
fig, ax = plt.subplots(figsize=(12, 6))
sns.countplot(x='publish_hour', data=trending_videos, palette='coolwarm')
plt.title('Distribution of Videos by Publish Hour')
plt.xlabel('Publish Hour')
plt.ylabel('Number of Videos')
st.pyplot(fig)

# scatter plot for publish hour vs view count
fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(x='publish_hour', y='view_count', data=trending_videos, alpha=0.6, color='teal')
plt.title('Publish Hour vs View Count')
plt.xlabel('Publish Hour')
plt.ylabel('View Count')
st.pyplot(fig)


st.write(""" 
## Conclusion
         
1. Encourage viewers to like and comment on videos to boost engagement metrics.
2. Aim to create shorter videos (under 5 minutes) for higher engagement, especially for categories like Music and Entertainment.
3. Schedule video uploads around peak times (2 PM – 8 PM) to maximize initial views and engagement.

        """)
