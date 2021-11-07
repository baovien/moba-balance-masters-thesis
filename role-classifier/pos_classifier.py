from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split

# train a decision tree classifier to clasify dota 2 player positions
def train_pos_classifier(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    clf = DecisionTreeClassifier(random_state=0)
    clf.fit(X_train, y_train)
    return clf, X_test, y_test

if __name__ == '__main__':
    pass

