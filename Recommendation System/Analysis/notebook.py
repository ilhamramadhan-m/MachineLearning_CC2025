# -*- coding: utf-8 -*-
"""notebook.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Jar_MLIgZQDKAppQLAXbdGKNN0m7mTac

## **Import Library**
"""

import kagglehub
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

"""## **Data Loading**"""

# Download dataset
path = kagglehub.dataset_download("arashnic/book-recommendation-dataset")
print("Path to dataset files:", path)

# Mengecek nama file
files = os.listdir(path)
print(files)

# Import dataset
df_books = pd.read_csv(f'{path}/Books.csv')
df_ratings = pd.read_csv(f'{path}/Ratings.csv')
df_users = pd.read_csv(f'{path}/Users.csv')

"""## **Exploratory Data Analysis**

### Ratings
"""

# Menampilkan informasi awal dari dataset
df_ratings.info()

# Memvisualisasikan distribusi rating
plt.figure(figsize=(10, 6))
sns.countplot(x='Book-Rating', data=df_ratings)
plt.title('Distribution of Book Ratings')
plt.xlabel('Rating')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.show()

"""**Insight**

Tabel `Ratings` merupakan inti dari sistem rekomendasi karena berisi interaksi antara pengguna dan buku dalam bentuk rating. Tabel ini menjadi dasar dalam pendekatan collaborative filtering untuk mempelajari pola kesukaan pengguna.

Kolom-kolom pada tabel ini mencakup:
- **User-ID** : ID pengguna yang memberikan rating.
- **ISBN** : ISBN buku yang dinilai.
- **Book-Rating** : Nilai rating yang diberikan pengguna terhadap buku (rentang 0–10, di mana 0 berarti tidak memberikan rating eksplisit).

Tabel `Ratings` merupakan tabel interaksi antara pengguna dan buku. Terdiri dari 1.149.780 baris dan 3 kolom, dengan nilai `Book-Rating` berupa skor dari 0 sampai 10. Rating bernilai 0 mengindikasikan bahwa pengguna tidak memberikan rating eksplisit.

Hasil visualisasi menunjukkan bahwa mayoritas pengguna cenderung memberikan rating tinggi, terutama pada nilai rentang 7 hingga 10. Sementara itu, rating rendah (1–3) relatif jarang diberikan. Distribusi ini mengindikasikan adanya bias positif dalam sistem penilaian buku, yang umum ditemukan pada data crowdsourced, di mana pengguna cenderung menilai buku yang mereka sukai.

### Books
"""

# Menampilkan informasi awal dari dataset
df_books.info()

# Mengecek nilai unik pada kolom 'Year-Of-Publication'
print("Unique years of publication :\n", df_books['Year-Of-Publication'].unique())

# Memvisualisasikan top 10 tahun dengan publikasi buku terbanyak
plt.figure(figsize=(12, 6))
sns.countplot(x='Year-Of-Publication', data=df_books, order=df_books['Year-Of-Publication'].value_counts().index[:10])
plt.title('Distribution of Book Publication Years')
plt.xlabel('Year of Publication')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.show()

"""**Insight**

Tabel `Books` berisi metadata terkait buku yang tersedia dalam dataset. Informasi ini berguna untuk membangun model content-based filtering karena dapat digunakan untuk menghitung kesamaan antar buku berdasarkan atribut seperti judul, penulis, dan penerbit.

Kolom-kolom pada tabel ini mencakup:
- **ISBN** : Nomor identifikasi unik untuk setiap buku (sebagai primary key).
- **Book-Title** : Judul buku.
- **Book-Author** : Nama penulis buku.
- **Year-Of-Publication** : Tahun diterbitkannya buku.
- **Publisher** : Nama penerbit buku.
- **Image-URL-S/M/L** : Link URL untuk gambar sampul buku dalam berbagai ukuran.

Tabel `Books` memiliki 271.360 entri data buku dengan 8 kolom. Kolom `ISBN` berperan sebagai identifikasi unik, dan sebagian besar kolom bertipe string. Namun, kolom `Year-Of-Publication` bertipe numerik. Beberapa data pada kolom `Year-Of-Publication` dan `Publisher` mengandung nilai tidak valid atau tidak lengkap.

Dari visualisasi tersebut terlihat bahwa sebagian besar buku dalam dataset diterbitkan antara tahun 1990 hingga awal 2000-an. Puncak publikasi terjadi pada tahun-tahun seperti 1999 dan 2002. Ini menandakan bahwa dataset memiliki fokus pada literatur modern dari dua dekade terakhir abad ke-20, yang cukup representatif untuk sistem rekomendasi buku kontemporer.

### Users
"""

