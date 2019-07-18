'''module docstring'''

import numpy as np
import pandas as pd

class Recommender():
    '''class docstring'''

    def __init__(self, reviews, items):
        '''init Recommender class'''
        self.reviews = reviews
        self.items = items
        self.n_rec = 5
        self.user_item_matrix = None
        self.user_matrix = None
        self.item_matrix = None
        self.user_ids_series = None
        self.item_ids_series = None


    def fit_funk_svd(self, n_components=12, learning_rate=0.0001, n_iter=100):
        '''docstring'''

        user_item_matrix = self._create_user_item_matrix(['user_id', 'wine_id'], 'rating')
        n_users, n_items, n_ratings = self._get_user_item_dimensions()
        # initialize the user and movie matrices with random values
        self.user_matrix = np.random.rand(n_users, n_components)
        self.item_matrix = np.random.rand(n_components, n_items)

        # initialize sse at 0 for first iteration
        sse_accum = 0

        # keep track of iteration and MSE
        print("Optimizaiton Statistics")
        print("Iterations | Mean Squared Error ")

        for iteration in range(n_iter):
            sse_accum = 0

            # For each user-movie pair
            for i in range(n_users):
                for j in range(n_items):
                    if user_item_matrix[i, j]:
                        diff = user_item_matrix[i, j] \
                               - self.user_matrix[i, :].dot(self.item_matrix[:, j])

                        # Keep track of the sum of squared errors for the matrix
                        sse_accum += diff ** 2

                        # update the values in each matrix in the direction of the gradient
                        for k in range(n_components):
                            self.user_matrix[i, k] += learning_rate \
                            * (2*diff*self.item_matrix[k, j])
                            self.item_matrix[k, j] += learning_rate \
                            * (2*diff*self.user_matrix[i, k])

            # print results
            print("%d \t\t %f" % (iteration+1, sse_accum / n_ratings))


    def predict(self, user_id, item_id):
        '''docstring'''

        try:
            user_row = np.where(self.user_ids_series == user_id)[0][0]
            item_col = np.where(self.item_ids_series == item_id)[0][0]

            pred = np.dot(self.user_matrix[user_row, :],
                          self.item_matrix[:, item_col])

            return pred

        except IndexError:
            print("Prediction cannot be made because user_id or item_id does \
            not exist in current database.")


    def find_similar_items(self, input_id, items_df, key):
        '''docstring'''

        content = np.array(items_df.iloc[:, 3:])
        items_dot_prod = content.dot(np.transpose(content))

        # find the row of each movie id
        item_idx = np.where(items_df[key] == input_id)[0][0]

        # find the most similar movie indices
        n_rec = self.n_rec
        similar_idxs = np.argpartition(items_dot_prod[item_idx], -n_rec)[-n_rec:][::-1]

        return similar_idxs


    def find_popular_items(self, ranked_df):
        '''docstring'''

        n_rec = self.n_rec
        top_items = list(ranked_df['name'][:n_rec])

        return top_items


    def make_recs(self, input_id):
        '''docstring'''

        n_rec = self.n_rec
        rec_ids, rec_names = None, None

        if input_id in self.user_ids_series:
            idx = np.where(self.user_ids_series == input_id)[0][0]
            preds = self.user_matrix[idx, :].dot(self.item_matrix)
            indices = preds.argsort()[-n_rec:][::-1]
            rec_ids = self.item_ids_series[indices]
            rec_names = self._get_item_names(self.items, 'sku', rec_ids)

        elif input_id in self.item_ids_series:
            rec_ids = self.find_similar_items(input_id, self.items, 'sku')[:n_rec]
            rec_names = self._get_item_names(rec_ids, self.items, 'sku')

        else:
            ranked_df = self._create_ranked_df()
            rec_names = self.find_popular_items(ranked_df)

        return rec_ids, rec_names


    def _create_user_item_matrix(self, by=None, rating_col=None):
        '''docstring'''

        user_item_df = self.reviews.groupby(by)[rating_col].max().unstack()
        self.user_ids_series = np.array(user_item_df.index)
        self.item_ids_series = np.array(user_item_df.columns)

        return np.array(user_item_df)


    def _get_user_item_dimensions(self):
        '''docstring'''

        n_users = self.user_item_matrix.shape[0]
        n_items = self.user_item_matrix.shape[1]
        n_ratings = np.count_nonzero(~np.isnan(self.user_item_matrix))

        return n_users, n_items, n_ratings


    def _create_ranked_df(self):
        '''docstring'''

        ranked_df = self.items.sort_values(['ratings_ave', 'ratings_count'],
                                           ascending=False)
        ranked_df = ranked_df[ranked_df['ratings_count'] > 3]

        return ranked_df


    @classmethod
    def _get_item_names(cls, input_ids, items_df, key):
        '''docstring'''

        item_names = list(items_df[items_df[key].isin(input_ids)]['name'])

        return item_names


class Data:
    '''class docstring'''

    def __init__(self):
        '''init Data class'''
        self.reviews = None
        self.items = None

    def load_data(self, review_path, item_path):
        '''docstring'''
        self.reviews = pd.read_pickle(review_path)
        self.items = pd.read_pickle(item_path)

    def select_review_cols(self, columns=None):
        '''docstring'''
        self.reviews = self.reviews.loc[:, columns]

    def select_item_cols(self, columns=None):
        '''docstring'''
        self.items = self.items.loc[:, columns]


# set data flow
load_and_process_data = True
run_rec = True


if __name__ == '__main__':

    if load_and_process_data:
        data = Data()
        data.load_data('../../data/processed/reviews.pkl',
                       '../../data/processed/items.pkl')
        data.select_review_cols(['user_id', 'wine_id', 'ratings'])

    if run_rec:
        rec = Recommender(data.reviews, data.items)
        rec.fit_funk_svd(learning_rate=0.01, n_iter=1)
        rec.predict(user_id=8, item_id=2844)
        print(rec.make_recs(8)) # user in the dataset
        print(rec.make_recs(1)) # user not in dataset
        print(rec.make_recs(1853728)) # item in the dataset
        print(rec.make_recs(1)) # item not in dataset
