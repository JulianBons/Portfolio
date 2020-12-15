import tensorflow as tf
NUM_CLASSES = 120
IMG_SIZE = 224

def preprocess(image, label):
    label = tf.one_hot(tf.cast(label, tf.int32), NUM_CLASSES)
    image = tf.image.resize(image, (IMG_SIZE, IMG_SIZE))
    label = tf.cast(label, tf.float32)
    image = tf.image.convert_image_dtype(image, tf.float32)
    
    return image, label


def augment(image, label):
    image = tf.image.random_flip_left_right(image)
    image = tf.image.random_flip_up_down(image)
    image = tf.image.rot90(image, k=1)
    image = tf.image.rot90(image, k=3)
    image = tf.image.random_brightness(image, max_delta=0.5)
    
    return image, label