# Menampilkan informasi awal dari dataset
df_users.info()

# Menmvisualisasikan 10 lokasi dengan jumlah pengguna terbanyak
plt.figure(figsize=(12, 6))
sns.countplot(y='Location', data=df_users, order=df_users['Location'].value_counts().index[:10])
plt.title('Top 10 User Locations')
plt.xlabel('Count')
plt.ylabel('Location')
plt.show()

"""**Insight**

Tabel `Users` berisi informasi dasar tentang pengguna yang memberikan rating pada buku. Informasi ini digunakan dalam collaborative filtering, terutama untuk mengelompokkan pengguna berdasarkan kesamaan preferensi.

Kolom-kolom pada tabel ini mencakup:
- **User-ID** : ID unik yang merepresentasikan setiap pengguna.
- **Location** : Informasi lokasi pengguna (biasanya terdiri dari kota, negara bagian, dan negara).
- **Age** : Usia pengguna (nilai ini bersifat opsional dan banyak mengandung missing value).

Tabel `Users` berisi 278.858 data pengguna dengan 3 kolom utama. Terdapat missing value pada kolom `Age`, dan data pada kolom `Location` memiliki format kombinasi `city, state, country`.

Visualisasi distribusi pengguna berdasarkan lokasi geografis menunjukkan bahwa sebagian besar pengguna berasal dari negara-negara dengan penetrasi internet yang tinggi, seperti Amerika Serikat, Kanada, dan Inggris. Hal ini mencerminkan distribusi penggunaan layanan berbasis buku yang cenderung terpusat di negara-negara berbahasa Inggris, yang juga menjadi target pasar utama bagi banyak sistem rekomendasi literatur digital.

## **Data Preparation**

### Data Handling
"""

# Menghapus rating yang bernilai 0
df_ratings = df_ratings[df_ratings['Book-Rating'] != 0]

# Melakukan pembersihan data pada kolom 'Year-Of-Publication'
df_books = df_books[df_books['Year-Of-Publication'].astype(str).str.isnumeric()]
df_books['Year-Of-Publication'] = df_books['Year-Of-Publication'].astype(int)

df_books['Year-Of-Publication'] = pd.to_datetime(
    df_books['Year-Of-Publication'], format='%Y', errors='coerce'
).dt.year

invalid_years = [2026, 2030, 2037, 2038, 2050]
df_books = df_books[~df_books['Year-Of-Publication'].isin(invalid_years)]

# Mengambil hanya bagian negara dari kolom 'Location'
df_users['Location'] = df_users['Location'].str.split(',').str[-1].str.strip()

"""**Insight**

Pada tabel `Ratings`, terdapat nilai rating 0 yang menunjukkan bahwa pengguna tidak memberikan penilaian eksplisit terhadap buku tersebut. Dalam sistem rekomendasi berbasis rating, nilai 0 ini tidak memberikan kontribusi terhadap proses pelatihan model karena tidak merepresentasikan preferensi pengguna.

Kolom `Year-Of-Publication` pada tabel Books memiliki data yang tidak valid, seperti nilai berupa string yang bukan angka dan tahun-tahun di luar rentang yang masuk akal (misalnya 2026, 2030, 2037, dll). Oleh karena itu, dilakukan beberapa langkah pembersihan data, dimulai dengan memfilter nilai tahun agar hanya menyisakan data numerik yang valid, kemudian mengubah formatnya ke datetime, serta menghapus tahun yang berada di luar rentang realistis.

Kolom `Location` pada tabel `Users` berisi informasi lokasi pengguna dalam format `city, state, country`. Untuk menyederhanakan data dan hanya mengambil informasi tingkat negara, dilakukan ekstraksi bagian terakhir setelah koma sebagai representasi negara pengguna. Langkah ini bertujuan untuk memudahkan agregasi dan analisis berdasarkan wilayah pengguna jika dibutuhkan pada tahap selanjutnya, seperti pemfilteran konten berdasarkan lokasi

### Penggabungan Tabel
"""

