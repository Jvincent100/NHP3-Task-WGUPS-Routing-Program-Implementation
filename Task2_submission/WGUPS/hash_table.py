class HashTableWithChaining:
    def __init__(self, capacity=10):
        self.table = [[] for _ in range(capacity)]

    def _hash(self, key):
        return int(key) % len(self.table)

    # Part A: insert data
    def insert(self, key, value):
        bucket = self._hash(key)
        bucket_list = self.table[bucket]

        # Check if key already exists in the bucket
        # If key exists, update the value
        # If key does not exist, add it to the bucket
        for item in bucket_list:
            if int(item[0]) == key:
                item[1] = value
                return
        bucket_list.append([int(key), value])

    # Search for an item in the table
    # O(n) time complexity
    # Part B: search
    def search(self, key):
        bucket = self._hash(key)
        bucket_row = self.table[bucket]

        # iterate the data in the bucket, return wanted data item
        # checks in O(N) where N is bucket_row length
        for data in bucket_row:
            if data[0] == key:
                return data[1]

        # if key not in table return nothing
        print('Key not found')
        return None

    # O(n) time complexity for deletion
    def delete(self, key):
        bucket = self._hash(key)
        bucket_list = self.table[bucket]

        for item in bucket_list:
            if int(item[0]) == key:
                bucket_list.remove(item)
                return

    def __str__(self):
        return str(self.table)

    # Make the hash table iterable
    def __iter__(self):
        for bucket in self.table:
            for item in bucket:
                yield item