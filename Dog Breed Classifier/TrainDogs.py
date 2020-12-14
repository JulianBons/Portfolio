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

#NUM_TRAINING = tf.data.experimental.cardinality(ds_train)
#NUM_TEST = tf.data.experimental.cardinality(ds_test)



IMG_SIZE = 224
BATCH_SIZE = 64
AUTOTUNE = tf.data.experimental.AUTOTUNE
 
size = (IMG_SIZE, IMG_SIZE)
ds_train = ds_train.map(lambda image, label: (tf.image.resize(image, size), label))
ds_test = ds_test.map(lambda image, label: (tf.image.resize(image, size), label))


def preprocess(image, label):
    label = tf.one_hot(tf.cast(label, tf.int32), NUM_CLASSES)
    label = tf.cast(label, tf.float32)
    image = tf.image.convert_image_dtype(image, tf.float32)
    
    return image, label

def augment(image, label):
    image = tf.image.random_flip_left_right(image)
    image = tf.image.random_brightness(image, max_delta=32. / 255.)
    image = tf.image.random_saturation(image, lower=0.5, upper=1.5)
    image = tf.keras.applications.resnet50.preprocess_input(image)
    
    return image, label
    


train = (ds_train
         .map(preprocess, num_parallel_calls=AUTOTUNE)
         .map(augment, num_parallel_calls=AUTOTUNE)
         .shuffle(100)
         .batch(64, drop_remainder=True)
         .prefetch(AUTOTUNE)
         .repeat()
        )
 
val = (ds_test
       .map(preprocess, num_parallel_calls=AUTOTUNE)
       .cache()
       .batch(64, drop_remainder=True)
      )


base_model = tf.keras.applications.ResNet50(weights='imagenet', include_top=False)

for layer in base_model.layers:
    layer.trainable = False
#for layer in base_model.layers[-10:]:
#    layer.trainable = True

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
          #steps_per_epoch=NUM_TRAINING//BATCH_SIZE,
          #validation_steps=NUM_TEST//BATCH_SIZE
         )