# Menggabungkan tabel df_ratings dengan df_books
ratings_books = df_ratings.merge(df_books, on='ISBN')

# Menggabungkan tabel dengan df_users
ratings_books_users = ratings_books.merge(df_users.drop("Age", axis=1), on="User-ID")

# Menyusun dataset final
df_all = ratings_books_users[['User-ID', 'ISBN', 'Book-Title', 'Book-Author', 'Publisher', 'Year-Of-Publication', 'Location', 'Book-Rating']]
df_all.head()

"""**Insight**

Tabel `Ratings`, `Books`, dan `Users` bersifat relasional dan dapat di-*join* dengan tabel `Books` dan `Users` melalui kolom `ISBN` dan `User-ID` untuk membentuk dataset yang lebih kaya informasi. Dalam proyek ini, ketiga tabel digunakan untuk membangun dan mengevaluasi sistem rekomendasi yang mampu memberikan saran buku yang relevan bagi pengguna.

### Menangani Missing Value
"""

# Cek missing value
print(f'Missing Value :\n{df_all.isnull().sum()}')

# Menghapus missing value
df_all.dropna(inplace=True)

"""**Insight**

Setelah semua data tergabung, dilakukan pengecekan nilai yang hilang. Dari hasil pengecekan, ditemukan beberapa missing value di kolom `Book-Author`, `Publisher`, dan `Year-Of-Publication`. Oleh karena itu, dilakukan penghapusan seluruh baris yang mengandung nilai kosong dengan kode berikut.

### Menangani Data Duplikat
"""

# Cek duplkasi data
print(f'Duplicate Data :\n{df_all.duplicated().sum()}')

"""**Insight**

Setelah memastikan tidak adanya missing value, langkah berikutnya adalah memeriksa apakah terdapat baris data yang duplikat. Duplikasi dapat terjadi karena kesalahan saat pengumpulan atau penggabungan data dan bisa memengaruhi hasil analisis. Berdasarkan hasil pengecekan duplikasi data, didapatkan bahwa tidak terdapat duplikat data pada dataset sehingga tidak diperlukan penghapusan data dan bisa dilanjutkan ke analisis selanjutnya.

### Penyesuaian Data
"""

df_all.columns = [
    'user_id',
    'isbn',
    'book_title',
    'book_author',
    'publisher',
    'year_of_publication',
    'location',
    'book_rating'
]

df_all

df_all = df_all[:10000]

df_all.sample(10)

df_all.info()

"""**Insight**

Agar nama kolom menjadi lebih seragam dan sesuai dengan konvensi penulisan Python (menggunakan lowercase dan underscore), maka dilakukan pengubahan nama kolom. Pengubahan ini sangat penting untuk meningkatkan keterbacaan dan konsistensi penamaan kolom dalam proses analisis berikutnya. Penamaan yang rapi akan mempermudah dalam pemanggilan kolom menggunakan kode dan meminimalkan kesalahan penulisan variabel.

Dataset yang dimiliki sekarang memiliki jumlah data yang sangat besar dan berpotensi membuat proses analisis dan pelatihan model menjadi lambat. Oleh karena itu, untuk keperluan eksperimen awal dan efisiensi komputasi, dataset ini dipotong menjadi 10.000 baris pertama. Pembatasan ini tidak memengaruhi validitas analisis selama distribusi data yang diambil tetap representatif. Nantinya, jika dibutuhkan, jumlah data dapat ditambah secara bertahap untuk meningkatkan akurasi sistem rekomendasi.

### TF-IDF
"""

# Menggabungkan kolom untuk representasi teks
df_all['content'] = (
    df_all['book_title'].astype(str) + ' ' +
    df_all['book_author'].astype(str)
)

# Melakukan TF-IDF pada kolom 'content'
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df_all['content'])
tfidf_matrix.shape

