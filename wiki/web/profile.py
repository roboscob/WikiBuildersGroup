import sqlite3


class ProfileManager(object):
    """A simple Profile manager that saves profile information in a SQLite database"""
    def __init__(self, database):
        self.connection = sqlite3.connect(database)

    def get_profile(self, username):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM profiles WHERE username=?', (username,))
        result = cursor.fetchone()
        if not result:
            return None
        return Profile(result[0], result[1], result[2])

    def add_profile(self, profile):
        cursor = self.connection.cursor()
        cursor.execute('INSERT INTO profiles values (?, ?, ?)', (profile.username, profile.full_name, profile.bio))
        self.connection.commit()

    def delete_profile(self, username):
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM profiles WHERE username=?', (username,))
        self.connection.commit()


class Profile(object):
    def __init__(self, username, full_name, bio):
        self.username = username
        self.full_name = full_name
        self.bio = bio
