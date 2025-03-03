import tensorflow as tf
import keras 
import numpy as np

# Загрузка набора данных IMDb
data = keras.datasets.imdb
(train_data, train_labels), (test_data, test_labels) = data.load_data(num_words=10000)

# Ограничение длины отзывов для единообразия
max_length = 250
train_data = pad_sequences(train_data, maxlen=max_length, padding='post', truncating='post')
test_data = pad_sequences(test_data, maxlen=max_length, padding='post', truncating='post')

# Создание модели RNN
model = keras.Sequential([
    keras.layers.Embedding(10000, 32, input_length=max_length),
    keras.layers.LSTM(64, return_sequences=True),
    keras.layers.LSTM(32),
    keras.layers.Dense(1, activation='sigmoid')
])

# Компиляция модели
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Обучение модели
epochs = 5
batch_size = 64
model.fit(train_data, train_labels, epochs=epochs, batch_size=batch_size, validation_data=(test_data, test_labels))

# Оценка модели
loss, accuracy = model.evaluate(test_data, test_labels)
print(f'Точность модели: {accuracy:.4f}')

# Функция предсказания тональности нового текста
def predict_sentiment(text, word_index=data.get_word_index()):
    encoded_text = [word_index.get(word, 2) + 3 for word in text.lower().split()]
    encoded_text = pad_sequences([encoded_text], maxlen=max_length, padding='post', truncating='post')
    prediction = model.predict(encoded_text)[0][0]
    return "Положительный" if prediction > 0.5 else "Негативный"

# Пример предсказания
sample_text = "The movie was fantastic with great acting"
print(f'Отзыв: {sample_text} → Тональность: {predict_sentiment(sample_text)}')