tfidf_matrix.todense()

# Mengubah matriks TF-IDF menjadi dataframe
pd.DataFrame(
    tfidf_matrix.todense(),
    columns=list(tfidf.vocabulary_.keys()),
    index = df_all.book_title
).sample(5)

"""**Insight**

Langkah pertama adalah membangun fitur teks yang mewakili isi atau deskripsi dari sebuah buku. Fitur ini dibentuk dari gabungan beberapa kolom yaitu `book_title` dan `book_author`. Hasil dari kolom `content` adalah representasi teks dari setiap buku yang akan digunakan untuk mengukur kemiripan satu sama lain.

Setelah kolom `content` dibuat, langkah selanjutnya adalah mengubah teks menjadi representasi numerik menggunakan TF-IDF (Term Frequency-Inverse Document Frequency).

Berikut adalah penjelasan kode transformasi dengan TF-IDF tersebut.

- `TfidfVectorizer` mengubah teks menjadi matriks angka berbasis frekuensi kata yang distandarisasi.

- Parameter `stop_words='english'` berguna untuk mengabaikan kata-kata umum (seperti "and", "the", dll).

- `tfidf_matrix.shape` menunjukkan dimensi dari hasil transformasi. Pada data tersebut didapatkan shape (10000, 14137) yang berarti ada 10.000 buku dan 14.137 kata unik (fitur).

Langkah selanjutnya adalah membentuk tabel yang menunjukkan nilai bobot TF-IDF untuk beberapa judul buku terhadap kata-kata tertentu. Nilai yang lebih tinggi menunjukkan kata tersebut lebih relevan untuk buku tersebut.

### Encoding dan Data Splitting
"""

# Mengambil ID unik pengguna dan buku
user_ids = df_all['user_id'].unique().tolist()
isbn_ids = df_all['isbn'].unique().tolist()

# Encoding ID pengguna dan buku
user_to_user_encoded = {x: i for i, x in enumerate(user_ids)}
isbn_to_isbn_encoded = {x: i for i, x in enumerate(isbn_ids)}
user_encoded_to_user = {i: x for x, i in user_to_user_encoded.items()}
isbn_encoded_to_isbn = {i: x for x, i in isbn_to_isbn_encoded.items()}

# Mapping encoding ke dataset utama
df_all['user'] = df_all['user_id'].map(user_to_user_encoded)
df_all['book'] = df_all['isbn'].map(isbn_to_isbn_encoded)

# Konversi dan normalisasi rating
df_all['book_rating'] = df_all['book_rating'].values.astype(np.float32)

min_rating = df_all['book_rating'].min()
max_rating = df_all['book_rating'].max()

df_all = df_all.sample(frac=1, random_state=42)
x = df_all[['user', 'book']].values
y = df_all['book_rating'].apply(lambda x: (x - min_rating) / (max_rating - min_rating)).values

# Data splitting
train_indices = int(0.8 * df_all.shape[0])
x_train, x_val, y_train, y_val = (
    x[:train_indices],
    x[train_indices:],
    y[:train_indices],
    y[train_indices:]
)

"""**Insight**

Sebelum membangun model Collaborative Learning, langkah-langkah pra-pemrosesan dilakukan untuk mengubah data mentah menjadi format numerik yang dapat digunakan dalam training.

- Langkah pertama adalah mengekstrak semua ID unik dari kolom `user_id` dan `isbn`.

- Setelah itu, ditemukan bahwa ID pengguna dan buku masih berbentuk string. Model deep learning membutuhkan input numerik, sehingga perlu dilakukan proses encoding dengan kode berikut.

- Setelah mendapatkan mapping ID ke angka, kita terapkan hasil encoding tersebut ke dataset utama agar model dapat mengenali setiap entitas pengguna dan buku dalam bentuk numerik.

- Langkah berikutnya adalah memastikan bahwa rating memiliki format numerik yang sesuai dan kemudian melakukan normalisasi ke skala 0–1. Setelah itu dilakukan konversi ke float32 memastikan efisiensi komputasi dan kompatibilitas dengan TensorFlow. Kemudian diambil nilai minimum dan maksimum dari rating, karena kita akan melakukan min-max normalization.

- Langkah terakhir dalam persiapan data adalah membagi dataset menjadi dua bagian yaitu data pelatihan dan data validasi. Pembagian ini penting untuk mengevaluasi performa model terhadap data yang belum pernah dilihat sebelumnya. Dengan membagi data, kita bisa mengetahui apakah model benar-benar belajar dari data atau hanya sekadar menghafal (overfitting).

## **Content-Based Filtering**

### Cosine Similarity
"""

