import os
import sys
import numpy as np
import tensorflow as tf
from tensorflow import keras
import tensorflow_datasets as tfds
import datetime
import utils

os.environ['GOOGLE_APPLICATION_CREDENTIALS']='key.json'
GCP_BUCKET = "modeldogbreeds"
GCP_PROJECT = 'fastai'
job_labels = {'job': 'dog_breeds'}


(ds_train, ds_test), metadata = tfds.load(
    'stanford_dogs',
    split=['train', 'test'],
    shuffle_files=True,
    with_info=True,
    as_supervised=True,
)
 
    
#Import Data
(ds_train, ds_test), metadata = tfds.load(
    'stanford_dogs',
    split=['train', 'test'],
    shuffle_files=True,
    with_info=True,
    as_supervised=True,
)


#The test set is pretty large, we merge some of it into the train set
ds_test = ds_test.shuffle(int(tf.data.experimental.cardinality(ds_test)), reshuffle_each_iteration=False)
ds_train = ds_train.concatenate(ds_test.take(5000))
ds_test = ds_test.skip(5000)


#Set Parameters
NUM_CLASSES = metadata.features['label'].num_classes
IMG_SIZE = 224
BATCH_SIZE = 64
AUTOTUNE = tf.data.experimental.AUTOTUNE

NUM_TRAINING = int(tf.data.experimental.cardinality(ds_train))
NUM_TEST = int(tf.data.experimental.cardinality(ds_test))
 
    
#Preprocess the data
train = (ds_train
         .map(utils.preprocess, num_parallel_calls=AUTOTUNE)
         .map(utils.augment, num_parallel_calls=AUTOTUNE)
         .map(
             lambda image, label: (tf.keras.applications.resnet50.preprocess_input(image), label),
             num_parallel_calls=AUTOTUNE)
         .batch(64, drop_remainder=True)
         .prefetch(AUTOTUNE)
         .repeat()
        )
 
val = (ds_test
       .map(utils.preprocess, num_parallel_calls=AUTOTUNE)
       .cache()
       .batch(64, drop_remainder=True)
      )


#Create first model for finetuning
base_model = tf.keras.applications.ResNet50(weights='imagenet', include_top=False)

for layer in base_model.layers:
    layer.trainable = False


model = keras.Sequential([
        keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3)),
        base_model,
        keras.layers.GlobalAveragePooling2D(),
        keras.layers.Dropout(0.5),
        keras.layers.Flatten(),
        keras.layers.Dense(NUM_CLASSES, activation='softmax')
    ])



MODEL_PATH = 'resnet-dogs'
checkpoint_path = os.path.join('gs://', GCP_BUCKET, MODEL_PATH, 'save_at_{epoch}')
tensorboard_path = os.path.join(
    'gs://', GCP_BUCKET, 'logs', datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
)

callbacks = [
    keras.callbacks.TensorBoard(log_dir=tensorboard_path, histogram_freq=1),
    keras.callbacks.ModelCheckpoint(checkpoint_path),
    keras.callbacks.EarlyStopping(monitor='val_loss', patience=3),
]

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-2),
    loss='categorical_crossentropy',
    metrics=['accuracy'],
)

model.fit(train, 
          epochs=5, 
          callbacks=callbacks, 
          validation_data=val, 
          steps_per_epoch=NUM_TRAINING//BATCH_SIZE,
          validation_steps=NUM_TEST//BATCH_SIZE
         )