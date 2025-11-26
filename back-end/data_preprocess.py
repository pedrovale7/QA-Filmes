import pandas as pd
NOTA_SELECAO = 3.0
df1 = pd.read_csv('datasets/movies.csv')
df2 = pd.read_csv('datasets/ratings.csv')
df3 = pd.read_csv('datasets/tags.csv')

movies = df1.copy()
ratings = df2.copy()
tags_movie = df3.copy()

def pre_process_data():

    metrics = ratings.groupby('movieId')['rating'].agg(['count', 'mean', 'max']).reset_index()
    metrics['mean'] = metrics['mean'].round(2)
    
    good_metrics = metrics[metrics['mean'] > NOTA_SELECAO].sort_values(
    'count', ascending=False).head(1000)   

    bad_metrics = metrics[metrics['mean'] <= NOTA_SELECAO].sort_values(
    'count', ascending=False).head(1000)
    metrics = pd.concat([good_metrics, bad_metrics])

    df = pd.merge(metrics, movies, on='movieId', how='left')
    df.columns = ['Id', 'Quantidade de Avaliações', 'Média das Avaliações', 'Avaliação Máxima', 'Nome do Filme', 'Gêneros']
    
    tags_movie['tag'] = tags_movie['tag'].astype(str)
    tags = tags_movie.groupby('movieId')['tag'].apply(lambda x: ' '.join(x)).reset_index()
    tags.columns = ['Id', 'Tags']
    
    df = pd.merge(df, tags, on='Id', how='left')

    df.to_csv('backend/pre_processed_movies.csv', index=False)
    
pre_process_data()