# Menghitung kemiripan antar buku dengan Cosine Similarity
cosine_sim = cosine_similarity(tfidf_matrix)
cosine_sim_df = pd.DataFrame(cosine_sim, index=df_all['book_title'], columns=df_all['book_title'])

print('Shape :\n', cosine_sim_df.shape)

"""**Insight**

Setelah vektorisasi, dilakukan perhitungan kemiripan antar buku dengan Cosine Similarity, yaitu ukuran sudut antar vektor teks. Semakin kecil sudutnya (mendekati 1), semakin mirip dua buku tersebut.


Dari kode yang telah diterapkan dapat dijelaskan bahwa variabel `cosine_sim` adalah matriks 2D (10000 x 10000) yang menunjukkan tingkat kemiripan antar semua kombinasi buku. Nilai dari diagonalnya pasti bernilai 1 karena setiap buku pasti mirip dengan dirinya sendiri. Sedangkan pembuatan `cosine_sim_df` mempermudah pencarian dan visualisasi skor kemiripan berdasarkan judul.

### Recommendation
"""

# Membuat fungsi untuk mendapatkan rekomendasi buku
def recommend_books_by_title(book_title, similarity_data=cosine_sim_df, book_data=df_all[['book_title', 'book_author', 'publisher', 'year_of_publication']], top_n=5):
    if book_title not in similarity_data.columns:
        return f"Book '{book_title}' not found in similarity data."

    similarity_scores = similarity_data[book_title].nlargest(20)
    similarity_scores = similarity_scores.drop(book_title, errors='ignore')

    result = pd.DataFrame({
        'book_title': similarity_scores.index,
        'similarity': similarity_scores.values
    })

    result = result.merge(book_data, on='book_title', how='left')
    result = result.drop_duplicates(subset='book_title')

    return result[['book_title', 'book_author', 'publisher', 'year_of_publication', 'similarity']].head(top_n)

# Mencari rekomendasi buku berdasarkan judul buku tertentu
recommend_books_by_title('Scooby-Doo on Zombie Island (Scooby-Doo)')

"""**Insight**

`recommend_books_by_title()` menggunakan content-based filtering dengan menghitung kemiripan antar buku menggunakan TF-IDF dan cosine similarity. Buku yang direkomendasikan didasarkan pada kesamaan konten (judul, penulis, lokasi) dengan buku input. Berikut adalah contoh pengimplementasiannya mencari rekomendasi berdasarkan suatu buku.

Dari contoh mencari rekomendasi buku berdasarkan buku "Scooby-Doo on Zombie Island", sistem merekomendasikan buku lain seperti "The Racecar Monster" dari seri Scooby-Doo dengan skor kemiripan tertinggi (0.627), serta buku bertema serupa seperti "Zombie!" dan "WINDS OF WAR". Rekomendasi ini membantu pengguna menemukan buku yang mirip secara konten.

## **Collaborative Filtering**

### RecommenderNet
"""

class RecommenderNet(tf.keras.Model):
    def __init__(self, num_users, num_books, embedding_size, **kwargs):
        super(RecommenderNet, self).__init__(**kwargs)
        self.user_embedding = layers.Embedding(num_users, embedding_size, embeddings_initializer='he_normal', embeddings_regularizer=keras.regularizers.l2(1e-6))
        self.user_bias = layers.Embedding(num_users, 1)
        self.book_embedding = layers.Embedding(num_books, embedding_size, embeddings_initializer='he_normal', embeddings_regularizer=keras.regularizers.l2(1e-6))
        self.book_bias = layers.Embedding(num_books, 1)

    def call(self, inputs):
        user_vector = self.user_embedding(inputs[:, 0])
        user_bias = self.user_bias(inputs[:, 0])
        book_vector = self.book_embedding(inputs[:, 1])
        book_bias = self.book_bias(inputs[:, 1])

        dot_user_book = tf.tensordot(user_vector, book_vector, 2)
        x = dot_user_book + user_bias + book_bias

        return tf.nn.sigmoid(x)

