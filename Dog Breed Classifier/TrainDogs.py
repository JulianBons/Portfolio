import os
import sys
import tensorflow as tf
from tensorflow import keras
import tensorflow_datasets as tfds
import matplotlib.pyplot as plt
import datetime


os.environ['GOOGLE_APPLICATION_CREDENTIALS']='key.json'
#path = os.getcwd()
GCP_BUCKET = "modeldogbreeds"
GCP_PROJECT = 'fastai'


(ds_train, ds_test), metadata = tfds.load(
    'stanford_dogs',
    split=['train', 'test'],
    shuffle_files=True,
    with_info=True,
    as_supervised=True,
)
 
NUM_CLASSES = metadata.features['label'].num_classes

#The test set is pretty large, we merge some of it into the train set
ds_test = ds_test.shuffle(tf.data.experimental.cardinality(ds_test), reshuffle_each_iteration=False)
ds_train = ds_train.concatenate(ds_test.take(4000))
ds_test = ds_test.skip(4000)


IMG_SIZE = 224
BATCH_SIZE = 64
BUFFER_SIZE = 2
 
size = (IMG_SIZE, IMG_SIZE)
ds_train = ds_train.map(lambda image, label: (tf.image.resize(image, size), label))
ds_test = ds_test.map(lambda image, label: (tf.image.resize(image, size), label))
 
def input_preprocess(image, label):
    image = tf.keras.applications.resnet50.preprocess_input(image)
    return image, label

ds_train = ds_train.map(
    input_preprocess, num_parallel_calls=tf.data.experimental.AUTOTUNE
)
 
ds_train = ds_train.batch(batch_size=BATCH_SIZE, drop_remainder=True)
ds_train = ds_train.prefetch(tf.data.experimental.AUTOTUNE)
 
ds_test = ds_test.map(input_preprocess)
ds_test = ds_test.batch(batch_size=BATCH_SIZE, drop_remainder=True)

inputs = tf.keras.layers.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
base_model = tf.keras.applications.ResNet50(
    weights="imagenet", include_top=False, input_tensor=inputs
)
x = tf.keras.layers.GlobalAveragePooling2D()(base_model.output)
x = tf.keras.layers.Dropout(0.5)(x)
outputs = tf.keras.layers.Dense(NUM_CLASSES)(x)
 
model = tf.keras.Model(inputs, outputs)

base_model.trainable = False


MODEL_PATH = "resnet-dogs"
checkpoint_path = os.path.join("gs://", GCP_BUCKET, MODEL_PATH, "save_at_{epoch}")
tensorboard_path = os.path.join(
    "gs://", GCP_BUCKET, "logs", datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
)

callbacks = [
    # TensorBoard will store logs for each epoch and graph performance for us. 
    keras.callbacks.TensorBoard(log_dir=tensorboard_path, histogram_freq=1),
    # ModelCheckpoint will save models after each epoch for retrieval later.
    keras.callbacks.ModelCheckpoint(checkpoint_path),
    # EarlyStopping will terminate training when val_loss ceases to improve. 
    keras.callbacks.EarlyStopping(monitor="val_loss", patience=3),
]

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-2),
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    metrics=["accuracy"],
)

model.fit(
    ds_train, epochs=1, callbacks=callbacks, validation_data=ds_test, verbose=2)