num_users = len(user_to_user_encoded)
num_books = len(isbn_to_isbn_encoded)

model = RecommenderNet(num_users, num_books, embedding_size=50)

model.compile(
    loss = tf.keras.losses.BinaryCrossentropy(),
    optimizer = keras.optimizers.Adam(learning_rate=0.001),
    metrics=[tf.keras.metrics.RootMeanSquaredError()]
)

history = model.fit(x=x_train, y=y_train, batch_size=16, epochs=20, validation_data=(x_val, y_val))

def recommend_books_for_user(user_id, top_n=5):
    user_books = df_all[df_all.user_id == user_id]
    books_read = user_books['isbn'].values

    unread_books = df_all[~df_all['isbn'].isin(books_read)]['isbn'].unique()

    unread_books_encoded = [isbn_to_isbn_encoded.get(x) for x in unread_books if x in isbn_to_isbn_encoded]
    user_encoded = user_to_user_encoded.get(user_id)

    user_book_array = np.hstack(([[user_encoded]] * len(unread_books_encoded), np.array(unread_books_encoded).reshape(-1, 1)))

    ratings = model.predict(user_book_array).flatten()
    top_indices = ratings.argsort()[-top_n:][::-1]

    top_isbn = [isbn_encoded_to_isbn[i] for i in np.array(unread_books_encoded)[top_indices]]

    recommended_books = df_all[df_all['isbn'].isin(top_isbn)][['isbn', 'book_title', 'book_author', 'publisher']].drop_duplicates()

    print(f"\nTop {top_n} book recommendations for User ID: {user_id}\n")
    for row in recommended_books.itertuples():
        print(f"{row.book_title} — {row.book_author} ({row.publisher})")

recommend_books_for_user(user_id=1234, top_n=10)

"""**Insight**

Model Collaborative Filtering yang dibangun menggunakan TensorFlow Keras dan terdiri dari arsitektur embedding untuk pengguna dan item (dalam hal ini buku). Tujuan utamanya adalah mempelajari representasi vektor (embedding) dari pengguna dan item, lalu menghitung skor kesukaan melalui operasi dot product. Berikut adalah kode dari permodelan yag digunakan.

Model RecommenderNet yang digunakan terdiri dari beberapa komponen berikut

- `Embedding(num_users, embedding_size)`  
Mengkonversi ID pengguna menjadi representasi vektor berdimensi embedding_size.

- `Embedding(num_items, embedding_size)`  
Mengkonversi ID buku menjadi vektor embedding berdimensi sama.

- `dot_user_item + user_bias + item_bias`  
Skor kesukaan dihitung sebagai hasil dot product vektor pengguna dan buku ditambah bias masing-masing.

- `sigmoid`  
Fungsi aktivasi sigmoid membatasi output ke rentang 0–1.

Setelah model dibangun, langkah selanjutnya adalah melakukan kompilasi dan pelatihan terhadap model dengan data pelatihan. Berikut adalah beberapa parameter yang digunakan dan penjelasan dari parameternya.

- `loss='binary_crossentropy'`  
Digunakan karena rating telah dinormalisasi ke 0–1 (mirip klasifikasi biner).

- `optimizer='adam'`  
Optimizer adaptif yang efisien dan umum digunakan.

- `metrics=['RootMeanSquaredError']`
Digunakan untuk mengukur deviasi prediksi terhadap nilai asli dalam bentuk kuadrat akar.

- `train_data, train_ratings`  
Data input dan target berupa pasangan user-item dan skor kesukaan.

- `batch_size=64`  
Jumlah data yang diproses dalam satu iterasi.

- `epochs=20`  
Jumlah putaran penuh pelatihan terhadap seluruh data.

- `validation_data`  
Data validasi digunakan untuk memantau generalisasi model.

Setelah model selesai dilatih, digunakan fungsi prediksi untuk merekomendasikan buku kepada pengguna berdasarkan skor tertinggi dari buku yang belum pernah dibaca. Dengan melakukan prediksi rekomendasi terhadap user '1234' didapatkan kesimpulan bahwa model ini memberikan rekomendasi berdasarkan kesamaan pola interaksi dengan pengguna lain yang memiliki preferensi serupa, tanpa memerlukan informasi konten eksplisit dari buku atau profil pengguna.

## **Evaluasi**
"""

def evaluate_recommendation(recommendations, test_book_title, df, top_n=5):
    test_author = df[df['book_title'] == test_book_title]['book_author'].values[0]

    recommended_authors = recommendations['book_author'].tolist()
    relevant_recommended = sum([1 for author in recommended_authors if author == test_author])

    total_relevant = len(df[(df['book_author'] == test_author) & (df['book_title'] != test_book_title)])

    precision = relevant_recommended / top_n
    recall = relevant_recommended / total_relevant if total_relevant > 0 else 0

    f1 = 0
    if precision + recall > 0:
        f1 = 2 * (precision * recall) / (precision + recall)

    return precision, recall, f1

test_book_title = 'Scooby-Doo on Zombie Island (Scooby-Doo)'

recs = recommend_books_by_title(test_book_title, top_n=5)

precision, recall, f1 = evaluate_recommendation(recs, test_book_title, df_all)

print(f"Evaluation for '{test_book_title}'")
print(f"Precision@5 : {precision:.4f}")
print(f"Recall@5    : {recall:.4f}")
print(f"F1-Score    : {f1:.4f}")

plt.plot(history.history['root_mean_squared_error'])
plt.plot(history.history['val_root_mean_squared_error'])
plt.title('model_metrics')
plt.ylabel('root_mean_squared_error')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

# Evaluasi model pada data validasi
results = model.evaluate(x_val, y_val, verbose=1)

# Tampilkan hasil RMSE
print(f"RMSE on validation data: {results[1]:.4f}")

"""**Insight**

Berdasarkan evaluasi terhadap model Content-Based Filtering didapatkan evaluasi sebagai berikut.

- **Precision@5 = 0.2000**  
  Dari 5 buku yang direkomendasikan, hanya 1 yang benar-benar relevan. Ini menunjukkan masih banyak rekomendasi yang tidak relevan.

- **Recall@5 = 1.0000**  
  Semua item yang dianggap relevan berhasil ditemukan dalam 5 rekomendasi. Ini menandakan sistem tidak melewatkan item relevan.

- **F1-Score = 0.3333**  
  Nilai F1 yang rendah menunjukkan bahwa meskipun recall tinggi, precision yang rendah menurunkan efektivitas keseluruhan sistem.

Berdasarkan evaluasi yang telah dilakukan, dapat disimpulkan bahwa Content-based model mampu menemukan semua item relevan, tapi perlu peningkatan pada kualitas ranking untuk meminimalkan rekomendasi yang tidak relevan.

Sedangkan untuk evaluasi Collaborative Filtering, berdasarkan grafik evaluasi tersebut dapat diambil beberapa informasi sebagai berikut.
- RMSE Training menurun secara signifikan hingga stabil yang berarti model mampu belajar pola dari data.
- RMSE Testing menurun perlahan dan stabil, tetapi tidak sebaik training yang mengindikasikan adanya *gap* kecil antara performa training dan testing (kemungkinan overfitting ringan).
- Tidak ada kenaikan tajam yang berarti tidak ada gejala underfitting atau overfitting parah.

Dari evaluasi yang telah dilakukan, dapat disimpulkan bahwa model Collaborative Filtering menunjukkan kinerja yang cukup baik dan stabil pada data test. Berdasarkan pengujian menggunakan data validasi, diperoleh nilai RMSE sebesar 0.2615, yang menunjukkan tingkat galat prediksi yang cukup rendah. Untuk meningkatkan performa lebih lanjut, dapat dipertimbangkan penggunaan regularisasi, model matrix factorization lainnya seperti SVD++ atau ALS, maupun pendekatan hybrid dengan content-based filtering.

"""